# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the GitRepo."""

from __future__ import annotations

import subprocess
from typing import Any, Mapping, TypedDict

from git import Head
from git import Repo as GitPython

from autotransform.batcher.base import Batch, BatchMetadata
from autotransform.repo.base import Repo
from autotransform.repo.type import RepoType


class GitRepoParams(TypedDict):
    """The param type for a GitRepo."""

    base_branch_name: str


class GitRepo(Repo[GitRepoParams]):
    """A Repo that provides support for commiting changes to git.

    Attributes:
        params (GitRepoParams): Contains the root path to the git repo
        local_repo (GitPython): An object representing the repo used for git operations
        base_branch (Head): The base branch to use for changes
    """

    params: GitRepoParams
    local_repo: GitPython
    base_branch: Head

    COMMIT_BRANCH_BASE: str = "AUTO_TRANSFORM"

    @staticmethod
    def get_branch_name(title: str) -> str:
        """Gets a unique name identified with a change using the provided title.

        Args:
            title (str): The title of the change

        Returns:
            str: The name of the branch for this change
        """
        return GitRepo.COMMIT_BRANCH_BASE + "_" + title.replace(" ", "_")

    @staticmethod
    def get_commit_message(metadata: BatchMetadata) -> str:
        """Gets a commit message for the change based on BatchMetadata

        Args:
            metadata (BatchMetadata): The metadata of the batch the commit message is for

        Returns:
            str: The commit message
        """
        return "[AutoTransform] " + metadata["title"]

    def __init__(self, params: GitRepoParams):
        """Gets the local repo object for future operations and attains the initial active branch.

        Args:
            params (GitRepoParams): The paramaters used to set up the GitRepo
        """
        Repo.__init__(self, params)
        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        self.local_repo = GitPython(repo_dir)
        for branch in self.local_repo.heads:
            if branch.name == self.params["base_branch_name"]:
                branch.checkout()
                self.base_branch = branch

    def get_type(self) -> RepoType:
        """Used to map Repo components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RepoType: The unique type associated with this Repo
        """
        return RepoType.GIT

    def has_changes(self, _: Batch) -> bool:
        """Checks the dirty status of the repo, including untracked changes

        Args:
            _ (Batch): Unused Batch object used to match signature to base

        Returns:
            bool: Returns True if there are any changes to the repo either staged or unstaged
        """
        return self.local_repo.is_dirty(untracked_files=True)

    def submit(self, batch: Batch) -> None:
        """Stages all changes and commits them in a new branch.

        Args:
            batch (Batch): The Batch for which the changes were made
        """
        self.commit(batch["metadata"])

    def clean(self, _: Batch) -> None:
        """Performs `git reset --hard` to remove any changes.

        Args:
            _ (Batch): Unused Batch object used to match signature to base
        """
        self.local_repo.git.reset("--hard")

    def rewind(self, batch: Batch) -> None:
        """First eliminates any uncommitted changes using the clean function than checks out
        the initial active branch.

        Args:
            batch (Batch): The Batch for the submitted changes that is being rewound
        """
        self.clean(batch)
        self.base_branch.checkout()

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GitRepo:
        """Produces a GitRepo from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            GitRepo: An instance of the GitRepo
        """
        base_branch_name = data["base_branch_name"]
        assert isinstance(base_branch_name, str)
        return GitRepo({"base_branch_name": base_branch_name})

    def commit(self, metadata: BatchMetadata) -> None:
        """Creates a new branch for all changes, stages them, and commits them.

        Args:
            metadata (BatchMetadata): The metadata of the Batch responsible for the changes
        """
        self.local_repo.git.checkout("-b", GitRepo.get_branch_name(metadata["title"]))
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(GitRepo.get_commit_message(metadata))
