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
from copy import deepcopy
from typing import TYPE_CHECKING, Any, ClassVar, Dict, List, Mapping, Optional, Sequence

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.change.github import GithubChange
from autotransform.event.github import GithubPullRequestCreatedEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.base import RepoName
from autotransform.repo.git import GitRepo
from autotransform.util.github import GithubUtils
from pydantic import BaseModel  # pylint: disable=no-name-in-module
from pydantic import Field

if TYPE_CHECKING:
    from autotransform.schema.schema import AutoTransformSchema


# pylint: disable=too-few-public-methods
class GithubRepoBatchMetadata(BaseModel):
    """The metadata used by GithubRepo.

    Attributes:
        body (str): The body of the Pull Request to make.
        labels(optional, List[str]): The labels to add to the Pull Request. Defaults to [].
        reviewers(optional, List[str]): The reviewers to request for the Pull Request.
            Defaults to [].
        team_reviewers(optional, List[str]): The team reviewers to request for the Pull Request.
            Defaults to [].
    """

    body: str
    labels: List[str] = Field(default_factory=list)
    reviewers: List[str] = Field(default_factory=list)
    team_reviewers: List[str] = Field(default_factory=list)


class GithubRepo(GitRepo):
    """A Repo that provides support for submitting changes as a pull request against
    a Github repo.

    Attributes:
        full_github_name (str): The fully qualified name of the Github Repo.
        commit_repo (optional, Optional[str]): The repo from which to generate a Pull Request. Used
            if creating a Pull Request from a fork. Defaults to None.
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

    commit_repo: Optional[str] = None
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
        batch_metadata = GithubRepoBatchMetadata.parse_obj(batch.get("metadata", {}))

        self.commit(batch["title"], change is not None)

        commit_branch = GitRepo.get_branch_name(batch["title"])
        remote = self._local_repo.remote()
        if change is not None:
            self._local_repo.git.push(remote.name, "-u", "-f", commit_branch)
            return

        self._local_repo.git.push(remote.name, "-u", commit_branch)

        if self.hide_automation_info:
            automation_info = ""
        else:
            automation_info = "\n\n" + self.get_automation_info(autotransform.schema.current, batch)

        if self.commit_repo is not None:
            head = f"{self.commit_repo}:"
        else:
            head = ""

        pull_request = GithubUtils.get(self.full_github_name).create_pull_request(
            title,
            f"{str(batch_metadata.body)}{automation_info}",
            self._base_branch.name,
            f"{head}{commit_branch}",
        )

        EventHandler.get().handle(GithubPullRequestCreatedEvent({"pull": pull_request}))

        # Add labels
        labels = deepcopy(batch_metadata.labels)
        labels.extend(self.labels)
        if labels:
            pull_request.add_labels(labels)

        # Request reviewers
        reviewers = deepcopy(batch_metadata.reviewers)
        reviewers.extend(self.reviewers)
        team_reviewers = deepcopy(batch_metadata.team_reviewers)
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

        files = {}
        # Add schema JSON
        if schema is not None:
            files["schema"] = {"content": json.dumps(schema.bundle(), indent=4)}

        # Add batch JSON
        chunk_size = 5000
        items = batch["items"]
        item_chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
        if not item_chunks:
            item_chunks = [[]]
        encodable_batch: Dict[str, Any] = {
            "title": batch["title"],
            "items": [item.bundle() for item in item_chunks[0]],
        }
        if "metadata" in batch:
            encodable_batch["metadata"] = batch["metadata"]
        files["batch"] = {"content": json.dumps(encodable_batch, indent=4)}
        gists = [
            GithubUtils.get(self.full_github_name).create_gist(
                files, description="Automation info for AutoTransform", public=True
            )
        ]
        for i in range(1, len(item_chunks)):
            item_file = {
                "items": {
                    "content": json.dumps([item.bundle() for item in item_chunks[i]], indent=4)
                }
            }
            gists.append(
                GithubUtils.get(self.full_github_name).create_gist(
                    item_file, description="Automation info for AutoTransform", public=True
                )
            )
        automation_info_lines.append(
            f"<<<Automation Info Gist: {'/'.join([gist.gist_id for gist in gists])}>>>"
        )

        return "\n".join(automation_info_lines)

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
