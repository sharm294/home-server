# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyinfra.api import State


class Profile(enum.Enum):
    S1 = enum.auto()
    S2 = enum.auto()
    WS1 = enum.auto()
    WS2 = enum.auto()


class Check(abc.ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def enabled(self, profile: Profile) -> bool:
        profiles = self._minimum_profiles()
        if profile in profiles:
            return True

        if profile == Profile.S2 and Profile.S1 in profiles:
            return True
        if profile == Profile.WS2 and Profile.WS1 in profiles:
            return True
        return False

    @abc.abstractmethod
    def run(self, state: State): ...

    @abc.abstractmethod
    def _minimum_profiles() -> set[Profile]: ...
