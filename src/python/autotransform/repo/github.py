# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GithubRepo."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional, Sequence

from pydantic import Field

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.change.github import GithubChange
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.base import RepoName
from autotransform.repo.git import GitRepo
from autotransform.util.github import GithubUtils

if TYPE_CHECKING:
    from autotransform.schema.schema import AutoTransformSchema


class GithubRepo(GitRepo):
    """A Repo that provides support for submitting changes as a pull request against
    a Github repo.

    Attributes:
        full_github_name (str): The fully qualified name of the Github Repo.
        hide_automation_info (bool, optional): Whether to hide information on how automation was
            done from the pull request body. Defaults to False.
        hide_autotransform_docs (bool, optional): Whether to hide links to AutoTransform docs
            from the pull request body. Defaults to False.
        labels (List[str], optional): The labels to add to pull requests. Defaults to [].
        reviewers (List[str], optional): The reviewers to request for pull requests. Defaults to [].
        team_reviewers (List[str], optional): The team reviewers to request for pull requests.
            Defaults to [].
        name (ClassVar[RepoName]): The name of the component.
    """

    full_github_name: str
    hide_automation_info: bool = False
    hide_autotransform_docs: bool = False
    labels: List[str] = Field(default_factory=list)
    reviewers: List[str] = Field(default_factory=list)
    team_reviewers: List[str] = Field(default_factory=list)

    name: ClassVar[RepoName] = RepoName.GITHUB

    def has_outstanding_change(self, batch: Batch) -> bool:
        """Checks the state of the repo to see whether an outstanding Change
        for the Batch exists.

        Args:
            batch (Batch): The Batch to check for.

        Returns:
            bool: Whether an outstanding Change exists.
        """

        refs = self._local_repo.git.ls_remote(
            "--heads",
            self._local_repo.remote().name,
            GitRepo.get_branch_name(batch["title"]),
        )
        return refs != ""

    def submit(
        self,
        batch: Batch,
        _transform_data: Optional[Mapping[str, Any]],
        change: Optional[Change] = None,
    ) -> None:
        """Performs the normal submit for a git repo then submits a pull request
        against the provided Github repo.

        Args:
            batch (Batch): The Batch for which the changes were made.
            _transform_data (Optional[Mapping[str, Any]]): Data from the transformation. Unused.
            change (Optional[Change]): An associated change which should be updated.
                Defaults to None.
        """

        title = GitRepo.get_commit_message(batch["title"])
        batch_metadata = batch.get("metadata", {})

        self.commit(batch["title"], change is not None)

        commit_branch = GitRepo.get_branch_name(batch["title"])
        remote = self._local_repo.remote()
        if change is not None:
            self._local_repo.git.push(remote.name, "-u", "-f", commit_branch)
            return

        self._local_repo.git.push(remote.name, "-u", commit_branch)

        body = batch_metadata.get("body", None)
        assert body is not None, "All pull requests must have a body."

        if self.hide_automation_info:
            automation_info = ""
        else:
            automation_info = "\n\n" + self.get_automation_info(autotransform.schema.current, batch)

        pull_request = GithubUtils.get(self.full_github_name).create_pull_request(
            title,
            f"{str(body)}{automation_info}",
            self._base_branch.name,
            commit_branch,
        )

        EventHandler.get().handle(
            DebugEvent({"message": f"Pull request created: {pull_request.number}"})
        )

        # Add labels
        labels = batch_metadata.get("labels", [])
        labels.extend(self.labels)
        if labels:
            pull_request.add_labels(labels)

        # Request reviewers
        reviewers = batch_metadata.get("reviewers", [])
        reviewers.extend(self.reviewers)
        team_reviewers = batch_metadata.get("team_reviewers", [])
        team_reviewers.extend(self.team_reviewers)
        if reviewers or team_reviewers:
            pull_request.add_reviewers(reviewers, team_reviewers)

    def get_automation_info(self, schema: Optional[AutoTransformSchema], batch: Batch) -> str:
        """Gets information on automating with AutoTransform.

        Args:
            schema (Optional[AutoTransformSchema]): The Schema making the Change.
            batch (Batch): The Batch the Change is being made for.

        Returns:
            str: The text for automating.
        """

        # Create body content with information on replicating the change
        automation_info_lines = ["ADDED AUTOMATICALLY BY AUTOTRANSFORM"]
        if not self.hide_autotransform_docs:
            automation_info_lines.append(
                "Learn more about AutoTransform [here](https://autotransform.readthedocs.io)"
            )
        automation_info_lines.append("Schema and batch information for the change below")

        # Add schema JSON
        if schema is not None:
            automation_info_lines.extend(
                GithubRepo._get_encoded_json_lines(
                    "Schema",
                    schema.bundle(),
                    GithubUtils.BEGIN_SCHEMA,
                    GithubUtils.END_SCHEMA,
                )
            )

        # Add batch JSON
        encodable_batch: Dict[str, Any] = {
            "title": batch["title"],
            "items": [item.bundle() for item in batch["items"]],
        }
        if "metadata" in batch:
            encodable_batch["metadata"] = batch["metadata"]
        automation_info_lines.extend(
            GithubRepo._get_encoded_json_lines(
                "Batch", encodable_batch, GithubUtils.BEGIN_BATCH, GithubUtils.END_BATCH
            )
        )

        return "\n".join(automation_info_lines)

    @staticmethod
    def _get_encoded_json_lines(
        title: str, encodable_object: Any, begin_section: str, end_section: str
    ) -> List[str]:
        """Gets the details section for an encoded json object as a list of lines.

        Args:
            title (str): The title of the section.
            encodable_object (Any): The object to json encode.
            begin_section (str): The beginning of the encoded section.
            end_section (str): The end of the encoded section.

        Returns:
            List[str]: _description_
        """
        return [
            f"<details><summary>{title} JSON</summary>",
            "",
            "```",
            begin_section,
            json.dumps(encodable_object, indent=4),
            end_section,
            "```",
            "",
            "</details>",
        ]

    def get_outstanding_changes(self) -> Sequence[GithubChange]:
        """Gets all outstanding pull requests for the Repo.

        Returns:
            Sequence[GithubChange]: The outstanding Changes against the Repo.
        """

        pulls = GithubUtils.get(self.full_github_name).get_open_pull_requests(self.base_branch)
        authenticated_user_id = GithubUtils.get(self.full_github_name).get_user_id()
        return [
            GithubChange(
                full_github_name=self.full_github_name,
                pull_number=pull.number,
            )
            for pull in pulls
            if pull.owner_id == authenticated_user_id
        ]
