# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from typing import Any, Mapping, TypedDict

from git import Repo as GitPython
from git.refs.head import Head

from autotransform.batcher.base import BatchMetadata, BatchWithFiles
from autotransform.repo.base import Repo
from autotransform.repo.type import RepoType


class GitRepoParams(TypedDict):
    path: str


class GitRepo(Repo):
    params: GitRepoParams
    local_repo: GitPython
    active_branch: Head

    COMMIT_BRANCH_BASE: str = "AUTO_TRANSFORM_COMMIT"

    @staticmethod
    def get_branch_name(title: str) -> str:
        return GitRepo.COMMIT_BRANCH_BASE + "_" + title.replace(" ", "_")

    def __init__(self, params: GitRepoParams):
        Repo.__init__(self, params)
        self.local_repo = GitPython(self.params["path"])
        self.active_branch = self.local_repo.active_branch

    def get_type(self) -> RepoType:
        return RepoType.GIT

    def has_changes(self, batch: BatchWithFiles) -> bool:
        return self.local_repo.is_dirty(untracked_files=True)

    def submit(self, batch: BatchWithFiles) -> None:
        self.commit(batch["metadata"])

    def clean(self, batch: BatchWithFiles) -> None:
        self.local_repo.git.reset("--hard")

    def rewind(self, batch: BatchWithFiles) -> None:
        self.clean(batch)
        self.local_repo.active_branch.checkout()

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GitRepo:
        path = data["path"]
        assert isinstance(path, str)
        return GitRepo({"path": path})

    def commit(self, metadata: BatchMetadata) -> None:
        self.local_repo.git.checkout("-b", GitRepo.get_branch_name(metadata["title"]))
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(metadata["title"])
