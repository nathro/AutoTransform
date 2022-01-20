# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Batcher components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Mapping, TypedDict, TypeVar

from autotransform.batcher.type import BatcherType
from autotransform.common.cachedfile import CachedFile

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class BatchMetadata(TypedDict):
    """An object containing the metadata associated with a batch. May
    include other fields as desired by Batcher and Repo/Transformer/etc.
    All fields should be JSON encodable.
    """

    title: str


class Batch(TypedDict):
    """A logical grouping of inputs with assocaited metadata."""

    files: List[CachedFile]
    metadata: BatchMetadata


class BatcherBundle(TypedDict):
    """A bundled version of the Batcher object used for JSON encoding."""

    params: Mapping[str, Any]
    type: BatcherType


class Batcher(Generic[TParams], ABC):
    """The base for Batcher components.

    Attributes:
        params (TParams): The paramaters that control operation of the Batcher.
            Should be defined using a TypedDict in subclasses
    """

    params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Batcher
        """
        self.params = params

    @abstractmethod
    def get_type(self) -> BatcherType:
        """Used to map Batcher components 1:1 with an enum, allowing construction from JSON.

        Returns:
            BatcherType: The unique type associated with this Batcher
        """

    @abstractmethod
    def batch(self, files: List[CachedFile]) -> List[Batch]:
        """Take filtered input and separate in to logical groupings with associated group metadata.
        If additional information should be associated with an individual file see
        autotransform.common.datastore.

        Args:
            files (List[CachedFile]): The filtered inputs to separate

        Returns:
            List[Batch]: A list of logical groupings of inputs with associated group metadata
        """

    def bundle(self) -> BatcherBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            BatcherBundle: The encodable bundle
        """
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Batcher:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            Batcher: An instance of the Batcher
        """
