# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Configure the Proxmox host.

This file defines how to configure the Proxmox host after installation.
"""

from pyinfra.api import State
from pyinfra.api.operation import add_op
from pyinfra.operations import server


def main(state: State) -> None:
    """Entrypoint for configuring the Proxmox host."""
    add_op(
        state,
        server.script,
        "src/home_server/configure/proxmox_community_scripts/microcode.sh",
    )

    add_op(
        state,
        server.script,
        "src/home_server/configure/proxmox_community_scripts/post-pve-install.sh",
    )

    add_op(
        state,
        server.script,
        "src/home_server/configure/cloud_debian_13.sh",
    )
