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
import re
from functools import cached_property
from typing import ClassVar, Dict, List, Tuple

from autotransform.batcher.base import Batch
from autotransform.change.base import Change, ChangeName, ChangeState, ReviewState, TestState
from autotransform.config import get_config
from autotransform.item.base import FACTORY as item_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.github import GithubUtils, PullRequest
from autotransform.util.schema_map import SchemaMap


class GithubChange(Change):
    """A Change representing a Pull Request on a Github repo.

    Attributes:
        full_github_name (str): The fully qualified name of the Github Repo the
            Pull Request is against.
        pull_number (int): The number for the Pull Request.
        name (ClassVar[ChangeName]): The name of the Component.
    """

    full_github_name: str
    pull_number: int
    name: ClassVar[ChangeName] = ChangeName.GITHUB

    @cached_property
    def _pull_request(self) -> PullRequest:
        """Gets the Pull Request.

        Returns:
            PullRequest: The Pull Request.
        """

        return GithubUtils.get(self.full_github_name).get_pull_request(self.pull_number)

    @cached_property
    def _automation_data(self) -> Tuple[AutoTransformSchema, Batch]:
        """Loads the Schema and Batch data for the GithubChange as a cached property.

        Returns:
            Tuple[AutoTransformSchema, Batch]: The Schema and Batch contained
                in the PullRequest's Body.
        """

        gist_match = re.search("<<<Automation Info Gist: (.*)>>>", self._pull_request.body)
        if gist_match:
            gist_ids = gist_match.groups()[0].split("/")
            gist = GithubUtils.get(self.full_github_name).get_gist(gist_ids[0])
            schema_data = gist.get_file_content("schema") or ""
            batch = json.loads(gist.get_file_content("batch") or "")
            assert isinstance(batch["items"], List)
            for i in range(1, len(gist_ids)):
                gist = GithubUtils.get(self.full_github_name).get_gist(gist_ids[i])
                items = json.loads(gist.get_file_content("items") or "[]")
                assert isinstance(items, List)
                batch["items"].extend(items)
        else:
            cur_line_placement = None
            data_lines: Dict[str, List[str]] = {"schema": [], "batch": []}
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
                    data_lines[cur_line_placement].append(line)
            schema_data = "\n".join(data_lines["schema"])
            batch = json.loads("\n".join(data_lines["batch"]))

        schema = AutoTransformSchema.from_data(json.loads(schema_data))
        items = [item_factory.get_instance(item) for item in batch["items"]]
        batch = {
            "items": items,
            "metadata": batch["metadata"],
            "title": str(batch["title"]),
        }
        return (schema, batch)

    def get_batch(self) -> Batch:
        """Gets the Batch that was used to produce the Change.

        Returns:
            Batch: The Batch used to produce the Change.
        """

        return self._automation_data[1]

    def get_schema(self) -> AutoTransformSchema:
        """Gets the Schema that was used to produce the Change.

        Returns:
            AutoTransformSchema: The Schema used to produce the Change.
        """

        schema_name = self.get_schema_name()
        schema = SchemaMap.get().get_schema(schema_name)
        assert schema_name == schema.config.schema_name
        repo_override = get_config().repo_override
        if repo_override is not None:
            schema.repo = repo_override

        return schema

    def get_schema_name(self) -> str:
        """Gets the name of the Schema that produced the Change.

        Returns:
            str: The name of the Schema.
        """

        return self._automation_data[0].config.schema_name

    def get_state(self) -> ChangeState:
        """Gets the current state of the Change.

        Returns:
            ChangeState: The current state of the Change.
        """

        if self._pull_request.merged:
            return ChangeState.MERGED
        if self._pull_request.is_closed():
            return ChangeState.CLOSED
        return ChangeState.OPEN

    def get_mergeable_state(self) -> str:
        """Gets the mergeable state of the Change.

        Returns:
            ChangeState: The mergeable state of the Change.
        """

        return self._pull_request.get_mergeable_state()

    @cached_property
    def _review_state(self) -> ReviewState:
        """The current review state of the Change as a cached property.

        Returns:
            ReviewState: The current review state of the Change.
        """

        review_state = self._pull_request.get_review_state()
        if review_state == "APPROVED":
            return ReviewState.APPROVED
        if review_state == "CHANGES_REQUESTED":
            return ReviewState.CHANGES_REQUESTED
        return ReviewState.NEEDS_REVIEW

    def get_review_state(self) -> ReviewState:
        """Gets the current review state of the Change.

        Returns:
            ReviewState: The current review state of the Change.
        """

        return self._review_state

    @cached_property
    def _test_state(self) -> TestState:
        """The current test state of the Change as a cached property.

        Returns:
            TestState: The current test state of the Change.
        """

        state = self._pull_request.get_test_state()
        if state == "pending":
            return TestState.PENDING
        if state in ["success", "neutral"]:
            return TestState.SUCCESS
        return TestState.FAILURE

    def get_test_state(self) -> TestState:
        """Gets the current test state of the Change.

        Returns:
            TestState: The current test state of the Change.
        """

        return self._test_state

    def get_labels(self) -> List[str]:
        """Gets all labels for a Change.

        Returns:
            List[str]: The list of labels.
        """

        return self._pull_request.get_labels()

    def get_reviewers(self) -> List[str]:
        """Gets all reviewers for a Change.

        Returns:
            List[str]: The list of reviewers.
        """

        return self._pull_request.get_reviewers()

    def get_team_reviewers(self) -> List[str]:
        """Gets all team reviewers for a Change.

        Returns:
            List[str]: The list of team reviewers.
        """

        return self._pull_request.get_team_reviewers()

    def get_created_timestamp(self) -> int:
        """Returns the timestamp when the Pull Request was created.

        Returns:
            int: The timestamp in seconds when the Pull Request was created.
        """

        return self._pull_request.get_created_at()

    def get_last_updated_timestamp(self) -> int:
        """Returns the timestamp when the Pull Request was last updated.

        Returns:
            int: The timestamp in seconds when the Pull Request was last updated.
        """

        return self._pull_request.get_updated_at()

    def abandon(self) -> bool:
        """Close the Pull Request and delete the associated branch.

        Returns:
            bool: Whether the abandon was completed successfully.
        """

        return self._pull_request.close() and self._pull_request.delete_branch()

    def add_labels(self, labels: List[str]) -> bool:
        """Adds labels to an outstanding Change.

        Args:
            labels (List[str]): The labels to add.

        Returns:
            bool: Whether the labels were added successfully.
        """

        self._pull_request.add_labels(labels)
        return True

    def add_reviewers(self, reviewers: List[str], team_reviewers: List[str]) -> bool:
        """Adds reviewers to an outstanding Change.

        Args:
            reviewers (List[str]): The reviewers to add.
            team_reviewers (List[str]): Any team reviewers to add.

        Returns:
            bool: Whether the reviewers were added successfully.
        """

        self._pull_request.add_reviewers(reviewers, team_reviewers)
        return True

    def comment(self, body: str) -> bool:
        """Comments on an outstanding Change.

        Args:
            body (str): The body of the comment.

        Returns:
            bool: Whether the comment was successful.
        """

        self._pull_request.create_comment(body)
        return True

    def merge(self) -> bool:
        """Merges the Pull Request and deletes the branch.

        Returns:
            bool: Whether the merge was completed successfully.
        """

        return self._pull_request.merge() and self._pull_request.delete_branch()

    def remove_label(self, label: str) -> bool:
        """Removes a label from an outstanding Change.

        Args:
            label (str): The label to remove.

        Returns:
            bool: Whether the label was removed successfully.
        """

        self._pull_request.remove_label(label)
        return True
