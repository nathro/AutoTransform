# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Action components."""

from enum import Enum
from typing import ClassVar

from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class ActionName(str, Enum):
    """A simple enum for mapping."""

    ABANDON = "abandon"
    ADD_REVIEWERS = "add_reviewers"
    MERGE = "merge"
    NONE = "none"
    UPDATE = "update"


class Action(NamedComponent):
    """The base for Action components. Used by AutoTransform to perform some task on
    outstanding Changes based on Steps in the Manager. Tasks include options such as
    updating, abandoning, merging, and more.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName]


class AbandonAction(Action):
    """Abandons an outstanding Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.ABANDON


class MergeAction(Action):
    """Merges an outstanding Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.MERGE


class NoneAction(Action):
    """Performs no task.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.NONE


class UpdateAction(Action):
    """Updates an outstanding Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.UPDATE


FACTORY = ComponentFactory(
    {
        ActionName.ABANDON: ComponentImport(
            class_name="AbandonAction", module="autotransform.step.action.base"
        ),
        ActionName.ADD_REVIEWERS: ComponentImport(
            class_name="AddReviewersAction", module="autotransform.step.action.reviewers"
        ),
        ActionName.MERGE: ComponentImport(
            class_name="MergeAction", module="autotransform.step.action.base"
        ),
        ActionName.NONE: ComponentImport(
            class_name="NoneAction", module="autotransform.step.action.base"
        ),
        ActionName.UPDATE: ComponentImport(
            class_name="UpdateAction", module="autotransform.step.action.base"
        ),
    },
    Action,  # type: ignore [misc]
    "action.json",
)
