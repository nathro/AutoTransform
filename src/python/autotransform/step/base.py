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
from typing import ClassVar, List

from autotransform.change.base import Change
from autotransform.step.action.base import Action
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


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
    def get_actions(self, change: Change) -> List[Action]:
        """Checks the Change to determine what actions should be taken. If no Actions
        are returned, the Step is considered skipped.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            List[Action]: The Actions the Step wants to take.
        """

    @abstractmethod
    def continue_management(self, change: Change) -> bool:
        """Checks if management should be continued after this Step when Actions were provided.

        Args:
            change (Change): The Change the Step is running against.

        Returns:
            bool: Whether to continue management.
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
