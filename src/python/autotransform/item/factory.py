# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Items from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.item.base import Item, ItemBundle
from autotransform.item.file import FileItem
from autotransform.item.type import ItemType


class ItemFactory:
    """The factory class for Items. Maps a type to an Item.

    Attributes:
        _map (Dict[ItemType, Callable[[Mapping[str, Any]], Item]]): A mapping from
            ItemType to the from_data function of the appropriate Item.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[ItemType, Callable[[Mapping[str, Any]], Item]] = {
        ItemType.FILE: FileItem.from_data,
        ItemType.GENERIC: Item.from_data,
    }

    @staticmethod
    def get(bundle: ItemBundle) -> Item:
        """Simple get method using the _map attribute.

        Args:
            bundle (ItemBundle): The bundled Item type and params.

        Returns:
            Item: An instance of the associated Item.
        """

        if bundle["type"] in ItemFactory._map:
            return ItemFactory._map[bundle["type"]](bundle)

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "ITEMS") and bundle["type"] in module.ITEMS:
                return module.ITEMS[bundle["type"]](bundle)
        raise ValueError(f"No Item found for type {bundle['type']}")
