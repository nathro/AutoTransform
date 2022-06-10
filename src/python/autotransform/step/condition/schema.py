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
from autotransform.step.condition.base import Condition, ConditionName
from autotransform.step.condition.comparison import ComparisonType, compare


class SchemaNameCondition(Condition):
    """A condition which checks the name of the Schema that produced a change against the supplied
    name, using the supplied comparison. Note: only equals and not equals are valid, all others will
    result in an error.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        schema_name (str): The schema name to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    schema_name: str

    name: ClassVar[ConditionName] = ConditionName.SCHEMA_NAME

    def check(self, change: Change) -> bool:
        """Checks whether the the schema name passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """

        assert self.comparison in [
            ComparisonType.EQUAL,
            ComparisonType.NOT_EQUAL,
        ], "SchemaNameCondition may only use equal or not_equal comparison"
        return compare(
            change.get_schema().config.schema_name,
            self.schema_name,
            self.comparison,
        )
