# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.filter.type import FilterType


class FilterBundle(TypedDict):
    inverted: Optional[bool]
    params: Mapping[str, Any]
    type: FilterType


class Filter(ABC):
    inverted: bool
    params: Mapping[str, Any]

    def __init__(self, params: Mapping[str, Any]):
        self.inverted = False
        self.params = params

    @abstractmethod
    def get_type(self) -> FilterType:
        pass

    def invert(self) -> Filter:
        self.inverted = not self.inverted
        return self

    def is_valid(self, file: CachedFile) -> bool:
        return self.inverted != self._is_valid(file)

    @abstractmethod
    def _is_valid(self, file: CachedFile) -> bool:
        pass

    def bundle(self) -> FilterBundle:
        return {
            "inverted": self.inverted,
            "params": self.params,
            "type": self.get_type(),
        }

    @classmethod
    def from_data(cls, inverted: Optional[bool], data: Mapping[str, Any]) -> Filter:
        unbundled_filter = cls._from_data(data)
        if inverted:
            unbundled_filter.invert()
        return unbundled_filter

    @staticmethod
    @abstractmethod
    def _from_data(data: Mapping[str, Any]) -> Filter:
        pass
