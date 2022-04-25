# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the GithubRepo."""

from __future__ import annotations

from typing import Any, List, Mapping

from github import Github, Repository
from typing_extensions import NotRequired

from autotransform.batcher.base import Batch
from autotransform.config import fetcher as Config
from autotransform.repo.git import GitRepo, GitRepoParams
from autotransform.repo.type import RepoType


class GithubRepoParams(GitRepoParams):
    """The param type for a GithubRepo."""

    full_github_name: str
    required_labels: NotRequired[List[str]]


class GithubRepo(GitRepo):
    """A Repo that provides support for submitting changes as a pull request against
    a Github repo.

    Attributes:
        _params (GithubRepoParams): Contains all git params as well as the Github repo
            name and any required labels.
        _github_repo (Repository.Repository): The Github Repository being interacted with.
    """

    _params: GithubRepoParams
    _github_repo: Repository.Repository

    def __init__(self, params: GithubRepoParams):
        """Establishes the Github object to enable API access.

        Args:
            params (GithubRepoParams): The paramaters used to set up the GithubRepo.
        """

        GitRepo.__init__(self, params)
        self._github_repo = GithubRepo.get_github_object().get_repo(
            self._params["full_github_name"],
        )

    def get_github_repo(self) -> Repository.Repository:
        """Gets the Github repository being interacted with.

        Returns:
            Repository.Repository: The Github repository being interacted with.
        """

        return self._github_repo

    @staticmethod
    def get_type() -> RepoType:
        """Used to map Repo components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RepoType: The unique type associated with this Repo
        """

        return RepoType.GITHUB

    @staticmethod
    def get_github_object() -> Github:
        """Authenticates with Github to allow API access via a token provided by AutoTransform
        configuration. If no token is provided a username + password will be used. Also allows
        use of a base URL for enterprise use cases.

        Returns:
            Github: An object allowing interaction with the Github API.
        """

        url = Config.get_credentials_github_base_url()
        token = Config.get_credentials_github_token()
        if token is not None:
            if url is not None:
                return Github(token, base_url=url)
            return Github(token)
        if url is not None:
            return Github(
                Config.get_credentials_github_username(),
                Config.get_credentials_github_password(),
                base_url=url,
            )
        return Github(
            Config.get_credentials_github_username(), Config.get_credentials_github_password()
        )

    def submit(self, batch: Batch, schema_name: str) -> None:
        """Performs the normal submit for a git repo then submits a pull request
        against the provided Github repo.

        Args:
            batch (Batch): The Batch for which the changes were made.
            schema_name (str): The name of the schema for this change.
        """

        title = GitRepo.get_commit_message(batch["title"], schema_name)

        self.commit(batch["title"], schema_name)

        commit_branch = GitRepo.get_branch_name(batch["title"], schema_name)
        remote = self._local_repo.remote()
        self._local_repo.git.push(remote.name, "-u", commit_branch)

        body = batch["metadata"].get("body", None)
        assert body is not None, "All pull requests must have a body."
        pull_request = self._github_repo.create_pull(
            title=title,
            body=str(body),
            base=self._base_branch.name,
            head=commit_branch,
        )

        labels = batch["metadata"].get("labels", [])
        assert isinstance(labels, List)
        labels = labels + self._params.get("required_labels", [])
        if len(labels) > 0:
            pull_request.add_to_labels(*labels)

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

        return GithubRepo(params)
