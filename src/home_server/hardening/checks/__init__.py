# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

import abc
import enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyinfra.api import State

    from home_server.hardening import Feature


class Profile(enum.Enum):
    """Hardening profiles that are allowed."""

    S1 = enum.auto()
    S2 = enum.auto()
    WS1 = enum.auto()
    WS2 = enum.auto()


class Level(enum.IntEnum):
    """Levels of hardening profiles that are allowed."""

    L1 = 1
    L2 = 2


def get_profile(platform: str, level: int) -> Profile:
    """
    Parse the user CLI arguments as a profile enum.

    Args:
        platform (str): Profile to run
        level (int): Level of the profile to run.

    Raises:
        ValueError: On unknown profile / level

    Returns:
        Profile: Profile enum of the profile to run

    """
    if platform == "server":
        if level == Level.L1:
            return Profile.S1
        if level == Level.L2:
            return Profile.S2
        err_msg = f"Unexpected level for server: {level}"
        raise ValueError(err_msg)
    if platform == "workstation":
        if level == Level.L1:
            return Profile.S1
        if level == Level.L2:
            return Profile.S2
        err_msg = f"Unexpected level for server: {level}"
        raise ValueError(err_msg)
    err_msg = f"Unexpected platform: {platform}"
    raise ValueError(err_msg)


class Check(abc.ABC):
    """
    The base class of all checks.

    This class defines a common interface for checks to implement for execution.
    """

    name = ""

    @classmethod
    def validate(cls) -> None:
        """Make sure the check is well-formed."""
        if not cls.name:
            err_msg = "Check subclasses must define a name as a class attribute"
            raise TypeError(err_msg)
        if not cls.description():
            err_msg = "Check subclasses must set a description as a docstring"
            raise TypeError(err_msg)

    @classmethod
    def enabled(
        cls, profile: Profile, requested_features: set[Feature]
    ) -> bool:
        """
        Determine if the check is enabled.

        Args:
            profile (Profile): Profile of checks to run
            requested_features (set[Feature]): Features that should be enabled

        Returns:
            bool: Whether the check should run.

        """
        min_profile_exceeded = False
        profiles = cls._minimum_profiles()
        if profile in profiles:
            min_profile_exceeded = True

        if profile == Profile.S2 and Profile.S1 in profiles:
            min_profile_exceeded = True
        if profile == Profile.WS2 and Profile.WS1 in profiles:
            min_profile_exceeded = True

        if not min_profile_exceeded:
            return False

        return requested_features.isdisjoint(cls.features())

    @classmethod
    def features(cls) -> set[Feature]:
        """
        Get the features this check helps enable.

        By executing, some checks will make changes to a host machine that are
        incompatible with features a user may want. By defining features that
        a check affects, that check can be removed from execution if that
        feature is desired.
        """
        return set()

    @classmethod
    @abc.abstractmethod
    def run(cls, state: State) -> None:
        """
        Add the check to the current state.

        Args:
            state (State): State to add the check to

        """

    @staticmethod
    @abc.abstractmethod
    def _minimum_profiles() -> set[Profile]: ...

    @classmethod
    def description(cls) -> str | None:
        """
        Get the description of the check.

        Returns:
            str | None: The check's docstring

        """
        return cls.__doc__
