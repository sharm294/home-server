# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from pyinfra.api.operation import add_op
from pyinfra.operations import files, server

from .. import Check, Feature, Profile

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

    @classmethod
    def features(cls) -> set[Feature]:
        return {Feature.CONTAINERS}

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


class CIS_7(Check):
    name = "1.1.1.7"
    description = "Ensure squashfs kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the squashfs kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("squashfs", state)

    @classmethod
    def features(cls) -> set[Feature]:
        return {Feature.SNAP}

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


class CIS_8(Check):
    name = "1.1.1.8"
    description = "Ensure udf kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the udf kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("udf", state)

    @classmethod
    def features(cls) -> set[Feature]:
        return {Feature.SNAP}

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


class CIS_9(Check):
    name = "1.1.1.9"
    description = "Ensure firewire-core kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the firewire-core kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("firewire-core", state)

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS2}


class CIS_10(Check):
    name = "1.1.1.10"
    description = "Ensure usb-storage kernel module is not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure the usb-storage kernel module is not available by unloading it and
        then disabling it.
        """
        remove_and_blacklist_kernel_module("usb-storage", state)

    @classmethod
    def features(cls) -> set[Feature]:
        return {Feature.USB_STORAGE}

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS2}


class CIS_11(Check):
    name = "1.1.1.11"
    description = "Ensure unused filesystems kernel modules are not available"

    @classmethod
    def run(cls, state: State):
        """
        Ensure unused filesystems kernel modules are not available.
        """
        name = "Run audit script to print filesystems kernel modules"
        add_op(state, server.shell, name, commands=["./cis_1_1_1_11.sh"])

    @staticmethod
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


def get_checks() -> list[Check]:
    checks: list[Check] = [
        CIS_1,
        CIS_2,
        CIS_3,
        CIS_4,
        CIS_5,
        CIS_6,
        CIS_7,
        CIS_8,
        CIS_9,
        CIS_10,
        CIS_11,
    ]
    for check in checks:
        check.validate()
    return checks
