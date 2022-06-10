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
from functools import cached_property
from typing import TYPE_CHECKING, ClassVar, Dict, List, Tuple

from autotransform.batcher.base import Batch
from autotransform.change.base import Change, ChangeName, ChangeState
from autotransform.item.base import FACTORY as item_factory
from autotransform.util.github import GithubUtils, PullRequest

if TYPE_CHECKING:
    from autotransform.schema.schema import AutoTransformSchema


class GithubChange(Change):
    """A Change representing a pull request on a Github repo.

    Attributes:
        full_github_name (str): The fully qualified name of the Github Repo the
            pull request is against.
        pull_number (int): The number for the pull request.
        name (ClassVar[ChangeName]): The name of the Component.
    """

    full_github_name: str
    pull_number: int
    name: ClassVar[ChangeName] = ChangeName.GITHUB

    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

        return self._body_data[1]

    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

        return self._body_data[0]

    def get_state(self) -> ChangeState:
        """Gets the current state of the Change. Caches the state in _state to prevent
        excessive use of Github API.

        Returns:
            ChangeState: The current state of the Change.
        """

        return self._state

    @cached_property
    def _state(self) -> ChangeState:
        """The current state of the Change as a cached property.

        Returns:
            ChangeState: The current state of the Change.
        """

        if self._pull_request.merged:
            return ChangeState.MERGED
        if self._pull_request.is_closed():
            return ChangeState.CLOSED
        review_state = self._pull_request.get_review_state()
        if review_state == "APPROVED":
            return ChangeState.APPROVED
        if review_state == "CHANGES_REQUESTED":
            return ChangeState.CHANGES_REQUESTED
        return ChangeState.OPEN

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

    @cached_property
    def _pull_request(self) -> PullRequest:
        """Gets the pull request as a cached property.

        Returns:
            PullRequest: The PullRequest.
        """

        return GithubUtils.get(self.full_github_name).get_pull_request(self.pull_number)

    @cached_property
    def _body_data(self) -> Tuple[AutoTransformSchema, Batch]:
        """Loads the Schema and Batch data for the GithubChange.

        Returns:
            Tuple[AutoTransformSchema, Batch]: The Schema and Batch contained
                in the PullRequest's Body.
        """

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

        schema = AutoTransformSchema.from_data(json.loads("\n".join(data["schema"])))
        batch = json.loads("\n".join(data["batch"]))
        items = [item_factory.get_instance(item) for item in batch["items"]]
        batch = {
            "items": items,
            "metadata": batch["metadata"],
            "title": str(batch["title"]),
        }
        return (schema, batch)
