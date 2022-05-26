# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Input components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Sequence, TypedDict, TypeVar

from autotransform.input.type import InputType
from autotransform.item.base import Item

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class InputBundle(TypedDict):
    """A bundled version of the Input object used for JSON encoding."""

    params: Mapping[str, Any]
    type: InputType


class Input(Generic[TParams], ABC):
    """The base for Input components. Used by AutoTransform to get Items that
    represent potentially transformable units for a Schema. Usually returns files but
    any Item can be returned as long as Schema components work with it.

    Attributes:
        _params (TParams): The paramaters that control operation of the Input.
            Should be defined using a TypedDict in subclasses.
    """

    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Input.
        """
        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Input.

        Returns:
            TParams: The paramaters used to set up the Input.
        """
        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input.
        """

    @abstractmethod
    def get_items(self) -> Sequence[Item]:
        """Get a list of Items to be used by the transformation based on the Input criteria. Usually
        returns FileItems.

        Returns:
            Sequence[Item]: The eligible Items for transformation.
        """

    def bundle(self) -> InputBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            InputBundle: The encodable bundle.
        """
        return {
            "params": self._params,
            "type": self.get_type(),
        }

    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Input:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Input: An instance of the Input.
        """
