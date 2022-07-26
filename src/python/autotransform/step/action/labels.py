# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's labels."""

from typing import ClassVar, List

from autotransform.step.action.base import Action, ActionName


class AddLabelsAction(Action):
    """Adds labels to an existing Change.

    Attributes:
        labels(List[str]): The list of labels to add.
        name (ClassVar[ActionName]): The name of the component.
    """

    labels: List[str]

    name: ClassVar[ActionName] = ActionName.ADD_LABELS


class RemoveLabelAction(Action):
    """Removes a label from an existing Change.

    Attributes:
        label(str): The label to remove.
        name (ClassVar[ActionName]): The name of the component.
    """

    label: str

    name: ClassVar[ActionName] = ActionName.REMOVE_LABEL
