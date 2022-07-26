# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""All Actions associated with a Change's reviewers."""

from typing import Any, ClassVar, Dict, List

from pydantic import Field, root_validator, validator

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

    # pylint: disable=invalid-name
    @validator("reviewers")
    @classmethod
    def labels_must_be_non_empty(cls, v: List[str]) -> List[str]:
        """Validates the reviewers are not empty strings.

        Args:
            v (List[str]): The reviewers to add to the Change.

        Raises:
            ValueError: Raises an error if a reviewer is an empty string.

        Returns:
            List[str]: The unmodified reviewers to add.
        """

        if any(reviewer == "" for reviewer in v):
            raise ValueError("Reviewers must be non-empty strings")
        return v

    # pylint: disable=invalid-name
    @validator("team_reviewers")
    @classmethod
    def team_reviewers_must_be_non_empty(cls, v: List[str]) -> List[str]:
        """Validates the team reviewers are not empty strings.

        Args:
            v (List[str]): The team reviewers to add to the Change.

        Raises:
            ValueError: Raises an error if a team reviewer is an empty string.

        Returns:
            List[str]: The unmodified team reviewers to add.
        """

        if any(team_reviewer == "" for team_reviewer in v):
            raise ValueError("Team reviewers must be non-empty strings")
        return v

    @root_validator
    @classmethod
    def some_reviewers_must_be_provided(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Checks that either reviewers or team reviewers are supplied.

        Args:
            values (Dict[str, Any]): The values for the action.

        Raises:
            ValueError: Raises an error if neither reviewers nor team reviewers are supplied.

        Returns:
            Dict[str, Any]: The unmodified values.
        """

        reviewers, team_reviewers = values.get("reviewers"), values.get("team_reviewers")
        if not reviewers and not team_reviewers:
            raise ValueError("Either reviewers or team reviewers must be supplied")
        return values


class AddOwnersAsReviewersAction(Action):
    """Adds the owners of a Schema as reviewers for the Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.ADD_OWNERS_AS_REVIEWERS


class AddOwnersAsTeamReviewersAction(Action):
    """Adds the owners of a Schema as team reviewers for the Change.

    Attributes:
        name (ClassVar[ActionName]): The name of the component.
    """

    name: ClassVar[ActionName] = ActionName.ADD_OWNERS_AS_TEAM_REVIEWERS
