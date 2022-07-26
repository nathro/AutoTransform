# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with handling source control options for a Change."""

from typing import ClassVar

from autotransform.step.action.base import Action, ActionName


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
