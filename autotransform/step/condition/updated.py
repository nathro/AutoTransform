# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for all conditions handling when a Change was updated."""

from __future__ import annotations

import time
from typing import Any, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.step.condition.base import Condition
from autotransform.step.condition.comparison import ComparisonType, compare
from autotransform.step.condition.type import ConditionType


class UpdatedAgoConditionParams(TypedDict):
    """The param type for a UpdatedAgoCondition."""

    comparison: ComparisonType
    time: int


class UpdatedAgoCondition(Condition[UpdatedAgoConditionParams]):
    """A condition which checks how long ago a Change was updated against the supplied time, all
    in seconds, using the supplied comparison.

    Attributes:
        _params (TParams): The comparison type and time to compare against.
    """

    _params: UpdatedAgoConditionParams

    @staticmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionType.UPDATED_AGO

    def check(self, change: Change) -> bool:
        """Checks whether how long ago the Change was updated passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        time_since_updated = time.time() - change.get_last_updated_timestamp()
        return compare(time_since_updated, self._params["time"], self._params["comparison"])

    def __str__(self) -> str:
        return f"Updated Ago {self._params['comparison'].name.lower()} {self._params['time']}"

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> UpdatedAgoCondition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            UpdatedAgoCondition: An instance of the UpdatedAgoCondition.
        """

        comparison = data["comparison"]
        if not ComparisonType.has_value(comparison):
            comparison = ComparisonType.from_name(comparison)
        else:
            comparison = ComparisonType.from_value(comparison)

        time_param = data["time"]
        assert isinstance(time_param, int)

        return UpdatedAgoCondition({"comparison": comparison, "time": time_param})
