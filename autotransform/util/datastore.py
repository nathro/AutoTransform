# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>


"""Provides a globally accessible store of data associated with items from the Input.
Used as a singleton. Attempting to construct a DataStore object outside of the
get() method will lead to unexpected behavior.
"""

from __future__ import annotations

from typing import Dict, Optional

from autotransform.util.dataobject import DataObject


class DataStore:
    """The data store containing a mapping of item to data object.

    Attributes:
        __instance (Optional[DataStore]): The singleton instance of the DataStore.
        items (Dict[str, Optional[DataObject]]): The mapping from item to data.
    """

    __instance: Optional[DataStore] = None
    items: Dict[str, Optional[DataObject]]

    def __init__(self):
        """A simple constructor."""
        if DataStore.__instance is not None:
            raise Exception("Trying to instantiate new DataStore when one is already present.")
        self.items: Dict[str, Optional[DataObject]] = {}
        DataStore.__instance = self

    @staticmethod
    def get() -> DataStore:
        """A singleton getter method for the DataStore.

        Returns:
            DataStore: The singleton instance of the DataStore.
        """
        if DataStore.__instance is None:
            DataStore.__instance = DataStore()
        return DataStore.__instance

    def add_object(self, key: str, data: Optional[DataObject]) -> None:
        """Adds an object to the data store associating it with an item.

        Args:
            key (str): The item returned by an Input.
            data (Optional[DataObject]): The data to associate with the item.

        Raises:
            KeyError: Raises an error when the item is already present in the store.
        """
        if key in self.items:
            raise KeyError("Duplicate key")
        self.items[key] = data

    def get_object_data(self, key: str) -> Optional[DataObject]:
        """Gets the data associated with an item if present.

        Args:
            key (str): The item from the Input.

        Returns:
            Optional[DataObject]: The data associated with the provided item
        """
        if key in self.items:
            return self.items[key]
        return None
