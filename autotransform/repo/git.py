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
from typing import Any, List, Mapping, Optional, Sequence, TypedDict

from git import Head
from git import Repo as GitPython

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.repo.base import Repo
from autotransform.repo.type import RepoType


class GitRepoParams(TypedDict):
    """The param type for a GitRepo."""

    base_branch_name: str


class GitRepo(Repo[GitRepoParams]):
    """A Repo that provides support for commiting changes to git.

    Attributes:
        _params (GitRepoParams): Contains the base branch name that the changes will be
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
    def get_branch_name(title: str) -> str:
        """Gets a unique name for a git branch using the title from the Batch.

        Args:
            title (str): The title of the change.

        Returns:
            str: The name of the branch for this change.
        """

        # Handle titles of the format "[1/2] foo" that can come from chunk batching
        fixed_title = re.sub(r"\[(\d+)/(\d+)\]", r"\1_\2", title)
        if autotransform.schema.current is not None:
            schema_name = f"{autotransform.schema.current.get_config().get_name()}/"
        else:
            schema_name = ""
        return f"{GitRepo.BRANCH_NAME_PREFIX}/{schema_name}{fixed_title}".replace(" ", "_")

    @staticmethod
    def get_commit_message(title: str) -> str:
        """Gets a commit message for the change based on the Batch title.

        Args:
            title (str): The title of the change.

        Returns:
            str: The commit message for this change.
        """

        # Add a blank space before prefixes
        if not title.startswith("["):
            title = " " + title
        if autotransform.schema.current is not None:
            schema_name = f"[{autotransform.schema.current.get_config().get_name()}]"
        else:
            schema_name = ""
        return f"{GitRepo.COMMIT_MESSAGE_PREFIX}{schema_name}{title}"

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

    def get_changed_files(self, _: Batch) -> List[str]:
        """Uses git status to get all changed files.

        Args:
            _ (Batch): Unused Batch object used to match signature to base.

        Returns:
            List[str]: All changed files, including untracked files.
        """

        status = self._local_repo.git.status("-s", untracked_files=True)
        if status.strip() == "":
            return []
        return [
            re.sub(r"^(?:\?\?|M|A|D)", "", line.strip()).strip()
            for line in status.strip().split("\n")
        ]

    def submit(self, batch: Batch, change: Optional[Change] = None) -> None:
        """Stages all changes and commits them in a new branch.

        Args:
            batch (Batch): The Batch for which the changes were made.
            change (Optional[Change]): An associated change which should be updated.
        """

        self.commit(batch["title"], change is not None)

    def commit(self, title: str, update: bool) -> None:
        """Creates a new branch for all changes, stages them, and commits them.

        Args:
            title (str): The title of the Batch being commited.
            update(bool): Whether to update an existing change.
        """

        if update:
            self._local_repo.git.checkout("-B", GitRepo.get_branch_name(title))
        else:
            self._local_repo.git.checkout("-b", GitRepo.get_branch_name(title))
        self._local_repo.git.add(all=True)
        self._local_repo.index.commit(GitRepo.get_commit_message(title))

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

    def get_outstanding_changes(self) -> Sequence[Change]:
        """Gets all outstanding Changes for the Repo.

        Returns:
            Sequence[Change]: The outstanding Changes against the Repo.
        """

        return []

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
