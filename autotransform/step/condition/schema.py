# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the SchemaNameCondition."""

from __future__ import annotations

from typing import Any, Mapping, TypedDict

from autotransform.change.base import Change
from autotransform.step.condition.base import Condition
from autotransform.step.condition.comparison import ComparisonType, compare
from autotransform.step.condition.type import ConditionType


class SchemaNameConditionParams(TypedDict):
    """The param type for a SchemaNameCondition."""

    comparison: ComparisonType
    name: str


class SchemaNameCondition(Condition[SchemaNameConditionParams]):
    """A condition which checks the name of the Schema that produced a change against the supplied
    name, using the supplied comparison. Note: only equals and not equals are valid, all others will
    result in an error.

    Attributes:
        _params (TParams): The comparison type and name to compare against.
    """

    _params: SchemaNameConditionParams

    @staticmethod
    def get_type() -> ConditionType:
        """Used to map Condition components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ConditionType: The unique type associated with this Condition.
        """

        return ConditionType.SCHEMA_NAME

    def check(self, change: Change) -> bool:
        """Checks whether the the schema name passes the comparison.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the Condition.
        """
        comparison = self._params["comparison"]
        assert comparison in [
            ComparisonType.EQUAL,
            ComparisonType.NOT_EQUAL,
        ], "SchemaNameCondition may only use equal or not_equal comparison"
        return compare(
            change.get_schema().get_config().get_name(),
            self._params["name"],
            self._params["comparison"],
        )

    def __str__(self) -> str:
        return f"Schema Name {self._params['comparison'].name.lower()} {self._params['name']}"

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> SchemaNameCondition:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            SchemaNameCondition: An instance of the SchemaNameCondition.
        """

        comparison = data["comparison"]
        if not ComparisonType.has_value(comparison):
            comparison = ComparisonType.from_name(comparison)
        else:
            comparison = ComparisonType.from_value(comparison)

        name = data["name"]
        assert isinstance(name, str)

        return SchemaNameCondition({"comparison": comparison, "name": name})
