# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for all conditions handling when a Change was created."""

from __future__ import annotations

import json
from enum import Enum
from typing import Any, Dict, List, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.step.condition import factory
from autotransform.step.condition.base import Condition, ConditionBundle
from autotransform.step.condition.type import ConditionType


class AggregatorType(str, Enum):
    """A list of possible comparisons."""

    ALL = "all"
    ANY = "any"

    @staticmethod
    def has_value(value: Any) -> bool:
        """Checks is the provided value is a valid value for this enum.

        Args:
            value (Any): An unknown value.

        Returns:
            [bool]: Whether the value is present in the enum.
        """

        # pylint: disable=no-member

        return value in AggregatorType._value2member_map_

    @staticmethod
    def from_name(name: str) -> Enum:
        """Gets the enum value associated with a name.

        Args:
            name (str): The name of a member of the enum.

        Returns:
            AggregatorType: The associated enum value.
        """

        # pylint: disable=no-member

        return AggregatorType._member_map_[name]

    @staticmethod
    def from_value(value: int) -> Enum:
        """Gets the enum value associated with an int value.

        Args:
            value (str): The value of a member of the enum.

        Returns:
            AggregatorType: The associated enum value.
        """

        # pylint: disable=no-member

        return AggregatorType._value2member_map_[value]


class AggregateConditionParams(TypedDict):
    """The param type for a AggregateCondition."""

    conditions: List[Condition]
    aggregator: AggregatorType


class AggregateCondition(Condition[AggregateConditionParams]):
    """A Condition which aggregates a list of Conditions using the supplied aggregator and
    returns the result of the aggregation.

    Attributes:
        _params (TParams): The aggregator type and list of Conditions.
    """

    _params: AggregateConditionParams

    @staticmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionType.AGGREGATE

    def check(self, change: Change) -> bool:
        """Checks whether how long ago the Change was created passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        if self._params["aggregator"] == AggregatorType.ALL:
            for condition in self._params["conditions"]:
                if not condition.check(change):
                    return False
            return True

        if self._params["aggregator"] == AggregatorType.ANY:
            for condition in self._params["conditions"]:
                if condition.check(change):
                    return True
            return False

        raise ValueError(f"Unknown aggregator type {self._params['aggregator']}")

    def bundle(self) -> ConditionBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            ConditionBundle: The encodable bundle.
        """
        bundled_params: Dict[str, Any] = {
            "conditions": [condition.bundle() for condition in self._params["conditions"]],
            "aggregator": self._params["aggregator"],
        }

        return {
            "params": bundled_params,
            "type": self.get_type(),
        }

    def __str__(self) -> str:
        conditions = [str(condition) for condition in self._params["conditions"]]
        return f"{self._params['aggregator']} {json.dumps(conditions)}"

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> AggregateCondition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            AggregateCondition: An instance of the AggregateCondition.
        """

        aggregator = data["aggregator"]
        if not AggregatorType.has_value(aggregator):
            aggregator = AggregatorType.from_name(aggregator)
        else:
            aggregator = AggregatorType.from_value(aggregator)

        conditions = [factory.ConditionFactory.get(condition) for condition in data["conditions"]]

        return AggregateCondition({"conditions": conditions, "aggregator": aggregator})
