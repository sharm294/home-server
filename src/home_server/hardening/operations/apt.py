# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing

from pyinfra.api.operation import add_op
from pyinfra.operations import apt

if typing.TYPE_CHECKING:
    from pyinfra.api import State
    from pyinfra.api.operation import OperationMeta


def ensure_unzip_present(state: State) -> OperationMeta:
    return add_op(
        state,
        apt.packages,
        name="Ensure 'unzip' package is installed",
        packages=["unzip"],
        update=True,
        cache_time=3600,
        _sudo=True,
    )


def ensure_unzip_present_2():
    apt.packages(
        name="Ensure the vim apt package is installed",
        packages=["unzip"],
        update=True,
        cache_time=3600,
        _sudo=True,
    )
