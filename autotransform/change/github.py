# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GithubChange."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Mapping, TypedDict

from github.PullRequest import PullRequest

from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.change.state import ChangeState
from autotransform.change.type import ChangeType
from autotransform.repo.github import GithubRepo

if TYPE_CHECKING:
    from autotransform.schema.schema import AutoTransformSchema


class GithubChangeParams(TypedDict):
    """The param type for a GithubRepo."""

    full_github_name: str
    pull_request_number: int


class GithubChange(Change[GithubChangeParams]):
    """A Change representing a pull request on a Github repo.

    Attributes:
        _params (GithubChangeParams): The paramaters for the github change, including the
            pull request number and the full github name of the repo.
        _pull_request (PullRequest): The PullRequest object for the change.
    """

    _params: GithubChangeParams
    _pull_request: PullRequest

    def __init__(self, params: GithubChangeParams):
        """A simple constructor.

        Args:
            params (GithubChangeParams): The paramaters used to set up the GithubChange.
        """

        Change.__init__(self, params)
        self._pull_request = GithubRepo.get_github_repo(params["full_github_name"]).get_pull(
            params["pull_request_number"]
        )

    def get_params(self) -> GithubChangeParams:
        """Gets the paramaters used to set up the GithubChange.

        Returns:
            GithubChangeParams: The paramaters used to set up the GithubChange.
        """

        return self._params

    @staticmethod
    def get_type() -> ChangeType:
        """Used to map Change components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ChangeType: The unique type associated with this Change.
        """

        return ChangeType.GITHUB

    @abstractmethod
    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

    @abstractmethod
    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

    def get_state(self) -> ChangeState:
        """Gets the current state of the Change.

        Returns:
            ChangeState: The current state of the Change.
        """

        if self._pull_request.state == "closed":
            return ChangeState.CLOSED

        for review in self._pull_request.get_reviews():
            if review.state == "APPROVED":
                return ChangeState.ACCEPTED

        if self._pull_request.is_merged():
            return ChangeState.MERGED

    def merge(self) -> bool:
        """Merges an approved change in to main.

        Returns:
            bool: Whether the merge was completed successfully.
        """

        merge_status = self._pull_request.merge()
        return merge_status.merged

    @abstractmethod
    def abandon(self) -> bool:
        """Close out and abandon a Change, removing it from the code review
        and/or version control system.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Change:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Change: An instance of the Change.
        """
