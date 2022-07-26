# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's comments."""

from typing import ClassVar

from autotransform.step.action.base import Action, ActionName


class CommentAction(Action):
    """Adds a comment to an existing Change.

    Attributes:
        body(str): The body of the comment.
        name (ClassVar[ActionName]): The name of the component.
    """

    body: str

    name: ClassVar[ActionName] = ActionName.COMMENT
