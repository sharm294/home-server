# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import enum


class Profile(enum.Enum):
    S1 = enum.auto()
    S2 = enum.auto()
    WS1 = enum.auto()
    WS2 = enum.auto()


from .main import main

__all__ = ["Profile", "main"]
