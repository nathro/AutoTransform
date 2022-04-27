# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the MypyValidator."""

from __future__ import annotations

from typing import Any, List, Mapping, TypedDict

from mypy import api
from typing_extensions import NotRequired

from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.validator.base import ValidationResult, ValidationResultLevel, Validator
from autotransform.validator.type import ValidatorType


class MypyValidatorParams(TypedDict):
    """The param type for a MypyValidator"""

    targets: NotRequired[List[str]]
    check_changed_files: NotRequired[bool]


class MypyValidator(Validator[MypyValidatorParams]):
    """Runs Mypy against supplied targets and any changed files if the flag is set for that.
    Returns an error result if Mypy returns a non-zero exit code.

    Attributes:
        _params (TParams): Contains the information to choose targets for mypy.
    """

    _params: MypyValidatorParams

    @staticmethod
    def get_type() -> ValidatorType:
        """Used to map Validator components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ValidatorType: The unique type associated with this Validator.
        """

        return ValidatorType.MYPY

    def validate(self, batch: Batch) -> ValidationResult:
        """Validate that a Batch that has undergone transformation does not produce any issues
        such as test failures or type errors.

        Args:
            batch (Batch): The transformed Batch to validate.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
        """

        # pylint: disable=c-extension-no-member

        targets: List[str] = []
        for target in self._params.get("targets", []):
            targets.append(target)
        sout, serr, code = api.run(targets)

        EventHandler.get().handle(DebugEvent({"message": f"Mypy validation stdout: {sout}"}))

        return {
            "level": ValidationResultLevel.ERROR if code != 0 else ValidationResultLevel.NONE,
            "message": serr,
            "validator": self.get_type(),
        }

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> MypyValidator:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Validator: An instance of the MypyValidator.
        """
