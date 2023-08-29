# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's labels."""

from typing import ClassVar, List

from autotransform.change.base import Change
from autotransform.step.action.base import Action, ActionName
from pydantic import validator


class AddLabelsAction(Action):
    """Adds labels to an existing Change.

    Attributes:
        labels(List[str]): The list of labels to add.
        name (ClassVar[ActionName]): The name of the component.
    """

    labels: List[str]

    name: ClassVar[ActionName] = ActionName.ADD_LABELS

    @validator("labels")
    @classmethod
    def labels_must_be_non_empty(cls, v: List[str]) -> List[str]:
        """Validates the labels are not empty.

        Args:
            v (List[str]): The labels to add to the Change.

        Raises:
            ValueError: Raises an error when the labels are empty.

        Returns:
            List[str]: The unmodified labels to add.
        """

        if not v:
            raise ValueError("At least 1 label must be provided")
        if any(label == "" for label in v):
            raise ValueError("Labels must be non-empty strings")
        return v

    def run(self, change: Change) -> bool:
        """Adds labels to the specified Change.

        Args:
            change (Change): The Change to add labels to.

        Returns:
            bool: Whether the labels were added successful.
        """

        return change.add_labels(self.labels)


class RemoveLabelAction(Action):
    """Removes a label from an existing Change.

    Attributes:
        label(str): The label to remove.
        name (ClassVar[ActionName]): The name of the component.
    """

    label: str

    name: ClassVar[ActionName] = ActionName.REMOVE_LABEL

    @validator("label")
    @classmethod
    def label_must_be_non_empty(cls, v: str) -> str:
        """Validates the label is not empty.

        Args:
            v (str): The label to remove.

        Raises:
            ValueError: Raises an error when the label is empty.

        Returns:
            str: The unmodified label of the comment.
        """

        if v == "":
            raise ValueError("Label to remove must be non-empty")
        return v

    def run(self, change: Change) -> bool:
        """Removes labels from the specified Change.

        Args:
            change (Change): The Change to remove labels from.

        Returns:
            bool: Whether the labels were removed successful.
        """

        return change.remove_label(self.label)
