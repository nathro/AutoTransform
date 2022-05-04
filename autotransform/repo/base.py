# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Repo components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Mapping, Optional, Sequence, TypedDict, TypeVar

from autotransform.batcher.base import Batch
from autotransform.change.base import Change
from autotransform.repo.type import RepoType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class RepoBundle(TypedDict):
    """A bundled version of the Repo object used for JSON encoding."""

    params: Mapping[str, Any]
    type: RepoType


class Repo(Generic[TParams], ABC):
    """The base for Repo components. Used by AutoTransform to interact with version
    control and code review systems.

    Attributes:
        _params (TParams): The paramaters that control operation of the Repo.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Repo.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Repo.

        Returns:
            TParams: The paramaters used to set up the Repo.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> RepoType:
        """Used to map Repo components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RepoType: The unique type associated with this Repo.
        """

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
    def submit(self, batch: Batch, change: Optional[Change] = None) -> None:
        """Submit the changes to the Repo (i.e. commit, submit pull request, etc...).
        Only called when changes are present.

        Args:
            batch (Batch): The Batch for which the changes were made.
            change (Optional[Change]): An associated change which should be updated.
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
        should NOT delete any submissions (i.e. commits should stay present). Only called after a
        submit has been done.

        Args:
            batch (Batch): The Batch for which changes were submitted.
        """

    @abstractmethod
    def get_outstanding_changes(self) -> Sequence[Change]:
        """Gets all outstanding Changes for the Repo.

        Returns:
            Sequence[Change]: The outstanding Changes against the Repo.
        """

    def bundle(self) -> RepoBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            RepoBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Repo:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Repo: An instance of the Repo.
        """
