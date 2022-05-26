# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Batcher components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Mapping, Sequence, TypedDict, TypeVar

from typing_extensions import NotRequired

from autotransform.batcher.type import BatcherType
from autotransform.item.base import Item

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class Batch(TypedDict):
    """A logical grouping of Items with title and associated metadata."""

    items: Sequence[Item]
    metadata: NotRequired[Mapping[str, Any]]
    title: str


class BatcherBundle(TypedDict):
    """A bundled version of the Batcher object used for JSON encoding."""

    params: Mapping[str, Any]
    type: BatcherType


class Batcher(Generic[TParams], ABC):
    """The base for Batcher components. Used by AutoTransform to separate Items in to logical
    groupings that can be acted on indepently and have associated metadata.

    Attributes:
        _params (TParams): The paramaters that control operation of the Batcher.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Batcher.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Batcher.

        Returns:
            TParams: The paramaters used to set up the Batcher.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher.
        """

    @abstractmethod
    def batch(self, items: Sequence[Item]) -> List[Batch]:
        """Take filtered Items and separate in to logical groupings with associated group metadata
        and title.

        Args:
            items (Sequence[Item]): The filtered Items to separate.

        Returns:
            List[Batch]: A list of logical groupings of Items with associated group metadata and
                title.
        """

    def bundle(self) -> BatcherBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            BatcherBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Batcher:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Batcher: An instance of the Batcher.
        """
