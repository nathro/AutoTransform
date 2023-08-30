# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the AggregateCondition."""

from typing import Any, ClassVar, Dict, List, Type

from autotransform.change.base import Change
from autotransform.step.condition.base import FACTORY as condition_factory
from autotransform.step.condition.base import Condition, ConditionName
from autotransform.util.enums import AggregatorType


class AggregateCondition(Condition):
    """A Condition which aggregates a list of Conditions using the supplied aggregator and
    returns the result of the aggregation.

    Attributes:
        aggregator (AggregatorType): How to aggregate the conditions, using any or all.
        conditions (List[Condition]): The conditions to be aggregated.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    aggregator: AggregatorType
    conditions: List[Condition]

    name: ClassVar[ConditionName] = ConditionName.AGGREGATE

    def check(self, change: Change) -> bool:
        """Checks whether the aggregation of all conditions passes.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        aggregator_check = all if self.aggregator == AggregatorType.ALL else any
        return aggregator_check(condition.check(change) for condition in self.conditions)

    @classmethod
    def from_data(cls: Type["AggregateCondition"], data: Dict[str, Any]) -> "AggregateCondition":
        """Produces an instance of the component from decoded data.

        Args:
            data (Dict[str, Any]): The JSON decoded data.

        Returns:
            AggregateCondition: An instance of the component.
        """

        aggregator = (
            AggregatorType(data["aggregator"])
            if isinstance(data["aggregator"], str)
            else data["aggregator"]
        )
        conditions = [condition_factory.get_instance(condition) for condition in data["conditions"]]
        return cls(aggregator=aggregator, conditions=conditions)
