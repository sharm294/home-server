# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from home_server.hardening.checks import Check

REGISTRY: list[type[Check]] = []


def register_check(check: type[Check]) -> type[Check]:
    """
    Register all the decorated checks to a registry using a decorator.

    Args:
        check (type[Check]): Check to register

    Returns:
        type[Check]: Registered check

    """
    check.validate()
    REGISTRY.append(check)
    return check


from . import cis_1_1_1_x as cis_1_1_1_x  # noqa: E402
