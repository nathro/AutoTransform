# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Filter components."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Generic, Mapping, Optional, TypedDict, TypeVar

from autotransform.filter.type import FilterType
from autotransform.item.base import Item

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class FilterBundle(TypedDict):
    """A bundled version of the Filter object used for JSON encoding."""

    inverted: Optional[bool]
    params: Mapping[str, Any]
    type: FilterType


class Filter(Generic[TParams], ABC):
    """The base for Filter components. Used by AutoTransform to determine if an Item from an Input
    is eligible for transformation.

    Attributes:
        _params (TParams): The paramaters that control operation of the Filter.
            Should be defined using a TypedDict in subclasses.
        _inverted (bool): Whether to invert the results of the Filter.
    """

    _inverted: bool
    _params: TParams

    def __init__(self, params: TParams):
        """A simple constructor.

        Args:
            params (TParams): The paramaters used to set up the Filter.
        """
        self._inverted = False
        self._params = params

    def get_params(self) -> TParams:
        """Gets the paramaters used to set up the Filter.

        Returns:
            TParams: The paramaters used to set up the Filter.
        """
        return self._params

    @staticmethod
    @abstractmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """

    def invert(self) -> Filter:
        """Inverts the results that the Filter will provide. Inverting an already inverted Filter
        will return it to normal operation.

        Returns:
            Filter: The Filter after setting the inversion.
        """
        self._inverted = not self._inverted
        return self

    def is_valid(self, item: Item) -> bool:
        """Check whether an Item is valid based on the Filter and handle inversion.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the Item is eligible for transformation
        """
        return self._inverted != self._is_valid(item)

    @abstractmethod
    def _is_valid(self, item: Item) -> bool:
        """Check whether an Item is valid based on the Filter. Does not handle inversion.

        Args:
            item (Item): The item to check.

        Returns:
            bool: Returns True if the item is eligible for transformation
        """

    def bundle(self) -> FilterBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            FilterBundle: The encodable bundle.
        """
        return {
            "inverted": self._inverted,
            "params": self._params,
            "type": self.get_type(),
        }

    @classmethod
    def from_data(cls, inverted: Optional[bool], data: Mapping[str, Any]) -> Filter:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid. Handles the inversion
        capabilities of the Filter.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.
            inverted (Optional[bool]): Whether the Filter was inverted before encoding.

        Returns:
            Filter: An instance of the Filter.
        """
        unbundled_filter = cls._from_data(data)
        if inverted:
            unbundled_filter.invert()
        return unbundled_filter

    @staticmethod
    @abstractmethod
    def _from_data(data: Mapping[str, Any]) -> Filter:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Filter: An instance of the Filter.
        """
