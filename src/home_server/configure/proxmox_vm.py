# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: AGPL-3.0-or-later

"""
Configure the Proxmox vm.

This file defines how to configure the Proxmox VM after creation.
"""

import tempfile

from pyinfra.api import State
from pyinfra.api.operation import add_op
from pyinfra.operations import files, server


def main(state: State) -> None:
    """Entrypoint for configuring the Proxmox VM."""
    with tempfile.NamedTemporaryFile() as f:
        add_op(
            state,
            files.download,
            # https://github.com/OpenMediaVault-Plugin-Developers/installScript/blob/master/install
            "https://github.com/OpenMediaVault-Plugin-Developers/installScript/raw/master/install",
            f.name,
            mode="777",
            sha256sum="c994d336a3fd66f463b2fc5cda18aa8619baf639448c6545c92e2012f5fb9020",
        )

        add_op(state, server.shell, [f"{f.name} -r -f"])
