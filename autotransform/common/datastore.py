# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>


"""Provides a globally accessible store of data associated with files.
Filled by Input components. Import the data_store variable when using,
not the FileDataStore class.
"""

from typing import Dict, Optional

from autotransform.common.dataobject import FileDataObject


class FileDataStore:
    """The data store containing a mapping of file path to data."""

    def __init__(self):
        """A simple constructor."""
        self.items: Dict[str, Optional[FileDataObject]] = {}

    def add_object(self, key: str, data: Optional[FileDataObject]) -> None:
        """Adds an object to the data store associating it with a file.

        Args:
            key (str): The path of the file
            data (Optional[FileDataObject]): The data to associate with the file

        Raises:
            KeyError: Raises an error when the key is already present in the store
        """
        if key in self.items:
            raise KeyError("Duplicate key")
        self.items[key] = data

    def get_object_data(self, key: str) -> Optional[FileDataObject]:
        """Gets the data associated with a file if present.

        Args:
            key (str): The path to a file

        Returns:
            Optional[FileDataObject]: The data associated with the provided file
        """
        if key in self.items:
            return self.items[key]
        return None


# To use, import this data_store variable rather than the class
data_store = FileDataStore()
