# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GithubChange."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict, List, Mapping, TypedDict

from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.change.state import ChangeState
from autotransform.change.type import ChangeType
from autotransform.item.factory import ItemFactory
from autotransform.util.github import GithubUtils, PullRequest

if TYPE_CHECKING:
    from autotransform.schema.schema import AutoTransformSchema


class GithubChangeParams(TypedDict):
    """The param type for a GithubChange."""

    full_github_name: str
    pull_number: int


class GithubChange(Change[GithubChangeParams]):
    """A Change representing a pull request on a Github repo.

    Attributes:
        _params (GithubChangeParams): The paramaters for the github change, including the
            pull request number and the full github name of the repo.
        _pull_request (PullRequest): The PullRequest object for the change.
        _state (Optional[ChangeState]): The cached state of the Change. Used to prevent excessive
            Github API requests.
    """

    _params: GithubChangeParams
    _pull_request: PullRequest
    _state: ChangeState
    _batch: Batch
    _schema: AutoTransformSchema

    def __init__(self, params: GithubChangeParams):
        """A simple constructor.

        Args:
            params (GithubChangeParams): The paramaters used to set up the GithubChange.
        """

        Change.__init__(self, params)
        self._pull_request = GithubUtils.get(self._params["full_github_name"]).get_pull_request(
            params["pull_number"]
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

    def _load_data(self) -> None:
        """Loads the Schema and Batch data for the GithubChange."""

        # pylint: disable=import-outside-toplevel
        from autotransform.schema.schema import AutoTransformSchema

        data: Dict[str, List[str]] = {"schema": [], "batch": []}
        cur_line_placement = None
        for line in self._pull_request.body.splitlines():
            if line == GithubUtils.BEGIN_SCHEMA:
                cur_line_placement = "schema"
            elif line == GithubUtils.END_SCHEMA:
                cur_line_placement = None
            elif line == GithubUtils.BEGIN_BATCH:
                cur_line_placement = "batch"
            elif line == GithubUtils.END_BATCH:
                cur_line_placement = None
            elif cur_line_placement is not None:
                data[cur_line_placement].append(line)

        self._schema = AutoTransformSchema.from_json("\n".join(data["schema"]))
        batch = json.loads("\n".join(data["batch"]))
        items = [ItemFactory.get(item) for item in batch["items"]]
        self._batch = {
            "items": items,
            "metadata": batch["metadata"],
            "title": str(batch["title"]),
        }

    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

        if not hasattr(self, "_batch"):
            self._load_data()

        return self._batch

    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

        if not hasattr(self, "_schema"):
            self._load_data()
        return self._schema

    def get_state(self) -> ChangeState:
        """Gets the current state of the Change. Caches the state in _state to prevent
        excessive use of Github API.

        Returns:
            ChangeState: The current state of the Change.
        """
        if not hasattr(self, "_state"):
            if self._pull_request.merged:
                self._state = ChangeState.MERGED
            elif self._pull_request.is_closed():
                self._state = ChangeState.CLOSED
            else:
                review_state = self._pull_request.get_review_state()
                if review_state == "APPROVED":
                    self._state = ChangeState.APPROVED
                elif review_state == "CHANGES_REQUESTED":
                    self._state = ChangeState.CHANGES_REQUESTED
        if not hasattr(self, "_state"):
            self._state = ChangeState.OPEN
        return self._state

    def get_created_timestamp(self) -> int:
        """Returns the timestamp when the pull request was created.

        Returns:
            int: The timestamp in seconds when the pull request was created.
        """

        return self._pull_request.get_created_at()

    def get_last_updated_timestamp(self) -> int:
        """Returns the timestamp when the pull request was last updated.

        Returns:
            int: The timestamp in seconds when the pull request was last updated.
        """

        return self._pull_request.get_updated_at()

    def _merge(self) -> bool:
        """Merges the pull request and deletes the branch.

        Returns:
            bool: Whether the merge was completed successfully.
        """

        merged = self._pull_request.merge()
        if not merged:
            return False
        return self._pull_request.delete_branch()

    def abandon(self) -> bool:
        """Close the pull request and delete the associated branch.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

        closed = self._pull_request.close()
        if not closed:
            return False
        return self._pull_request.delete_branch()

    def __str__(self) -> str:
        return f"Pull Request #{self._params['pull_number']}"

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GithubChange:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            GithubChange: An instance of the GithubChange.
        """

        full_github_name = data["full_github_name"]
        assert isinstance(full_github_name, str)
        pull_number = data["pull_number"]
        assert isinstance(pull_number, int)

        return GithubChange({"full_github_name": full_github_name, "pull_number": pull_number})
