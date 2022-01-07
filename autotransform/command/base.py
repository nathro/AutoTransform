# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, TypedDict

from autotransform.batcher.base import Batch
from autotransform.command.type import CommandType


class CommandBundle(TypedDict):
    params: Mapping[str, Any]
    type: CommandType


class Command(ABC):
    params: Mapping[str, Any]

    def __init__(self, params: Mapping[str, Any]):
        self.params = params

    @abstractmethod
    def get_type(self) -> CommandType:
        pass

    @abstractmethod
    def run(self, batch: Batch) -> None:
        pass

    def bundle(self) -> CommandBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Command:
        pass
