#!/usr/bin/python

"""test.thing - A simple modern VM runner.

A simple VM runner script exposing an API useful for use as a pytest fixture.
Can also be used to run a VM and login via the console.

Each VM is allocated an identifier: 'tt.0', 'tt.1', etc.

For each VM, an ephemeral ssh key is created and used to connect to the VM via
vsock with systemd-ssh-proxy, which works even if the guest doesn't have
networking configured.  The ephemeral key means that access is limited to the
current user (since vsock connections are otherwise available to all users on
the host system).  The guest needs to have systemd 256 for this to work.

An ssh control socket is created for sending commands and can also be used
externally, avoiding the need to authenticate.  A suggested ssh config:

```
Host tt.*
        ControlPath ${XDG_RUNTIME_DIR}/test.thing/%h/ssh
```

And then you can say `ssh tt.0` or `scp file tt.0:/tmp`.
"""

import argparse
import asyncio
import contextlib
import ctypes
import json
import os
import shlex
import shutil
import signal
import socket
import sys
import traceback
import weakref
from collections.abc import AsyncGenerator, Callable
from pathlib import Path


# This is basically tempfile.TemporaryDirectory but sequentially-allocated.
# We do that so we can easily interact with the VMs from outside (with ssh).
class _IpcDir:
    finalizer: Callable[[], None] | None = None

    def __enter__(self) -> Path:
        tt_dir = Path(os.environ["XDG_RUNTIME_DIR"]) / "test.thing"
        for n in range(10000):
            tmpdir = tt_dir / f"tt.{n}"

            try:
                tmpdir.mkdir(exist_ok=False, parents=True, mode=0o700)
            except FileExistsError:
                continue

            self.finalizer = weakref.finalize(self, shutil.rmtree, tmpdir)
            return tmpdir

        raise FileExistsError

    def __exit__(self, *args: object) -> None:
        del args
        if self.finalizer:
            self.finalizer()


def _vsock_listen(family: socket.SocketKind) -> tuple[socket.socket, int]:
    """Bind a vsock to a free port number and start listening on it.

    Returns the socket and the chosen port number.
    """
    sock = socket.socket(socket.AF_VSOCK, family)
    sock.bind((-1, -1))
    sock.listen()
    _, port = sock.getsockname()
    return (sock, port)


async def _wait_stdin(msg: str) -> None:
    r"""Wait until stdin sees \n or EOF.

    This prints the given message to stdout without adding an extra newline.

    The input is consumed (and discarded) up to the \n and maybe more...
    """
    done = asyncio.Event()

    def stdin_ready() -> None:
        data = os.read(0, 4096)
        if not data or b"\n" in data:
            done.set()

    loop = asyncio.get_running_loop()
    loop.add_reader(0, stdin_ready)
    sys.stdout.write(msg)
    sys.stdout.flush()
    try:
        await done.wait()
    finally:
        loop.remove_reader(0)


async def _spawn(
    cmd: str,
    *args: tuple[str | Path, ...],
    stdin: int | None = None,
    stdout: int | None = None,
    verbose: bool = True,
) -> asyncio.subprocess.Process:
    """Spawn a process.

    This has a couple of extra niceties: the args list is flattened, Path is
    converted to str, the spawned process is logged to stderr for debugging,
    and we call PR_SET_PDEATHSIG with SIGTERM after forking to make sure the
    process exits with us.

    The flattening allows grouping logically-connected arguments together,
    producing nicer verbose output, allowing for adding groups of arguments
    from helper functions or comprehensions, and works nicely with code
    formatters:

    For example:

    private = Path(...)
    options = { ... }

    ssh = await _spawn(
        "ssh",
        ("-i", private),
        *(("-o", f"{k} {v}") for k, v in options.items()),
        ("-l", "root", "x"),
        ...
    )
    """
    # This might be complicated: do it before the fork
    prctl = ctypes.CDLL(None, use_errno=True).prctl

    def pr_set_pdeathsig() -> None:
        PR_SET_PDEATHSIG = 1  # noqa: N806
        if prctl(PR_SET_PDEATHSIG, signal.SIGTERM):
            os._exit(1)  # should never happen

    if verbose:
        argv = [cmd, *(shlex.join(map(str, chunk)) for chunk in args)]
        print("+", " \\\n      ".join(argv))

    argv = [cmd, *(str(arg) for chunk in args for arg in chunk)]
    return await asyncio.subprocess.create_subprocess_exec(
        *argv, stdin=stdin, stdout=stdout, preexec_fn=pr_set_pdeathsig
    )


async def _ssh_keygen(ipc: Path) -> tuple[Path, str]:
    """Create a ssh key in the given directory.

    Returns the path to the private key and the public key as a string.
    """
    private_key = ipc / "id"

    keygen = await _spawn(
        "ssh-keygen",
        ("-q",),  # quiet
        ("-t", "ed25519"),
        ("-N", ""),  # no passphrase
        ("-C", ""),  # no comment
        ("-f", f"{private_key}"),
        stdin=asyncio.subprocess.DEVNULL,
    )
    await keygen.wait()

    return private_key, (ipc / "id.pub").read_text().strip()


async def _notify_server(
    listener: socket.socket, callback: Callable[[str, str], None]
) -> None:
    """Listen on the socket for incoming sd-notify connections.

    `callback` is called with each notification.

    The socket is consumed and will be closed when the server exits (which
    happens via cancelling its task).
    """
    loop = asyncio.get_running_loop()

    async def handle_connection(conn: socket.socket) -> None:
        try:
            while data := await loop.sock_recv(conn, 65536):
                for line in data.decode().splitlines():
                    k, _, v = line.strip().partition("=")
                    callback(k, v)
        finally:
            conn.close()

    # AbstractEventLoop.sock_accept() expects a non-blocking socket
    listener.setblocking(False)  # noqa: FBT003

    try:
        while True:
            conn, _ = await loop.sock_accept(listener)
            asyncio.create_task(handle_connection(conn))  # noqa: RUF006
    finally:
        # If we have a listener but don't accept the connections then the
        # guest can deadlock.  Make sure we close it when we exit.
        listener.close()


async def _run_qemu(
    *,
    attach_console: bool,
    image: Path | str,
    ipc: Path,
    port: int,
    public: str,
    snapshot: bool,
) -> asyncio.subprocess.Process:
    # Console setup:
    #
    #  - attach_console = 0 means nothing goes on stdio
    #  - attach_console = 1 means that a getty starts on stdio
    #  - attach_console = 2 means that console= goes also to stdio
    #
    # In the cases that the console isn't directed to stdio (ie: 0, 1) then we
    # write it to a log file instead.  Unfortunately, we also get a getty in
    # our log file: https://github.com/systemd/systemd/issues/37928
    #
    # We also get our screen cleared unnecessarily in '-a' mode:
    # https://github.com/tianocore/edk2/issues/11218
    #
    # We always use hvc0 for the console=.  We use it also for the getty in
    # mode 2.  In mode 1 we create a separate hvc1 and use that.

    creds = {
        "vmm.notify_socket": f"vsock:2:{port}",
        "ssh.ephemeral-authorized_keys-all": public,
    }

    console = [
        ("-device", "virtio-serial"),
        (
            "-smbios",
            "type=11,value=io.systemd.boot.kernel-cmdline-extra=console=hvc0",
        ),
    ]

    if attach_console < 2:
        console.extend(
            [
                ("-chardev", f"file,path={ipc}/console,id=console-log"),
                ("-device", "virtconsole,chardev=console-log"),
            ]
        )

    if attach_console > 0:
        console.extend(
            [
                ("-chardev", "stdio,mux=on,signal=off,id=console-stdio"),
                ("-mon", "chardev=console-stdio,mode=readline"),
            ]
        )

    if attach_console == 1:
        console.extend(
            [
                ("-device", "virtconsole,chardev=console-stdio"),
            ]
        )
        creds["getty.ttys.serial"] = "hvc1\n"

    if attach_console == 2:
        console.extend(
            [
                ("-device", "virtconsole,chardev=console-stdio"),
            ]
        )

    drive = f"file={image},format=qcow2,if=virtio,media=disk"
    if snapshot:
        # TODO: the image can still be written even with snapshot=true, using
        # an explicit commit.  We need to figure out a way to prevent that from
        # happening...
        drive = drive + ",snapshot=on"

    # we don't have a good way to dynamically allocate guest-cid so we
    # assign it to the same numeric value as the port number the kernel
    # gave us when we created our notify-socket listener (which is unique)
    guest_cid = port

    args = [
        ("-nodefaults",),
        ("-bios", "/usr/share/edk2/ovmf/OVMF_CODE.fd"),
        ("-smp", "4"),
        ("-m", "4G"),
        ("-display", "none"),
        ("-qmp", f"unix:{ipc}/qmp,server,wait=off"),
        # Console stuff...
        *console,
        ("-device", f"vhost-vsock-pci,id=vhost-vsock-pci0,guest-cid={guest_cid}"),
        ("-drive", drive),
        # Credentials
        *(
            ("-smbios", f"type=11,value=io.systemd.credential:{k}={v}")
            for k, v in creds.items()
        ),
    ]

    return await _spawn("qemu-kvm", *args)


async def _wait_qemu(qemu: asyncio.subprocess.Process) -> None:
    try:
        await qemu.wait()
        raise QemuExited
    except asyncio.CancelledError:
        qemu.terminate()
        await asyncio.shield(qemu.wait())


async def _qmp_command(ipc: Path, command: str) -> object:
    reader, writer = await asyncio.open_unix_connection(ipc / "qmp")

    async def execute(command: str) -> object:
        writer.write((json.dumps({"execute": command}) + "\n").encode())
        await writer.drain()
        while True:
            response = json.loads(await reader.readline())
            if "event" in response:
                continue
            if "return" in response:
                return response["return"]
            raise RuntimeError(f"Got error response from qmp: {response!r}")

    # Trivial handshake (ignore them, send nothing)
    _ = json.loads(await reader.readline())
    await execute("qmp_capabilities")

    response = await execute(command)

    writer.close()
    await writer.wait_closed()

    return response


async def _qmp_quit(qmp: Path, *, hard: bool) -> None:
    await _qmp_command(qmp, "quit" if hard else "system_powerdown")


async def _run_ssh_control(
    *, ipc: Path, private: Path, port: int
) -> asyncio.subprocess.Process:
    options = {
        # Fake that we know the host key
        "KnownHostsCommand": "/bin/echo %H %t %K",
        # Use systemd-ssh-proxy to connect via vsock
        "ProxyCommand": f"/usr/lib/systemd/systemd-ssh-proxy vsock/{port} 22",
        "ProxyUseFdpass": "yes",
        # Try to prevent interactive prompting and/or updating known_hosts files
        "PasswordAuthentication": "no",
        "StrictHostKeyChecking": "yes",
    }

    ssh = await _spawn(
        "ssh",
        ("-F", "none"),  # don't use the user's config
        ("-N", "-n"),  # no command, stdin disconnected
        ("-M", "-S", ipc / "ssh"),  # listen on the control socket
        ("-i", private),
        *(("-o", f"{k} {v}") for k, v in options.items()),
        ("-l", "root", ipc.name),  # the name is ignored but displayed in messages
        stdin=asyncio.subprocess.DEVNULL,
        stdout=asyncio.subprocess.PIPE,
    )
    # ssh sends EOF after the connection succeeds
    assert ssh.stdout
    await ssh.stdout.read()

    return ssh


async def _ssh_cmd(ipc: Path, *args: tuple[str | Path, ...]) -> None:
    ssh = await _spawn("ssh", ("-F", "none"), ("-S", ipc / "ssh", ipc.name), *args)
    await ssh.wait()


class VirtualMachine:
    """A handle to a running virtual machine.

    This can be used to perform operations on that machine.
    """

    def __init__(self, ipc: Path) -> None:
        """Don't construct VirtualMachine yourself.  Use vm_run()."""
        self.ipc = ipc

    def get_id(self) -> str:
        """Get the machine identifier like `tt.0`, `tt.1`, etc."""
        return self.ipc.name

    async def forward_port(self, spec: str) -> None:
        """Set up a port forward.

        The `spec` is the format used by `ssh -L`, and looks something like
        `2222:127.0.0.1:22`.
        """
        return await _ssh_cmd(self.ipc, ("-O", "forward"), ("-L", spec))

    async def cancel_port(self, spec: str) -> None:
        """Cancel a previous forward."""
        return await _ssh_cmd(self.ipc, ("-O", "cancel"), ("-L", spec))

    async def execute(self, *args: str | Path) -> None:
        """Execute a command on the guest."""
        return await _ssh_cmd(self.ipc, ("--", shlex.join(map(str, args))))

    async def qmp(self, command: str) -> object:
        """Send a QMP command to the hypervisor.

        This can be used for things like modifying the hardware configuration.
        Don't power it off this way: the correct way to stop the VM is to exit
        the context manager.
        """
        return await _qmp_command(self.ipc, command)


class QemuExited(Exception):
    """An exception thrown when qemu exits unexpectedly.

    You can request that this be suppressed by passing shutdown_ok=True to vm_run().
    """


@contextlib.asynccontextmanager
async def run_vm(
    image: Path | str,
    *,
    sit: bool = False,
    attach_console: bool = False,
    shutdown: bool = True,
    shutdown_ok: bool = False,
    snapshot: bool = True,
    status_messages: bool = False,
) -> AsyncGenerator[VirtualMachine]:
    """Run a VM, returning a handle that can be used to perform operations on it.

    This is meant to be used as an async context manager like so:

    image = Path("...")
    async with run_vm(image) as vm:
        await vm.execute("cat", "/usr/lib/os-release")

    The user of the context manager runs in context of an asyncio.TaskGroup and
    will be cancelled if anything unexpected happens (ssh connection lost, VM
    exiting, etc).

    When the context manager is exited the machine is taken down.

    When the machine is running it is also possible to access it from outside.
    See the documentation for the module.

    The kwargs allow customizing the behaviour:
      - attach_console: if qemu should connect the console to stdio
      - sit: if we should "sit" when an exception occurs: print the exception
        and wait for input (to allow inspecting the running VM)
      - shutdown: if the machine should be shut down on exit from the context
        manager (otherwise: wait)
      - shutdown_ok: if other shutdowns/exits are expected (ie: due to user
        interaction)
      - snapshot: if the 'snapshot' option is used on the disk (changes are
        transient)
      - status_messages: if we should do output of extra messages
    """
    async with contextlib.AsyncExitStack() as exit_stack, asyncio.TaskGroup() as tg:
        # We create a temporary directory for various sockets, ssh keys, etc.
        ipc = exit_stack.enter_context(_IpcDir())

        if shutdown_ok:
            exit_stack.enter_context(contextlib.suppress(QemuExited))

        private, public = await _ssh_keygen(ipc)

        ssh_access = asyncio.Event()
        notify_listener, port = _vsock_listen(socket.SOCK_SEQPACKET)

        def notify(key: str, value: str) -> None:
            if status_messages:
                print(f"notify: {key}={value}")
            if (key, value) == ("X_SYSTEMD_UNIT_ACTIVE", "ssh-access.target"):
                ssh_access.set()

        notify_task = tg.create_task(_notify_server(notify_listener, notify))

        qemu = await _run_qemu(
            ipc=ipc,
            attach_console=attach_console,
            image=image,
            port=port,
            public=public,
            snapshot=snapshot,
        )

        qemu_exit = tg.create_task(_wait_qemu(qemu))

        await ssh_access.wait()
        ssh = await _run_ssh_control(ipc=ipc, private=private, port=port)

        vm = VirtualMachine(ipc)

        try:
            yield vm
        except Exception as exc:
            if sit:
                print("🤦")
                traceback.print_exception(
                    exc.__class__, exc, exc.__traceback__, file=sys.stderr
                )
                # <pitti> lis: the ages old design question: does the button
                # show the current state or the future one when you press it :)
                # <lis> pitti: that's exactly my question.  by taking the one
                # with both then i don't have to choose! :D
                # <lis> although to be honest, i find your argument convincing.
                # i'll put the ⏸️ back
                # <pitti> lis: it was more of a joke -- I actually agree that a
                # play/pause button is nicer
                # <lis> too late lol
                await _wait_stdin("⏸️ ")
            raise

        if shutdown:
            exit_stack.enter_context(contextlib.suppress(QemuExited))
            ssh.terminate()
            # If we're in snapshot mode then we don't have to do a clean shutdown
            await _qmp_quit(ipc, hard=snapshot)

        await qemu_exit

        notify_task.cancel()


async def _async_main() -> None:
    parser = argparse.ArgumentParser(
        description="test.thing - a simple modern VM runner"
    )
    parser.add_argument(
        "--maintain", "-m", action="store_true", help="Changes are permanent"
    )
    parser.add_argument(
        "--attach", "-a", action="count", help="Attach to the VM console", default=0
    )
    parser.add_argument("--sit", "-s", action="store_true", help="Pause on exceptions")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Print verbose output"
    )
    parser.add_argument("image", type=Path, help="The path to a qcow2 VM image to run")
    args = parser.parse_args()

    async with run_vm(
        args.image,
        shutdown=not args.attach,
        shutdown_ok=True,
        attach_console=args.attach,
        status_messages=args.verbose,
        snapshot=not args.maintain,
        sit=args.sit,
    ) as vm:
        if not args.attach:
            await _wait_stdin(f"\nVM running: {vm.get_id()}\n\nEnter or EOF to exit.\n")

def _main() -> None:
    asyncio.run(_async_main())


if __name__ == "__main__":
    _main()
