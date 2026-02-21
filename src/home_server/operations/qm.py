# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""Define operations using qm - QEMU/KVM virtual machine manager."""

import shlex
from collections.abc import Generator
from typing import Any

from pyinfra import host
from pyinfra.api import operation
from pyinfra.api.exceptions import OperationError
from pyinfra.facts.server import Which

from home_server.facts import qm


def kwargs_to_flags(**kwargs: Any) -> str:
    """
    Convert a dict of keyword arguments to a string of unix flags.

    Returns:
        str: joined string of kwargs as flags.

    """
    flags = []
    prefix = "--"
    for key, value in kwargs.items():
        flag_name = f"{prefix}{key}"

        if value is None:
            flags.append(flag_name)
        else:
            flags.append(f"{flag_name}={shlex.quote(str(value))}")

    return " ".join(flags)


@operation()  # type: ignore[untyped-decorator]
def create(vm_id: int, vm_name: str, **kwargs: Any) -> Generator[str]:
    """
    Create a VM.

    Args:
        vm_id (int): ID of the VM
        vm_name (str): Name of the VM
        kwargs (Any): Flags to "qm create"

    Raises:
        OperationError: Raised on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    vms = host.get_fact(qm.List)
    for vm in vms:
        if vm["id"] == vm_id and vm["name"] == vm_name:
            host.noop(f"VM {vm_name} with ID {vm_id} already exists")
            return
        if vm["name"] == vm_name or vm["id"] == vm_id:
            # if a VM exists that matches one field only, raise an error
            err_msg = f"VM {vm_name} already exists with ID {vm['id']}"
            raise OperationError(err_msg)
    flags = {kwargs_to_flags(**kwargs)}
    yield f"qm create {vm_id} --name {shlex.quote(vm_name)} {flags}"
