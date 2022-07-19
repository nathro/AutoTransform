# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Repo components."""

from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any, ClassVar, List, Mapping, Optional, Sequence

from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.util.component import ComponentFactory, ComponentImport, NamedComponent


class RepoName(str, Enum):
    """A simple enum for mapping."""

    GIT = "git"
    GITHUB = "github"


class Repo(NamedComponent):
    """The base for Repo components. Used by AutoTransform to interact with version
    control and code review systems.

    Attributes:
        name (ClassVar[RepoName]): The name of the component.
    """

    name: ClassVar[RepoName]

    @abstractmethod
    def get_changed_files(self, batch: Batch) -> List[str]:
        """Gets all files in the repo that have been modified.

        Args:
            batch (Batch): The Batch that was used for the transformation

        Returns:
            List[str]: The list of files that have unsubmitted changes.
        """

    def has_changes(self, batch: Batch) -> bool:
        """Check whether any changes have been made to the underlying code based on the Batch.

        Args:
            batch (Batch): The Batch that was used for the transformation.

        Returns:
            bool: Returns True if there are any changes to the codebase.
        """

        return len(self.get_changed_files(batch)) > 0

    @abstractmethod
    def has_outstanding_change(self, batch: Batch) -> bool:
        """Checks the state of the repo to see whether an outstanding Change
        for the Batch exists.

        Args:
            batch (Batch): The Batch to check for.

        Returns:
            bool: Whether an outstanding Change exists.
        """

    @abstractmethod
    def submit(
        self,
        batch: Batch,
        transform_data: Optional[Mapping[str, Any]],
        change: Optional[Change] = None,
    ) -> None:
        """Submit the changes to the Repo (i.e. commit, submit Pull Request, etc...).
        Only called when changes are present.

        Args:
            batch (Batch): The Batch for which the changes were made.
            transform_data (Optional[Mapping[str, Any]]): Data from the transformation.
            change (Optional[Change]): An associated change which should be updated.
                Defaults to None.
        """

    @abstractmethod
    def clean(self, batch: Batch) -> None:
        """Clean any changes present in the Repo that have not been submitted.

        Args:
            batch (Batch): The Batch for which we are cleaning the repo.
        """

    @abstractmethod
    def rewind(self, batch: Batch) -> None:
        """Rewind the repo to a pre-submit state to prepare for executing another Batch. This
        should NOT delete any submissions (i.e. commits should stay present).

        Args:
            batch (Batch): The Batch for which changes were submitted.
        """

    @abstractmethod
    def get_outstanding_changes(self) -> Sequence[Change]:
        """Gets all outstanding Changes for the Repo.

        Returns:
            Sequence[Change]: The outstanding Changes against the Repo.
        """


FACTORY = ComponentFactory(
    {
        RepoName.GIT: ComponentImport(class_name="GitRepo", module="autotransform.repo.git"),
        RepoName.GITHUB: ComponentImport(
            class_name="GithubRepo", module="autotransform.repo.github"
        ),
    },
    Repo,  # type: ignore [misc]
    "repo.json",
)
