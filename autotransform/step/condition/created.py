# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for all conditions handling when a Change was created."""

from __future__ import annotations

import time
from typing import Any, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.step.condition.base import Condition
from autotransform.step.condition.comparison import ComparisonType, compare
from autotransform.step.condition.type import ConditionType


class CreatedAgoConditionParams(TypedDict):
    """The param type for a CreatedAgoCondition."""

    comparison: ComparisonType
    time: int


class CreatedAgoCondition(Condition[CreatedAgoConditionParams]):
    """A condition which checks how long ago a Change was created against the supplied time, all
    in seconds, using the supplied comparison.

    Attributes:
        _params (TParams): The comparison type and time to compare against.
    """

    _params: CreatedAgoConditionParams

    @staticmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionType.CREATED_AGO

    def check(self, change: Change) -> bool:
        """Checks whether how long ago the Change was created passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        time_since_created = time.time() - change.get_created_timestamp()
        return compare(time_since_created, self._params["time"], self._params["comparison"])

    def __str__(self) -> str:
        return f"Created Ago {self._params['comparison'].name.lower()} {self._params['time']}"

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> CreatedAgoCondition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            CreatedAgoCondition: An instance of the CreatedAgoCondition.
        """

        comparison = data["comparison"]
        if not ComparisonType.has_value(comparison):
            comparison = ComparisonType.from_name(comparison)
        else:
            comparison = ComparisonType.from_value(comparison)

        time_param = data["time"]
        assert isinstance(time_param, int)

        return CreatedAgoCondition({"comparison": comparison, "time": time_param})
