# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the PytestValidator."""

from __future__ import annotations

import subprocess
from typing import Any, List, Mapping, TypedDict

from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.validator.base import ValidationResult, ValidationResultLevel, Validator
from autotransform.validator.type import ValidatorType


class PytestValidatorParams(TypedDict):
    """The param type for a PytestValidator"""

    args: List[str]


class PytestValidator(Validator[PytestValidatorParams]):
    """Runs Pytest with the supplied arguments.
    Returns an error result if pytest returns a non-zero exit code.

    Attributes:
        _params (TParams): Contains the args for pytest.
    """

    _params: PytestValidatorParams

    @staticmethod
    def get_type() -> ValidatorType:
        """Used to map Validator components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ValidatorType: The unique type associated with this Validator.
        """

        return ValidatorType.PYTEST

    def validate(self, batch: Batch) -> ValidationResult:
        """Validate that a Batch that has undergone transformation does not produce any issues
        such as test failures or type errors.

        Args:
            batch (Batch): The transformed Batch to validate.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
        """

        cmd = ["pytest"]
        for arg in self._params["args"]:
            cmd.append(arg)
        proc = subprocess.run(cmd, capture_output=True, encoding="ascii", check=False)

        EventHandler.get().handle(
            DebugEvent({"message": f"Pytest validation stdout:\n{proc.stdout}"})
        )
        level = ValidationResultLevel.ERROR if proc.returncode != 0 else ValidationResultLevel.NONE
        return {
            "level": level,
            "message": proc.stderr,
            "validator": self.get_type(),
        }

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> PytestValidator:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            PytestValidator: An instance of the PytestValidator.
        """

        args = data["args"]
        assert isinstance(args, List)
        for arg in args:
            assert isinstance(arg, str)

        return PytestValidator({"args": args})
