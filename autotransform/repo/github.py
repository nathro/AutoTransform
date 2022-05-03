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
from typing import Any, Dict, List, Mapping, Optional, Sequence

from github import Github, Repository
from typing_extensions import NotRequired

import autotransform.change.github as github_change
import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.config import fetcher as Config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.git import GitRepo, GitRepoParams
from autotransform.repo.type import RepoType


class GithubRepoParams(GitRepoParams):
    """The param type for a GithubRepo."""

    full_github_name: str
    required_labels: NotRequired[List[str]]
    hide_automation_info: NotRequired[bool]
    hide_autotransform_docs: NotRequired[bool]


class GithubRepo(GitRepo):
    """A Repo that provides support for submitting changes as a pull request against
    a Github repo.

    Attributes:
        _params (GithubRepoParams): Contains all git params as well as the Github repo
            name and any required labels.
        __github_repos (Dict[str, Repository.Repository]): A mapping of repo names to repos. Used
            for caching.
        __github_object (Optional[Github]): An instance of the Github object of PyGithub.
    """

    _params: GithubRepoParams
    __github_repos: Dict[str, Repository.Repository] = {}
    __github_object: Optional[Github] = None

    BEGIN_SCHEMA: str = "<<<<BEGIN SCHEMA>>>>"
    END_SCHEMA: str = "<<<<END SCHEMA>>>>"

    BEGIN_BATCH: str = "<<<<BEGIN BATCH>>>>"
    END_BATCH: str = "<<<<END BATCH>>>>"

    def __init__(self, params: GithubRepoParams):
        """Establishes the Github object to enable API access.

        Args:
            params (GithubRepoParams): The paramaters used to set up the GithubRepo.
        """

        GitRepo.__init__(self, params)

    @staticmethod
    def get_github_object() -> Github:
        """Authenticates with Github to allow API access via a token provided by AutoTransform
        configuration. If no token is provided a username + password will be used. Also allows
        use of a base URL for enterprise use cases. Stores the Github object for future use.

        Returns:
            Github: An object allowing interaction with the Github API.
        """

        if GithubRepo.__github_object is None:
            url = Config.get_credentials_github_base_url()
            token = Config.get_credentials_github_token()
            if token is not None:
                if url is not None:
                    GithubRepo.__github_object = Github(token, base_url=url)
                GithubRepo.__github_object = Github(token)
            elif url is not None:
                GithubRepo.__github_object = Github(
                    Config.get_credentials_github_username(),
                    Config.get_credentials_github_password(),
                    base_url=url,
                )
            else:
                GithubRepo.__github_object = Github(
                    Config.get_credentials_github_username(),
                    Config.get_credentials_github_password(),
                )
        return GithubRepo.__github_object

    @staticmethod
    def get_github_repo(repo_name: str) -> Repository.Repository:
        """Gets the Github repository being interacted with.

        Returns:
            Repository.Repository: The Github repository being interacted with.
        """

        if repo_name not in GithubRepo.__github_repos:
            GithubRepo.__github_repos[repo_name] = GithubRepo.get_github_object().get_repo(
                repo_name,
            )
        return GithubRepo.__github_repos[repo_name]

    @staticmethod
    def get_type() -> RepoType:
        """Used to map Repo components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RepoType: The unique type associated with this Repo
        """

        return RepoType.GITHUB

    def submit(self, batch: Batch) -> None:
        """Performs the normal submit for a git repo then submits a pull request
        against the provided Github repo.

        Args:
            batch (Batch): The Batch for which the changes were made.
        """

        title = GitRepo.get_commit_message(batch["title"])

        self.commit(batch["title"])

        commit_branch = GitRepo.get_branch_name(batch["title"])
        remote = self._local_repo.remote()
        self._local_repo.git.push(remote.name, "-u", commit_branch)

        body = batch["metadata"].get("body", None)

        if self._params.get("hide_automation_info", False):
            automation_info = ""
        else:
            automation_info = "\n\n" + self.get_automation_info(batch)

        assert body is not None, "All pull requests must have a body."
        pull_request = GithubRepo.get_github_repo(self._params["full_github_name"]).create_pull(
            title=title,
            body=f"{str(body)}{automation_info}",
            base=self._base_branch.name,
            head=commit_branch,
        )

        EventHandler.get().handle(
            DebugEvent({"message": f"Pull request created: {pull_request.number}"})
        )

        # Add labels
        labels = batch["metadata"].get("labels", [])
        assert isinstance(labels, List)
        labels = labels + self._params.get("required_labels", [])
        if len(labels) > 0:
            pull_request.add_to_labels(*labels)

    def get_automation_info(self, batch: Batch) -> str:
        """Gets information on automating with AutoTransform.

        Args:
            batch (Batch): The Batch the change is being made for.

        Returns:
            str: The text for automating.
        """

        # Create body content with information on replicating the change
        automation_info_lines = ["ADDED AUTOMATICALLY BY AUTOTRANSFORM"]
        if not self._params.get("hide_autotransform_docs", False):
            automation_info_lines.append(
                "Learn more about AutoTransform [here](https://autotransform.readthedocs.io)"
            )
        automation_info_lines.append("Schema and batch information for the change below")

        # Add schema JSON
        current_schema = autotransform.schema.current
        if current_schema is not None:
            automation_info_lines.append("<details><summary>Schema JSON</summary>")
            automation_info_lines.append("")
            automation_info_lines.append("```")
            automation_info_lines.append(GithubRepo.BEGIN_SCHEMA)
            automation_info_lines.append(current_schema.to_json(pretty=True))
            automation_info_lines.append(GithubRepo.END_SCHEMA)
            automation_info_lines.append("```")
            automation_info_lines.append("")
            automation_info_lines.append("</details>")

            # Add batch JSON
        encodable_batch: Dict[str, Any] = {
            "title": batch["title"],
            "items": [item.bundle() for item in batch["items"]],
        }
        if "metadata" in batch:
            encodable_batch["metadata"] = batch["metadata"]
        automation_info_lines.append("<details><summary>Batch JSON</summary>")
        automation_info_lines.append("")
        automation_info_lines.append("```")
        automation_info_lines.append(GithubRepo.BEGIN_BATCH)
        automation_info_lines.append(json.dumps(encodable_batch, indent=4))
        automation_info_lines.append(GithubRepo.END_BATCH)
        automation_info_lines.append("```")
        automation_info_lines.append("")
        automation_info_lines.append("</details>")

        return "\n".join(automation_info_lines)

    def get_outstanding_changes(self) -> Sequence[github_change.GithubChange]:
        """Gets all outstanding pull requests for the Repo.

        Returns:
            Sequence[github_change.GithubChange]: The outstanding Changes against the Repo.
        """

        repo = GithubRepo.get_github_repo(self._params["full_github_name"])
        pulls = repo.get_pulls(
            "open", sort="created", direction="desc", base=self._params["base_branch_name"]
        )
        changes: List[github_change.GithubChange] = []
        for pull in pulls:
            changes.append(
                github_change.GithubChange(
                    {
                        "full_github_name": self._params["full_github_name"],
                        "pull_request_number": pull.number,
                    }
                )
            )

        return changes

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GithubRepo:
        """Produces a GithubRepo from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            GithubRepo: An instance of the GithubRepo
        """

        base_branch_name = data["base_branch_name"]
        assert isinstance(base_branch_name, str)
        full_github_name = data["full_github_name"]
        assert isinstance(full_github_name, str)
        params: GithubRepoParams = {
            "base_branch_name": base_branch_name,
            "full_github_name": full_github_name,
        }

        required_labels = data.get("required_labels")
        if required_labels is not None:
            assert isinstance(required_labels, List)
            params["required_labels"] = required_labels

        hide_automation_info = data.get("hide_automation_info")
        if hide_automation_info is not None:
            assert isinstance(hide_automation_info, bool)
            params["hide_automation_info"] = hide_automation_info

        hide_autotransform_docs = data.get("hide_autotransform_docs")
        if hide_autotransform_docs is not None:
            assert isinstance(hide_autotransform_docs, bool)
            params["hide_autotransform_docs"] = hide_autotransform_docs

        return GithubRepo(params)
