# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from pyinfra.api.operation import add_op
from pyinfra.operations import files, server

from .. import Check, Profile

if TYPE_CHECKING:
    from pyinfra.api import State


class CIS_1(Check):
    def __init__(self):
        super().__init__(
            "1.1.1.1", "Ensure cramfs kernel module is not available"
        )

    def run(self, state: State):
        """
        Ensure the cramfs kernel module is not available by unloading it and
        then disabling it.
        """
        add_op(state, server.modprobe, "cramfs", present=False, _sudo=True)

        add_op(
            state,
            files.line,
            "/etc/modprobe.d/cis.conf",
            "install cramfs /bin/false",
            present=True,
            _sudo=True,
        )

        add_op(
            state,
            files.line,
            "/etc/modprobe.d/cis.conf",
            "blacklist cramfs",
            present=True,
            _sudo=True,
        )

    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}
