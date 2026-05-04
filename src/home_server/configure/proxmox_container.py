# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Configure the Proxmox vm.

This file defines how to configure the Proxmox VM after creation.
"""

from pyinfra.api import State
from pyinfra.api.operation import add_op
from pyinfra.operations import server


def main(state: State) -> None:
    """Entrypoint for configuring the Proxmox container."""
    add_op(
        state,
        server.script,
        "src/home_server/configure/samba.sh",
    )
