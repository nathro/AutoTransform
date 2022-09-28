# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's comments."""

from typing import ClassVar

from pydantic import validator

from autotransform.change.base import Change
from autotransform.step.action.base import Action, ActionName


class CommentAction(Action):
    """Adds a comment to an existing Change.

    Attributes:
        body(str): The body of the comment.
        name (ClassVar[ActionName]): The name of the component.
    """

    body: str

    name: ClassVar[ActionName] = ActionName.COMMENT

    # pylint: disable=invalid-name
    @validator("body")
    @classmethod
    def body_must_be_non_empty(cls, v: str) -> str:
        """Validates the body is not empty.

        Args:
            v (str): The body of the comment.

        Raises:
            ValueError: Raises an error when the body is empty.

        Returns:
            str: The unmodified body of the comment.
        """

        if v == "":
            raise ValueError("Comment body must be non-empty")
        return v

    def run(self, change: Change) -> bool:
        """Adds a comment to the specified Change.

        Args:
            change (Change): The Change to comment on.

        Returns:
            bool: Whether the comment was successful.
        """

        return change.comment(self.body)
