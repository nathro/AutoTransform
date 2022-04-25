# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GitRepo."""

from __future__ import annotations

import re
import subprocess
from typing import Any, Mapping, TypedDict

from git import Head
from git import Repo as GitPython

from autotransform.batcher.base import Batch
from autotransform.repo.base import Repo
from autotransform.repo.type import RepoType


class GitRepoParams(TypedDict):
    """The param type for a GitRepo."""

    base_branch_name: str


class GitRepo(Repo[GitRepoParams]):
    """A Repo that provides support for commiting changes to git.

    Attributes:
        _params (GitRepoParams): Contains tthe base branch name that the changes will be
            made on top of.
        _local_repo (GitPython): An object representing the repo used for git operations.
        _base_branch (Head): The base branch to use for changes.
    """

    _params: GitRepoParams
    _local_repo: GitPython
    _base_branch: Head

    BRANCH_NAME_PREFIX: str = "AUTO_TRANSFORM"
    COMMIT_MESSAGE_PREFIX: str = "[AutoTransform]"

    @staticmethod
    def get_branch_name(title: str, schema_name: str) -> str:
        """Gets a unique name for a git branch using the title from the Batch.

        Args:
            title (str): The title of the change.
            schema_name (str): The name of the schema for this change.

        Returns:
            str: The name of the branch for this change.
        """

        # Handle titles of the format "[1/2] foo" that can come from chunk batching
        fixed_title = re.sub(r"\[(\d+)/(\d+)\]", r"\1_\2", title)
        return f"{GitRepo.BRANCH_NAME_PREFIX}_{schema_name}_{fixed_title}".replace(" ", "_")

    @staticmethod
    def get_commit_message(title: str, schema_name: str) -> str:
        """Gets a commit message for the change based on the Batch title.

        Args:
            title (str): The title of the change.
            schema_name (str): The name of the schema for this change.

        Returns:
            str: The commit message for this change.
        """

        # Add a blank space before prefixes
        if not title.startswith("["):
            title = " " + title
        return f"{GitRepo.COMMIT_MESSAGE_PREFIX}[{schema_name}]{title}"

    def __init__(self, params: GitRepoParams):
        """Gets the local repo object for future operations and attains the initial active branch.

        Args:
            params (GitRepoParams): The paramaters used to set up the GitRepo.
        """

        Repo.__init__(self, params)
        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        self._local_repo = GitPython(repo_dir)
        for branch in self._local_repo.heads:
            if branch.name == self._params["base_branch_name"]:
                branch.checkout()
                self._base_branch = branch
                break

    @staticmethod
    def get_type() -> RepoType:
        """Used to map Repo components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RepoType: The unique type associated with this Repo
        """

        return RepoType.GIT

    def has_changes(self, _: Batch) -> bool:
        """Checks the dirty status of the repo, including untracked changes.

        Args:
            _ (Batch): Unused Batch object used to match signature to base.

        Returns:
            bool: Returns True if there are any changes to the repo either staged or unstaged.
        """
        return self._local_repo.is_dirty(untracked_files=True)

    def submit(self, batch: Batch, schema_name: str) -> None:
        """Stages all changes and commits them in a new branch.

        Args:
            batch (Batch): The Batch for which the changes were made.
            schema_name (str): The name of the schema for this change.
        """

        self.commit(batch["title"], schema_name)

    def commit(self, title: str, schema_name: str) -> None:
        """Creates a new branch for all changes, stages them, and commits them.

        Args:
            title (str): The title of the Batch being commited.
            schema_name (str): The name of the schema for this change.
        """

        self._local_repo.git.checkout("-b", GitRepo.get_branch_name(title, schema_name))
        self._local_repo.git.add(all=True)
        self._local_repo.index.commit(GitRepo.get_commit_message(title, schema_name))

    def clean(self, _: Batch) -> None:
        """Performs `git reset --hard` to remove any changes.

        Args:
            _ (Batch): Unused Batch object used to match signature to base
        """

        self._local_repo.git.reset("--hard")

    def rewind(self, batch: Batch) -> None:
        """First eliminates any uncommitted changes using the clean function then checks out
        the initial active branch.

        Args:
            batch (Batch): The Batch for the submitted changes that is being rewound.
        """

        self.clean(batch)
        self._base_branch.checkout()

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GitRepo:
        """Produces a GitRepo from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            GitRepo: An instance of the GitRepo.
        """

        base_branch_name = data["base_branch_name"]
        assert isinstance(base_branch_name, str)
        return GitRepo({"base_branch_name": base_branch_name})
