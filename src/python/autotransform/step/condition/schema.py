# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the SchemaNameCondition."""

from __future__ import annotations

from typing import ClassVar

from autotransform.change.base import Change
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.comparison import ComparisonType


class SchemaNameCondition(ComparisonCondition[str]):
    """A condition which checks the name of the Schema that produced a change against the supplied
    name, using the supplied comparison. Note: only equals and not equals are valid, all others will
    result in an error.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (str): The schema name to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: str

    name: ClassVar[ConditionName] = ConditionName.SCHEMA_NAME

    def get_val_from_change(self, change: Change) -> str:
        """Gets the Schema name from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            str: The name of the Schema that produced the change.
        """

        return change.get_schema().config.schema_name
