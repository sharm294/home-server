# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

from typing import TYPE_CHECKING

from .cis_1_1_1_x import get_checks as get_checks_1_1_1

if TYPE_CHECKING:
    from .. import Check

REGISTRY: list[Check] = [
    *get_checks_1_1_1(),
]
