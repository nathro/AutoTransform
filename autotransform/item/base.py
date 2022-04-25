# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Item components. Can be used as a generic Item."""

from __future__ import annotations

from abc import ABC
from typing import Any, Dict, Mapping, Optional, TypedDict

from typing_extensions import NotRequired

from autotransform.item.type import ItemType


class ItemBundle(TypedDict):
    """A bundled version of the Item object used for JSON encoding."""

    extra_data: NotRequired[Mapping[str, Any]]
    key: str
    type: ItemType


class Item(ABC):
    """The base for Item components. Returned by Input components and act as the units on which
    AutoTransform operates.

    Attributes:
        _extra_data (Optional[Mapping[str, Any]]): Any extra data that needs to be associated with
            this Item.Should be JSON encodable.
        _key (str): A unique key used to represent this item, such as a file path.
    """

    _extra_data: Optional[Mapping[str, Any]]
    _key: str

    def __init__(self, key: str, extra_data: Optional[Mapping[str, Any]] = None):
        """A simple constructor.

        Args:
            key (str): The unique key representing this Item.
            extra_data (Optional[Mapping[str, Any]]): Any extra data that needs to be associated
                with the Item.
        """

        self._key = key
        self._extra_data = extra_data

    def get_key(self) -> str:
        """Gets the unique key that represents the Item.

        Returns:
            str: The unique key representing the Item.
        """

        return self._key

    def get_extra_data(self) -> Optional[Mapping[str, Any]]:
        """Gets the extra data associated with the Item.

        Returns:
            Optional[Mapping[str, Any]]: The extra data associated with the Item.
        """

        return self._extra_data

    @staticmethod
    def get_type() -> ItemType:
        """Used to map Item components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ItemType: The unique type associated with this Item.
        """

        return ItemType.GENERIC

    def bundle(self) -> ItemBundle:
        """Generates a JSON encodable bundle.
        If a component's params are not JSON encodable this method should be overridden to provide
        an encodable version.

        Returns:
            ItemBundle: The encodable bundle.
        """

        bundle: ItemBundle = {
            "key": self._key,
            "type": self.get_type(),
        }
        if self._extra_data is not None:
            bundle["extra_data"] = self._extra_data
        return bundle

    @classmethod
    def from_data(cls, data: Mapping[str, Any]) -> Item:
        """Produces an instance of the component from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            Item: An instance of the Item.
        """

        key = data["key"]
        assert isinstance(key, str)
        extra_data = data.get("extra_data", None)
        if extra_data is not None:
            assert isinstance(extra_data, Dict)
        return cls(key, extra_data)
