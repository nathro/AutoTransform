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
from functools import cached_property
from typing import Any, ClassVar, List, Mapping, Optional, Sequence

from git import Head
from git import Repo as GitPython

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.repo.base import Repo, RepoName


class GitRepo(Repo):
    """A Repo that provides support for commiting changes to git.

    Attributes:
        base_branch (str): The name of the base branch for the repository.
        name (ClassVar[str]): The name of the component.
        BRANCH_NAME_PREFIX (ClassVar[str]): The prefix to apply to branches that are created.
        COMMIT_MESSAGE_PREFIX (ClassVar[str]): The prefix to apply to commits that are created.
    """

    base_branch: str

    name: ClassVar[RepoName] = RepoName.GIT

    BRANCH_NAME_PREFIX: ClassVar[str] = "AUTO_TRANSFORM"
    COMMIT_MESSAGE_PREFIX: ClassVar[str] = "[AutoTransform]"

    @staticmethod
    def get_changed_files_from_status(status: str) -> List[str]:
        """Parses the git status to get the changed files.

        Args:
            status (str): The result of git status -s --untracked-files

        Returns:
            List[str]: The changed files.
        """

        if status.strip() == "":
            return []
        return [
            re.sub(r"^(?:\?\?|M|A|D)", "", line.strip()).strip()
            for line in status.strip().split("\n")
        ]

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
            schema_name = f"{autotransform.schema.current.config.schema_name}/"
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
            title = f" {title}"
        if autotransform.schema.current is not None:
            schema_name = f"[{autotransform.schema.current.config.schema_name}]"
        else:
            schema_name = ""
        return f"{GitRepo.COMMIT_MESSAGE_PREFIX}{schema_name}{title}"

    @cached_property
    def _local_repo(self) -> GitPython:
        """Returns a cached instance of the local repo

        Returns:
            GitPython: The local repository.
        """

        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        return GitPython(repo_dir)

    @cached_property
    def _base_branch(self) -> Head:
        """Returns a cached instance of the base branch.

        Returns:
            Head: The base branch.
        """

        for branch in self._local_repo.heads:
            if branch.name == self.base_branch:
                return branch
        raise ValueError("Invalid base branch name, branch not found.")

    def get_changed_files(self, _batch: Batch) -> List[str]:
        """Uses git status to get all changed files.

        Args:
            _batch (Batch): Unused Batch object used to match signature to base.

        Returns:
            List[str]: All changed files, including untracked files.
        """

        return GitRepo.get_changed_files_from_status(
            self._local_repo.git.status("-s", untracked_files=True),
        )

    def has_outstanding_change(self, batch: Batch) -> bool:
        """Checks the state of the repo to see whether an outstanding Change
        for the Batch exists.

        Args:
            batch (Batch): The Batch to check for.

        Returns:
            bool: Whether an outstanding Change exists.
        """

        return GitRepo.get_branch_name(batch["title"]) in [
            str(ref) for ref in self._local_repo.references
        ]

    def submit(
        self,
        batch: Batch,
        _transform_data: Optional[Mapping[str, Any]],
        change: Optional[Change] = None,
    ) -> None:
        """Stages all changes and commits them in a new branch.

        Args:
            batch (Batch): The Batch for which the changes were made.
            _transform_data (Optional[Mapping[str, Any]]): Data from the transformation. Unused.
            change (Optional[Change]): An associated change which should be updated.
                Defaults to None.
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

    def clean(self, _batch: Batch) -> None:
        """Performs `git reset --hard` to remove any changes.

        Args:
            _batch (Batch): Unused Batch object used to match signature to base
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
