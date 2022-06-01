# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Validator components."""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional

from autotransform.batcher.base import Batch
from autotransform.util.component import Component, ComponentFactory, ComponentImport


class ValidationResultLevel(int, Enum):
    """The result level of a validation indicating how bad a validation failure is."""

    NONE = 0
    WARNING = 1
    ERROR = 2


@dataclass
class ValidationResult:
    """Represents the result of an attempt at validation.

    Attributes:
        level (ValidationResultLevel): The level of the validation issue raised.
        message (Optional[str], optional): The message associated with the validation
            result. Defaults to None.
    """

    level: ValidationResultLevel
    validator: Validator
    message: Optional[str] = None


@dataclass
class ValidationError(Exception):
    """An error raised by validation failing on a run.

    Attributes:
        issue (ValidationResult): The validation result that triggered the error.
        message (str): A message representing why the validation failed.
    """

    issue: ValidationResult
    message: Optional[str]


class ValidatorName(str, Enum):
    """A simple enum for mapping."""

    SCRIPT = "script"


class Validator(Component):
    """The base for Validator components. Validators test that the codebase is still
    healthy after a transformation.

    Attributes:
        _params (TParams): The paramaters that control operation of the Validator.
            Should be defined using a TypedDict in subclasses.
    """

    @abstractmethod
    def validate(
        self, batch: Batch, transform_data: Optional[Mapping[str, Any]]
    ) -> ValidationResult:
        """Validate that a Batch that has undergone transformation does not produce any issues
        such as test failures or type errors.

        Args:
            batch (Batch): The transformed Batch to validate.
            transform_data (Optional[Mapping[str, Any]]): Data from the transformation.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
        """


FACTORY = ComponentFactory(
    {
        ValidatorName.SCRIPT: ComponentImport(
            class_name="ScriptValidator", module="autotransform.validator.script"
        ),
    },
    Validator,  # type: ignore [misc]
    "validator.json",
)
