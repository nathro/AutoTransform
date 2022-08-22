# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the SchemaNameCondition."""

from __future__ import annotations

from typing import ClassVar, List

from autotransform.change.base import Change
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.comparison import ComparisonType


class SchemaNameCondition(ComparisonCondition[str]):
    """A condition which checks the name of the Schema that produced a change against the supplied
    name, using the supplied comparison.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (str | List[str]): The schema name(s) to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: str | List[str]

    name: ClassVar[ConditionName] = ConditionName.SCHEMA_NAME

    def get_val_from_change(self, change: Change) -> str:
        """Gets the Schema name from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            str: The name of the Schema that produced the change.
        """

        return change.get_schema_name()
