# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Transformer components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.type import TransformerType


class TransformerBundle(TypedDict):
    """A bundled version of the Transformer object used for JSON encoding."""

    params: Mapping[str, Any]
    type: TransformerType


class Transformer(ABC):
    """The base for Transformer components.

    Attributes:
        params (Mapping[str, Any]): The paramaters that control operation of the Transformer.
            Should be defined using a TypedDict in subclasses
    """

    params: Mapping[str, Any]

    def __init__(self, params: Mapping[str, Any]):
        """A simple constructor.

        Args:
            params (Mapping[str, Any]): The paramaters used to set up the Transformer
        """
        self.params = params

    @abstractmethod
    def get_type(self) -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer
        """

    @abstractmethod
    def transform(self, file: CachedFile) -> None:
        """Execute a transformation against the provided file. Additional files may be modified
        based on these changes (i.e. as part of a rename) and should be done as part of this
        transform rather than using separate calls to transform. All writing should be done via
        CachedFile's write_content method to ensure operations are easily accessible to testing.

        Args:
            file (CachedFile): The file that will be transformed
        """

    def bundle(self) -> TransformerBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            TransformerBundle: The encodable bundle
        """
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Transformer:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            Transformer: An instance of the Transformer
        """
