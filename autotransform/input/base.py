# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, TypedDict

from autotransform.inputsource.type import InputType


class InputBundle(TypedDict):
    params: Mapping[str, Any]
    type: InputType


class Input(ABC):
    params: Mapping[str, Any]

    def __init__(self, params: Mapping[str, Any]):
        self.params = params

    @abstractmethod
    def get_type(self) -> InputType:
        pass

    @abstractmethod
    def get_files(self) -> List[str]:
        pass

    def bundle(self) -> InputBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Input:
        pass
