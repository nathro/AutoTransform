# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's reviewers."""

from typing import ClassVar, List

from pydantic import Field

from autotransform.step.action.base import Action, ActionName


class AddReviewersAction(Action):
    """Adds reviewers to an existing Change.

    Attributes:
        reviewers(optional, List[str]): The list of reviewers to add. Defaults to [].
        team_reviewers(optional, List[str]): The list of team reviewers to add. Defaults to [].
        name (ClassVar[ActionName]): The name of the component.
    """

    reviewers: List[str] = Field(default_factory=list)
    team_reviewers: List[str] = Field(default_factory=list)

    name: ClassVar[ActionName] = ActionName.ADD_REVIEWERS
