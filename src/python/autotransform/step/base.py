# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Step components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.step.action import Action
from autotransform.util.component import NamedComponent, ComponentFactory, ComponentImport


class StepName(str, Enum):
    """A simple enum for mapping."""

    CONDITIONAL = "conditional"


class Step(NamedComponent):
    """The base for Step components. Used by AutoTransform to manage outstanding
    Changes, determining what actions to take.

    Attributes:
        name (ClassVar[StepName]): The name of the component.
    """

    name: ClassVar[StepName]

    @abstractmethod
    def get_action(self, change: Change) -> Action:
        """Checks the Change to determine what action should be taken. If no action is needed,
        an action with ActionType.NONE can be returned.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            Action: The Action the Step wants to take.
        """


FACTORY = ComponentFactory(
    {
        StepName.CONDITIONAL: ComponentImport(
            class_name="ConditionalStep", module="autotransform.step.conditional"
        ),
    },
    Step,  # type: ignore [misc]
    "step.json",
)
