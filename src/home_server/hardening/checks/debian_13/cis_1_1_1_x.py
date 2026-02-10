# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from pyinfra.api.operation import add_op
from pyinfra.operations import files, server

from .. import Check, Profile

if TYPE_CHECKING:
    from pyinfra.api import State


def remove_and_blacklist_kernel_module(name: str, state: State):
    add_op(state, server.modprobe, name, present=False)

    add_op(
        state,
        files.line,
        "/etc/modprobe.d/cis.conf",
        f"install {name} /bin/false",
        present=True,
    )

    add_op(
        state,
        files.line,
        "/etc/modprobe.d/cis.conf",
        f"blacklist {name}",
        present=True,
    )


class CIS_1(Check):
    name = "1.1.1.1"
    description = "Ensure cramfs kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the cramfs kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("cramfs", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


class CIS_2(Check):
    name = "1.1.1.2"
    description = "Ensure freevxfs kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the freevxfs kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("freevxfs", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


class CIS_3(Check):
    name = "1.1.1.3"
    description = "Ensure hfs kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the hfs kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("hfs", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


class CIS_4(Check):
    name = "1.1.1.4"
    description = "Ensure hfsplus kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the hfsplus kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("hfsplus", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


class CIS_5(Check):
    name = "1.1.1.5"
    description = "Ensure jffs2 kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the jffs2 kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("jffs2", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


class CIS_6(Check):
    name = "1.1.1.6"
    description = "Ensure overlay kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the overlay kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("overlay", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


def get_checks() -> list[Check]:
    checks: list[Check] = [CIS_1, CIS_2, CIS_3, CIS_4, CIS_5, CIS_6]
    for check in checks:
        check.validate()
    return checks
