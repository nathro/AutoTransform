# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Change components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.util.component import NamedComponent, ComponentFactory, ComponentImport


class ConditionName(str, Enum):
    """A simple enum for mapping."""

    AGGREGATE = "aggregate"
    CHANGE_STATE = "change_state"
    CREATED_AGO = "created_ago"
    SCHEMA_NAME = "schema_name"
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
        ConditionName.SCHEMA_NAME: ComponentImport(
            class_name="SchemaNameCondition", module="autotransform.step.condition.schema"
        ),
        ConditionName.UPDATED_AGO: ComponentImport(
            class_name="UpdatedAgoCondition", module="autotransform.step.condition.updated"
        ),
    },
    Condition,  # type: ignore [misc]
    "condition.json",
)
