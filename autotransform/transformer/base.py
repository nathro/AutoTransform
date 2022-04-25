# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Transformer components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, TypedDict, TypeVar

from autotransform.batcher.base import Batch
from autotransform.transformer.type import TransformerType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class TransformerBundle(TypedDict):
    """A bundled version of the Transformer object used for JSON encoding."""

    params: Mapping[str, Any]
    type: TransformerType


class Transformer(Generic[TParams], ABC):
    """The base for Transformer components. Transformers are used to execute changes to a codebase.
    A Transformer takes in a Batch and then executes all changes associated with the Batch.

    Attributes:
        _params (TParams): The paramaters that control operation of the Transformer.
            Should be defined using a TypedDict in subclasses
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Transformer.
        """

        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Transformer.

        Returns:
            TParams: The paramaters used to set up the Transformer.
        """

        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer.
        """

    @abstractmethod
    def transform(self, batch: Batch) -> None:
        """Execute a transformation against the provided Batch. All writing should be done via
        CachedFile's write_content method or FileItem's write_content method to ensure operations
        are easily accessible to testing and file content cache's are kept accurate.

        Args:
            batch (Batch): The Batch that will be transformed.
        """

    def bundle(self) -> TransformerBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            TransformerBundle: The encodable bundle.
        """

        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Transformer:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Transformer: An instance of the Transformer.
        """
