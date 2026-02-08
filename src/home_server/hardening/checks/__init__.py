# Copyright (c) 2026 sharm294
# SPDX-License-Identifier: MIT

import abc


class Check(abc.ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abc.abstractmethod
    def run(self): ...
