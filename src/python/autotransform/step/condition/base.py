# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Condition components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, ClassVar, Dict, Generic, List, Optional, Set, Type, TypeVar

from pydantic import root_validator, validator

from autotransform.change.base import Change
from autotransform.step.condition.comparison import ComparisonType, compare
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class ConditionName(str, Enum):
    """A simple enum for mapping."""

    AGGREGATE = "aggregate"
    CHANGE_STATE = "change_state"
    CREATED_AGO = "created_ago"
    LABELS = "labels"
    REVIEWERS = "reviewers"
    SCHEMA_NAME = "schema_name"
    TEAM_REVIEWERS = "team_reviewers"
    UPDATED_AGO = "updated_ago"


class Condition(NamedComponent):
    """The base for Condition components. Used by ConditionalStep to determine whether to
    take an Action.

    Attributes:
        name (ClassVar[ConditionName]): The name of the Component.
    """

    name: ClassVar[ConditionName]

    @abstractmethod
    def check(self, change: Change) -> bool:
        """Checks whether the Change passes the Condition.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the condition.
        """


T = TypeVar("T")


class ComparisonCondition(Generic[T], Condition):
    """The base for comparison Condition components. Uses the ComparisonType enum to perform
    comparisons.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (T): The value to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: T

    name: ClassVar[ConditionName]

    @abstractmethod
    def get_val_from_change(self, change: Change) -> T:
        """Gets the existing value to compare against from the change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            T: The value from the Change to compare against.
        """

    def check(self, change: Change) -> bool:
        """Checks whether the Change passes the Condition.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the condition.
        """

        return compare(self.get_val_from_change(change), self.value, self.comparison)

    @staticmethod
    def valid_comparisons() -> Set[ComparisonType]:
        """Gets the valid comparisons that can be done for this condition.

        Returns:
            Set[ComparisonType]: The valid comparisons this condition can perform.
        """

        return {ComparisonType.EQUAL, ComparisonType.NOT_EQUAL}

    # pylint: disable=invalid-name
    @validator("comparison")
    @classmethod
    def comparison_type_is_valid(
        cls: Type[ComparisonCondition], v: ComparisonType
    ) -> ComparisonType:
        """Validates the condition can perform the specified comparison.

        Args:
            cls (Type[ComparisonCondition]): The Condition class.
            v (ComparisonType): The comparison to perform.

        Raises:
            ValueError: Raised if the Condition can not perform the comparison.

        Returns:
            ComparisonType: The unmodified comparison to perform.
        """

        if v not in cls.valid_comparisons():
            raise ValueError(f"{cls.__name__} can not perform comparison {v}")
        return v


class SortableComparisonCondition(ABC, Generic[T], ComparisonCondition[T]):
    """The base for sortable comparison Condition components. Uses the ComparisonType enum to
    perform comparisons that are sortable.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (T): The value to compare against.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    @staticmethod
    def valid_comparisons() -> Set[ComparisonType]:
        """Gets the valid comparisons that can be done for this condition.

        Returns:
            Set[ComparisonType]: The valid comparisons this condition can perform.
        """

        return {
            ComparisonType.EQUAL,
            ComparisonType.NOT_EQUAL,
            ComparisonType.GREATER_THAN,
            ComparisonType.GREATER_THAN_OR_EQUAL,
            ComparisonType.LESS_THAN,
            ComparisonType.LESS_THAN_OR_EQUAL,
        }


class ListComparisonCondition(Generic[T], Condition):
    """The base for sortable comparison Condition components. Uses the ComparisonType enum to
    perform comparisons that are sortable.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        value (optional, Optional[T]): The value to compare against. Defaults to None.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    value: Optional[T] = None

    name: ClassVar[ConditionName]

    @abstractmethod
    def get_val_from_change(self, change: Change) -> List[T]:
        """Gets the existing value to compare against from the change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            List[T]: The value from the Change to compare against.
        """

    def check(self, change: Change) -> bool:
        """Checks whether the Change passes the Condition.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            bool: Whether the Change passes the condition.
        """

        return compare(self.get_val_from_change(change), self.value, self.comparison)

    @root_validator
    @classmethod
    def check_value_for_comparison(
        cls: Type[ListComparisonCondition], values: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ensures that the value is provided for contains/not contains checks
        or not provided for empty/not empty checks.

        Args:
            cls (Type[ListComparisonCondition]): The Condition class.
            values (Dict[str, Any]): The values for the comparison.

        Raises:
            ValueError: Raises errors when values are provided for an empty check
                or not provided for a contains check.

        Returns:
            Dict[str, Any]: The unmodified values for comparison.
        """

        comparison = values["comparison"]
        if (
            comparison in [ComparisonType.EMPTY, ComparisonType.NOT_EMPTY]
            and values.get("value") is not None
        ):
            raise ValueError(f"Can not perform comparison {comparison} when value is not None.")
        if (
            comparison in [ComparisonType.CONTAINS, ComparisonType.NOT_CONTAINS]
            and values.get("value") is None
        ):
            raise ValueError(f"Can not perform comparison {comparison} when value is None.")

        return values

    @staticmethod
    def valid_comparisons() -> Set[ComparisonType]:
        """Gets the valid comparisons that can be done for this condition.

        Returns:
            Set[ComparisonType]: The valid comparisons this condition can perform.
        """

        return {
            ComparisonType.CONTAINS,
            ComparisonType.NOT_CONTAINS,
            ComparisonType.EMPTY,
            ComparisonType.NOT_EMPTY,
        }

    # pylint: disable=invalid-name
    @validator("comparison")
    @classmethod
    def comparison_type_is_valid(
        cls: Type[ListComparisonCondition], v: ComparisonType
    ) -> ComparisonType:
        """Validates the condition can perform the specified comparison.

        Args:
            cls (Type[ListComparisonCondition]): The Condition class.
            v (ComparisonType): The comparison to perform.

        Raises:
            ValueError: Raised if the Condition can not perform the comparison.

        Returns:
            ComparisonType: The unmodified comparison to perform.
        """

        if v not in cls.valid_comparisons():
            raise ValueError(f"{cls.__name__} can not perform comparison {v}")
        return v


FACTORY = ComponentFactory(
    {
        ConditionName.AGGREGATE: ComponentImport(
            class_name="AggregateCondition", module="autotransform.step.condition.aggregate"
        ),
        ConditionName.CHANGE_STATE: ComponentImport(
            class_name="ChangeStateCondition", module="autotransform.step.condition.state"
        ),
        ConditionName.CREATED_AGO: ComponentImport(
            class_name="CreatedAgoCondition", module="autotransform.step.condition.created"
        ),
        ConditionName.LABELS: ComponentImport(
            class_name="LabelsCondition", module="autotransform.step.condition.labels"
        ),
        ConditionName.REVIEWERS: ComponentImport(
            class_name="ReviewersCondition", module="autotransform.step.condition.reviewers"
        ),
        ConditionName.SCHEMA_NAME: ComponentImport(
            class_name="SchemaNameCondition", module="autotransform.step.condition.schema"
        ),
        ConditionName.TEAM_REVIEWERS: ComponentImport(
            class_name="TeamReviewersCondition", module="autotransform.step.condition.reviewers"
        ),
        ConditionName.UPDATED_AGO: ComponentImport(
            class_name="UpdatedAgoCondition", module="autotransform.step.condition.updated"
        ),
    },
    Condition,  # type: ignore [misc]
    "condition.json",
)
