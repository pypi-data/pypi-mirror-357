import os
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest

import testthing


@pytest.fixture
async def machine() -> AsyncGenerator[testthing.VirtualMachine, None]:
    image = os.getenv("TEST_IMAGE")
    if not image:
        raise RuntimeError("TEST_IMAGE environment variable must be set")
    async with testthing.run_vm(image=image) as vm:
        yield vm


async def test_cat_os_release(machine: testthing.VirtualMachine) -> None:
    await machine.execute("cat", "/etc/os-release")
