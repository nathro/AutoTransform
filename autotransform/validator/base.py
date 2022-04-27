# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Validator components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Generic, Mapping, Optional, TypedDict, TypeVar

from autotransform.batcher.base import Batch
from autotransform.validator.type import ValidatorType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class ValidationResultLevel(int, Enum):
    """The result level of a validation indicating how bad a validation failure is."""

    NONE = 0
    WARNING = 1
    ERROR = 2

    @staticmethod
    def has_value(value: Any) -> bool:
        """Checks is the provided value is a valid value for this enum.

        Args:
            value (Any): An unknown value.

        Returns:
            [bool]: Whether the value is present in the enum.
        """

        # pylint: disable=no-member

        return value in ValidationResultLevel._value2member_map_

    @staticmethod
    def from_name(name: str) -> Enum:
        """Gets the enum value associated with a name.

        Args:
            name (str): The name of a member of the enum.

        Returns:
            ValidationResultLevel: The associated enum value.
        """

        # pylint: disable=no-member

        return ValidationResultLevel._member_map_[name]

    @staticmethod
    def from_value(value: int) -> Enum:
        """Gets the enum value associated with an int value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            ValidationResultLevel: The associated enum value.
        """

        # pylint: disable=no-member

        return ValidationResultLevel._value2member_map_[value]


class ValidationResult(TypedDict):
    """Represents the result of an attempt at validation."""

    level: ValidationResultLevel
    message: Optional[str]
    validator: ValidatorType


class ValidationError(Exception):
    """An error raised by validation failing on a run.

    Attributes:
        _issue (ValidationResult): The validation result that triggered the error.
        _message (str): A message representing why the validation failed.
    """

    _issue: ValidationResult
    _message: Optional[str]

    def __init__(self, issue: ValidationResult):
        """A simple constructor.

        Args:
            issue (ValidationResult): The issue responsible for the validation error.
        """

        super().__init__(issue["message"])
        self._message = issue["message"]
        self._issue = issue

    def __str__(self) -> str:
        """Override the default str casting of the error to include useful information.

        Returns:
            str: A string representation of the error.
        """

        level = ValidationResultLevel(self._issue["level"]).name
        validator = self._issue["validator"]

        return f"[{level}][{validator}]: {self._message}"


class ValidatorBundle(TypedDict):
    """A bundled version of the Validator object used for JSON encoding."""

    params: Mapping[str, Any]
    type: ValidatorType


class Validator(Generic[TParams], ABC):
    """The base for Validator components. Validators test that the codebase is still
    healthy after a transformation.

    Attributes:
        _params (TParams): The paramaters that control operation of the Validator.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Validator.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Validator.

        Returns:
            TParams: The paramaters used to set up the Validator.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> ValidatorType:
        """Used to map Validator components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ValidatorType: The unique type associated with this Validator.
        """

    @abstractmethod
    def validate(self, batch: Batch) -> ValidationResult:
        """Validate that a Batch that has undergone transformation does not produce any issues
        such as test failures or type errors.

        Args:
            batch (Batch): The transformed Batch to validate.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
        """

    def bundle(self) -> ValidatorBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            ValidatorBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Validator:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Validator: An instance of the Validator.
        """
