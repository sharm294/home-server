# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

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
