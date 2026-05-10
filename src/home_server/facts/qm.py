# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

"""Define facts about qm - QEMU/KVM virtual machine manager."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from pyinfra.api import FactBase

if TYPE_CHECKING:
    from typing import Any


class List(FactBase):  # type: ignore[misc]
    """
    Return a list of VMs on the host.

    .. code:: python

        [
            (VM_ID, name, status, memory [MB], boot_disk [GB], PID), ...
        ]
    """

    @override
    def command(self) -> str:
        return "qm list"

    @override
    def requires_command(self) -> str:
        return "qm"

    default = list

    @override
    def process(self, output: list[str]) -> list[dict[str, Any]]:
        vms = []
        header = ["id", "name", "status", "mem", "boot_disk", "pid"]
        # first row is header so skip it
        for row in output[1:]:
            row_split = row.split()
            if len(header) != len(row_split):
                err_msg = "Unexpected output size of 'qm list'"
                raise ValueError(err_msg)
            vms.append(
                {
                    "id": int(row_split[0]),
                    "name": row_split[1],
                    "status": row_split[2],
                    "mem": int(row_split[3]),
                    "boot_disk": float(row_split[4]),
                    "pid": int(row_split[5]),
                }
            )
        return vms


class VmIdExists(FactBase):  # type: ignore[misc]
    """
    Returns True if a VM with the given ID exists.

    Usage: host.get_fact(VmIdExists, vm_id=8000)
    """

    @override
    def command(self, vm_id: int) -> str:
        return (
            "qm list | awk '{print $1}' | grep -q ^{vm_id}$ && echo 1 || echo 0"
        )

    @override
    def requires_command(self) -> str:
        return "qm"

    @override
    def process(self, output: list[str]) -> bool:
        return bool(int(output[0].strip()))


class VmStatus(FactBase):  # type: ignore[misc]
    """
    Return the status of a VM (running, stopped, paused).

    Usage: host.get_fact(VmStatus, vm_id=8000)
    """

    @override
    def command(self, vm_id: int) -> str:
        return f"qm status {vm_id}"

    @override
    def requires_command(self) -> str:
        return "qm"

    @override
    def process(self, output: list[str]) -> str:
        # output format: "status: running" or "status: stopped"
        if output and "status:" in output[0]:
            return output[0].split()[-1]
        return "unknown"


class VmConfig(FactBase):  # type: ignore[misc]
    """
    Return the current configuration of a VM as a dict.

    Usage: host.get_fact(VmConfig, vm_id=8000)

    Returns a dict with keys like: memory, cores, sockets, cpu,
    agent, ostype, scsihw, efidisk0, tags, scsi1, rng0, ciuser,
    cipassword, boot, bootdisk, tablet, ipconfig0, sshkeys, etc.
    """

    @override
    def command(self, vm_id: int) -> str:
        return f"qm config {vm_id}"

    @override
    def requires_command(self) -> str:
        return "qm"

    @override
    def process(self, output: list[str]) -> dict[str, Any]:
        config = {}
        for line_raw in output:
            line = line_raw.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                config[key] = value
        return config


class DiskSize(FactBase):  # type: ignore[misc]
    """
    Return the size of a VM disk in GiB.

    Usage: host.get_fact(DiskSize, vm_id=8000, disk_id='scsi0')

    Returns the disk size as a float or None if disk not found.
    """

    @override
    def command(self, vm_id: int, disk_id: str) -> str:
        # Use qm config and parse the disk entry
        return f"qm config {vm_id} | grep '^{disk_id}:' | head -1"

    @override
    def requires_command(self) -> str:
        return "qm"

    @override
    def process(self, output: list[str]) -> float | None:
        if not output or not output[0].strip():
            return None
        # output format: "scsi0: local:vm-100-disk-0,size=50G"
        # or "scsi0: local-lvm:vm-100-disk-0,size=50G"
        line = output[0].strip()
        if ":" not in line:
            return None
        value_part = line.split(":", 1)[1].strip()
        # Parse size from comma-separated values
        for part in value_part.split(","):
            if part.startswith("size="):
                size_str = part.split("=", 1)[1].strip()
                # Convert G/T/M suffix to GiB
                multiplier = 1.0
                if size_str.endswith("G"):
                    size_str = size_str[:-1]
                    multiplier = 1.0
                elif size_str.endswith("T"):
                    size_str = size_str[:-1]
                    multiplier = 1024.0
                elif size_str.endswith("M"):
                    size_str = size_str[:-1]
                    multiplier = 1.0 / 1024
                try:
                    return float(size_str) * multiplier
                except ValueError:
                    return None
        return None
