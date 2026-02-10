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


def get_profile(platform: str, level: int) -> Profile:
    if platform == "server":
        if level == 1:
            return Profile.S1
        if level == 2:
            return Profile.S2
        raise ValueError(f"Unexpected level for server: {level}")
    if platform == "workstation":
        if level == 1:
            return Profile.S1
        if level == 2:
            return Profile.S2
        raise ValueError(f"Unexpected level for server: {level}")
    raise ValueError(f"Unexpected platform: {platform}")


class Check(abc.ABC):
    name = None
    description = None

    @classmethod
    def validate(cls):
        if cls.name is None:
            raise TypeError(
                "Check subclasses must define a name as a class attribute"
            )
        if cls.description is None:
            raise TypeError(
                "Check subclasses must set a description as a class attribute"
            )

    @classmethod
    def enabled(cls, profile: Profile) -> bool:
        profiles = cls._minimum_profiles()
        if profile in profiles:
            return True

        if profile == Profile.S2 and Profile.S1 in profiles:
            return True
        if profile == Profile.WS2 and Profile.WS1 in profiles:
            return True
        return False

    @classmethod
    @abc.abstractmethod
    def run(cls, state: State): ...

    @staticmethod
    @abc.abstractmethod
    def _minimum_profiles() -> set[Profile]: ...
