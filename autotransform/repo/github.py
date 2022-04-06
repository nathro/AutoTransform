# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the GithubRepo."""

from __future__ import annotations

from typing import Any, Mapping

from github import Github

from autotransform.batcher.base import Batch
from autotransform.config import fetcher as Config
from autotransform.repo.git import GitRepo, GitRepoParams
from autotransform.repo.type import RepoType


class GithubRepoParams(GitRepoParams):
    """The param type for a GithubRepo."""

    full_github_name: str


class GithubRepo(GitRepo):
    """A Repo that provides support for commiting changes to git.

    Attributes:
        params (GithubRepoParams): Contains the root path to the fully qualified name of the
            repo on Github
        github (Github): An object allowing interaction with the Github API
    """

    params: GithubRepoParams
    github: Github

    def __init__(self, params: GithubRepoParams):
        """Establishes the Github object to enable API access

        Args:
            params (GithubRepoParams): The paramaters used to set up the GithubRepo
        """
        GitRepo.__init__(self, params)
        self.github = GithubRepo.get_github_object()

    def get_type(self) -> RepoType:
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
            Github: An object allowing interaction with the Github API
        """
        url = Config.get_github_base_url()
        token = Config.get_github_token()
        if token is not None:
            if url is not None:
                return Github(token, base_url=url)
            return Github(token)
        if url is not None:
            return Github(Config.get_github_username(), Config.get_github_password(), base_url=url)
        return Github(Config.get_github_username(), Config.get_github_password())

    def submit(self, batch: Batch) -> None:
        """Performs the normal submit for a git repo then submits a pull request
        against the provided Github repo.

        Args:
            batch (Batch): The Batch for which the changes were made
        """
        title = batch["metadata"]["title"]

        self.commit(batch["metadata"])

        commit_branch = GitRepo.get_branch_name(title)
        remote = self.local_repo.remote()
        self.local_repo.git.push(remote.name, "-u", commit_branch)

        github_repo = self.github.get_repo(self.params["full_github_name"])
        body = str(batch["metadata"].get("body"))
        assert body is not None, "All pull requests must have a body."
        github_repo.create_pull(
            title=title,
            body=body,
            base=self.base_branch.name,
            head=commit_branch,
        )

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
        return GithubRepo(
            {"base_branch_name": base_branch_name, "full_github_name": full_github_name}
        )
