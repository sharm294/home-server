# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

"""Implement the CIS 1.1.1.x checks."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from pyinfra.api.operation import add_op
from pyinfra.operations import files, server

from home_server.hardening import Feature
from home_server.hardening.checks import Check, Profile
from home_server.hardening.checks.debian_13 import register_check

if TYPE_CHECKING:
    from pyinfra.api import State


def remove_and_blacklist_kernel_module(name: str, state: State) -> None:
    """
    Remove and blacklist a kernel module.

    Args:
        name (str): Name of the kernel module
        state (State): State to add the step to

    """
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


@register_check
class CIS1(Check):
    """Ensure cramfs kernel module is not available."""

    name = "1.1.1.1"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("cramfs", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


@register_check
class CIS2(Check):
    """Ensure freevxfs kernel module is not available."""

    name = "1.1.1.2"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("freevxfs", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


@register_check
class CIS3(Check):
    """Ensure hfs kernel module is not available."""

    name = "1.1.1.3"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("hfs", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


@register_check
class CIS4(Check):
    """Ensure hfsplus kernel module is not available."""

    name = "1.1.1.4"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("hfsplus", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


@register_check
class CIS5(Check):
    """Ensure jffs2 kernel module is not available."""

    name = "1.1.1.5"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("jffs2", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}


@register_check
class CIS6(Check):
    """Ensure overlay kernel module is not available."""

    name = "1.1.1.6"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("overlay", state)

    @classmethod
    @override
    def features(cls) -> set[Feature]:
        return {Feature.CONTAINERS}

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


@register_check
class CIS7(Check):
    """Ensure squashfs kernel module is not available."""

    name = "1.1.1.7"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("squashfs", state)

    @classmethod
    @override
    def features(cls) -> set[Feature]:
        return {Feature.SNAP}

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


@register_check
class CIS8(Check):
    """Ensure udf kernel module is not available."""

    name = "1.1.1.8"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("udf", state)

    @classmethod
    @override
    def features(cls) -> set[Feature]:
        return {Feature.SNAP}

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S2, Profile.WS2}


@register_check
class CIS9(Check):
    """Ensure firewire-core kernel module is not available."""

    name = "1.1.1.9"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("firewire-core", state)

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS2}


@register_check
class CIS10(Check):
    """Ensure usb-storage kernel module is not available."""

    name = "1.1.1.10"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        remove_and_blacklist_kernel_module("usb-storage", state)

    @classmethod
    @override
    def features(cls) -> set[Feature]:
        return {Feature.USB_STORAGE}

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS2}


@register_check
class CIS11(Check):
    """Ensure unused filesystems kernel modules are not available."""

    name = "1.1.1.11"

    @classmethod
    @override
    def run(cls, state: State) -> None:
        add_op(
            state,
            server.script,
            "src/home_server/hardening/checks/debian_13/cis_1_1_1_11.sh",
        )

    @staticmethod
    @override
    def _minimum_profiles() -> set[Profile]:
        return {Profile.S1, Profile.WS1}
