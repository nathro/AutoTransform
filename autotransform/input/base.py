# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Input components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, List, Mapping, TypedDict

from autotransform.input.type import InputType


class InputBundle(TypedDict):
    """A bundled version of the Input object used for JSON encoding."""

    params: Mapping[str, Any]
    type: InputType


class Input(ABC):
    """The base for Input components.

    Attributes:
        params (Mapping[str, Any]): The paramaters that control operation of the Input.
            Should be defined using a TypedDict in subclasses
    """

    params: Mapping[str, Any]

    def __init__(self, params: Mapping[str, Any]):
        """A simple constructor.

        Args:
            params (Mapping[str, Any]): The paramaters used to set up the Input
        """
        self.params = params

    @abstractmethod
    def get_type(self) -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input
        """

    @abstractmethod
    def get_files(self) -> List[str]:
        """Get a list of files to be used by the transformation based on the input criteria.

        Returns:
            List[str]: The eligible files for transformation
        """

    def bundle(self) -> InputBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            InputBundle: The encodable bundle
        """
        return {
            "params": self.params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Input:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            Input: An instance of the Input
        """
