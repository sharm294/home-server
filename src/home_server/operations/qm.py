# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

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


@operation()  # type: ignore[untyped-decorator]
def set(vm_id: int, **config: Any) -> Generator[str]:  # noqa: A001
    """
    Configure a VM by setting one or more configuration options.

    This operation is idempotent: it only executes if the current
    configuration differs from the desired configuration.

    Args:
        vm_id (int): ID of the VM to configure
        config (Any): Configuration options to set
            (e.g., memory=2048, cores=4, agent="enabled")

    Raises:
        OperationError: Raised if VM doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # Get current VM configuration
    current_config = host.get_fact(qm.VmConfig, vm_id=vm_id)

    # Determine which settings need to be changed
    changes = {}
    for key, desired_value in config.items():
        current_value = current_config.get(key)
        # Convert both to strings for comparison (qm config returns strings)
        if str(current_value) != str(desired_value):
            changes[key] = desired_value

    if not changes:
        host.noop(f"VM {vm_id} already has desired configuration")
        return

    # Build qm set command with only changed settings
    flags = kwargs_to_flags(**changes)
    yield f"qm set {vm_id} {flags}"


@operation()  # type: ignore[untyped-decorator]
def start(vm_id: int) -> Generator[str]:
    """
    Start a VM.

    This operation is idempotent: if the VM is already running,
    it will noop.

    Args:
        vm_id (int): ID of the VM to start

    Raises:
        OperationError: Raised if VM doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # Check current status
    status = host.get_fact(qm.VmStatus, vm_id=vm_id)
    if status == "running":
        host.noop(f"VM {vm_id} is already running")
        return

    yield f"qm start {vm_id}"


@operation()  # type: ignore[untyped-decorator]
def resize(vm_id: int, disk_id: str, size: str) -> Generator[str]:
    """
    Resize a VM's disk.

    This operation is idempotent: if the disk is already at or larger
    than the requested size, it will noop.

    Args:
        vm_id (int): ID of the VM
        disk_id (str): Disk identifier (e.g., 'scsi0')
        size (str): New size (e.g., '50G', '1T')

    Raises:
        OperationError: Raised if VM or disk doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # Get current disk size
    current_size = host.get_fact(qm.DiskSize, vm_id=vm_id, disk_id=disk_id)
    if current_size is None:
        err_msg = f"Disk {disk_id} on VM {vm_id} not found"
        raise OperationError(err_msg)

    # Parse desired size to GiB
    multiplier = 1.0
    size_normalized = size.upper()
    if size_normalized.endswith("G"):
        size_normalized = size_normalized[:-1]
        multiplier = 1.0
    elif size_normalized.endswith("T"):
        size_normalized = size_normalized[:-1]
        multiplier = 1024.0
    elif size_normalized.endswith("M"):
        size_normalized = size_normalized[:-1]
        multiplier = 1.0 / 1024

    try:
        desired_size = float(size_normalized) * multiplier
    except ValueError as err:
        err_msg = f"Invalid size format: {size}"
        raise OperationError(err_msg) from err

    if current_size >= desired_size:
        host.noop(
            f"Disk {disk_id} on VM {vm_id} is already {current_size}GiB "
            f"(desired: {desired_size}GiB)"
        )
        return

    yield f"qm resize {vm_id} {disk_id} {size}"


@operation()  # type: ignore[untyped-decorator]
def importdisk(
    vm_id: int,
    source_image: str,
    storage: str,
    disk_format: str = "qcow2",
) -> Generator[str]:
    """
    Import a disk image into a VM.

    This operation is idempotent: if a disk with the expected size
    already exists, it will noop.

    Args:
        vm_id (int): ID of the VM
        source_image (str): Path to the source disk image
        storage (str): Target storage (e.g., 'local-lvm')
        disk_format (str): Disk format (default: 'qcow2')

    Raises:
        OperationError: Raised if VM doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # Check current config for existing scsi0 disk
    # If scsi0 already exists with a disk, assume already imported
    current_config = host.get_fact(qm.VmConfig, vm_id=vm_id)
    if current_config.get("scsi0"):
        host.noop(f"VM {vm_id} already has a disk (scsi0) configured")
        return

    yield (
        f"qm importdisk {vm_id} {shlex.quote(source_image)} {storage} "
        f"--format {disk_format}"
    )


@operation()  # type: ignore[untyped-decorator]
def template(vm_id: int) -> Generator[str]:
    """
    Convert a VM to a template.

    This operation is idempotent: if the VM is already a template,
    it will noop.

    Args:
        vm_id (int): ID of the VM to convert to a template

    Raises:
        OperationError: Raised if VM doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # Check if already a template
    # Templates have "template: 1" in their config
    current_config = host.get_fact(qm.VmConfig, vm_id=vm_id)
    if current_config.get("template") == "1":
        host.noop(f"VM {vm_id} is already a template")
        return

    yield f"qm template {vm_id}"


@operation()  # type: ignore[untyped-decorator]
def clone(
    source_vm_id: int,
    target_vm_id: int,
    target_name: str,
    full: int = 1,
) -> Generator[str]:
    """
    Clone a VM from a template or another VM.

    This operation is idempotent: if the target VM already exists,
    it will noop.

    Args:
        source_vm_id (int): ID of the source VM/template
        target_vm_id (int): ID for the new cloned VM
        target_name (str): Name for the new cloned VM
        full (int): Whether to do a full clone (1=true, 0=false,
                    default: 1)

    Raises:
        OperationError: Raised if source VM doesn't exist,
                        target already exists, or on other errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that source VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=source_vm_id):
        err_msg = f"Source VM {source_vm_id} does not exist"
        raise OperationError(err_msg)

    # Check if target already exists
    if host.get_fact(qm.VmIdExists, vm_id=target_vm_id):
        host.noop(f"Target VM {target_vm_id} already exists")
        return

    yield (
        f"qm clone {source_vm_id} {target_vm_id} --name "
        f"{shlex.quote(target_name)} --full {full}"
    )


@operation()  # type: ignore[untyped-decorator]
def cloudinit_update(vm_id: int) -> Generator[str]:
    """
    Update cloud-init metadata for a VM.

    This operation regenerates the cloud-init metadata based on the
    VM's current configuration.

    Args:
        vm_id (int): ID of the VM

    Raises:
        OperationError: Raised if VM doesn't exist or on errors

    Yields:
        str | None: A string denoting the command or None for no-ops

    """
    if not host.get_fact(Which, command="pveversion"):
        err_msg = "Cannot run on a non-proxmox system"
        raise OperationError(err_msg)

    # Check that VM exists
    if not host.get_fact(qm.VmIdExists, vm_id=vm_id):
        err_msg = f"VM {vm_id} does not exist"
        raise OperationError(err_msg)

    # cloud-init update is always executed as it regenerates metadata
    yield f"qm cloudinit update {vm_id}"
