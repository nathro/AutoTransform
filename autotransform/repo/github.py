# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from typing import Any, Mapping

from git import Repo as GitPython
from github import Github

from autotransform.batcher.base import BatchWithFiles
from autotransform.config import fetcher as Config
from autotransform.repo.git import GitRepo, GitRepoParams
from autotransform.repo.type import RepoType


class GithubRepoParams(GitRepoParams):
    full_github_name: str


class GithubRepo(GitRepo):
    params: GithubRepoParams
    local_repo: GitPython
    github: Github

    def __init__(self, params: GithubRepoParams):
        GitRepo.__init__(self, params)
        self.github = GithubRepo.get_github_object()

    def get_type(self) -> RepoType:
        return RepoType.GITHUB

    @staticmethod
    def get_github_object() -> Github:
        url = Config.get_github_base_url()
        token = Config.get_github_token()
        if token is not None:
            if url is not None:
                return Github(token, base_url=url)
            return Github(token)
        if url is not None:
            return Github(Config.get_github_username(), Config.get_github_password(), base_url=url)
        return Github(Config.get_github_username(), Config.get_github_password())

    def submit(self, batch: BatchWithFiles) -> None:
        title = batch["metadata"]["title"]
        summary = batch["metadata"].get("summary", "")
        tests = batch["metadata"].get("tests", "")

        self.commit(batch["metadata"])

        commit_branch = GitRepo.get_branch_name(title)
        remote = self.local_repo.remote()
        self.local_repo.git.push(remote.name, "-u", commit_branch)

        github_repo = self.github.get_repo(self.params["full_github_name"])
        body = f"""
            SUMMARY
            {summary}
            
            TESTS
            {tests}
        """
        github_repo.create_pull(
            title=title, body=body, base=self.active_branch.name, head=commit_branch
        )

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GithubRepo:
        path = data["path"]
        assert isinstance(path, str)
        full_github_name = data["full_github_name"]
        assert isinstance(full_github_name, str)
        return GithubRepo({"path": path, "full_github_name": full_github_name})
