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
from typing import Any, ClassVar, Dict, Mapping, Optional

from autotransform.batcher.base import Batch
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class ValidationResultLevel(str, Enum):
    """The result level of a validation indicating how bad a validation failure is."""

    NONE = "none"
    WARNING = "warning"
    ERROR = "error"

    def compare(self, other: str) -> int:
        """Compares two result levels and returns an integer indicating the comparison.

        Args:
            other (str): The value to compare against.

        Returns:
            int: A negative number if lt, 0 if equal, and a positive number if gt.
        """

        if self.value is other:
            return 0
        val_order: Dict[str, int] = {"none": 0, "warning": 1, "error": 2}
        return val_order[self.value] - val_order[other]

    def __eq__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) == 0

    def __ne__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) != 0

    def __lt__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) < 0

    def __le__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) <= 0

    def __gt__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) > 0

    def __ge__(self, other: object) -> bool:
        return self.compare(str(other.value) if isinstance(other, Enum) else str(other)) >= 0


@dataclass(frozen=True, kw_only=True)
class ValidationResult:
    """Represents the result of an attempt at validation.

    Attributes:
        level (ValidationResultLevel): The level of the validation issue raised.
        validator (Validator): The Validator that returned this result.
        message (Optional[str], optional): The message associated with the validation
            result. Defaults to None.
    """

    level: ValidationResultLevel
    validator: Validator
    message: Optional[str] = None


@dataclass(frozen=True, kw_only=True)
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


class Validator(NamedComponent):
    """The base for Validator components. Validators test that the codebase is still
    healthy after a transformation.

    Attributes:
        name (ClassVar[ValidatorName]): The name of the component.
    """

    name: ClassVar[ValidatorName]

    @abstractmethod
    def check(self, batch: Batch, transform_data: Optional[Mapping[str, Any]]) -> ValidationResult:
        """Validate that a Batch that has undergone transformation does not produce any issues
        such as test failures or type errors.

        Args:
            batch (Batch): The transformed Batch to validate.
            transform_data (Optional[Mapping[str, Any]]): Data from the transformation.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message.
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
