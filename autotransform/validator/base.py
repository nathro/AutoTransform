# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Mapping, Optional, TypedDict

from autotransform.batcher.base import BatchWithFiles
from autotransform.validator.type import ValidatorType


class ValidationResultLevel(int, Enum):
    NONE = 0
    WARNING = 1
    ERROR = 2

    @staticmethod
    def has_value(value: Any):
        # pylint: disable=no-member
        return value in ValidationResultLevel._value2member_map_

    @staticmethod
    def from_name(name: str):
        # pylint: disable=no-member
        assert name in ValidationResultLevel._member_names_
        return ValidationResultLevel._member_map_[name]


class ValidationResult(TypedDict):
    level: ValidationResultLevel
    message: Optional[str]
    validator: ValidatorType


class ValidationError(Exception):
    issue: ValidationResult

    def __init__(self, issue: ValidationResult):
        self.issue = issue
        self.message = issue["message"]
        super().__init__(self.message)

    def __str__(self):
        level = ValidationResultLevel(self.issue["level"]).name
        validator = self.issue["validator"]

        return f"[{level}][{validator}]: {self.message}"


class ValidatorBundle(TypedDict):
    params: Mapping[str, Any]
    type: ValidatorType


class Validator(ABC):
    params: Mapping[str, Any]

    def __init__(self, params: Dict[str, Any]):
        self.params = params

    @abstractmethod
    def get_type(self) -> ValidatorType:
        pass

    @abstractmethod
    def validate(self, batch: BatchWithFiles) -> ValidationResult:
        pass

    def bundle(self) -> ValidatorBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Validator:
        pass
