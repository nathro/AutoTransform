# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An object representing data associated with a given file that is primed by the Input
component.
"""

from typing import Any, Dict, Optional


class FileDataObject:
    """An object representing keyed data about an object providing typed getter methods."""

    def __init__(self, data: Dict[str, Any]):
        """A simple constructor

        Args:
            data (Dict[str, Any]): The data associated with the file
        """
        self.data: Dict[str, Any] = data

    def get_str(self, key: str) -> str:
        """Gets the string value associated with a given key.

        Args:
            key (str): The key for which to fetch a value

        Raises:
            ValueError: Raises an error when the value is not present or
                is not of the correct type

        Returns:
            str: The value associated with the key
        """
        val = self.data[key]
        if isinstance(val, str):
            return val
        raise ValueError("Key [" + key + "] is not string")

    def get_optional_str(self, key: str) -> Optional[str]:
        """Gets the string value associated with a given key if present, otherwise
        None is returned.

        Args:
            key (str): The key for which to fetch a value

        Raises:
            ValueError: Raises an error when the value is of an incorrect
                type

        Returns:
            Optional[str]: The value associated with the key if present, otherwise None
        """
        if key in self.data:
            val = self.data[key]
            if isinstance(val, str):
                return val
            raise ValueError("Key [" + key + "] is not string")
        return None

    def get_int(self, key: str) -> int:
        """Gets the int value associated with a given key.

        Args:
            key (str): The key for which to fetch a value

        Raises:
            ValueError: Raises an error when the value is not present or
                is not of the correct type

        Returns:
            int: The value associated with the key
        """
        val = self.data[key]
        if isinstance(val, int):
            return val
        raise ValueError("Key [" + key + "] is not int")

    def get_optional_int(self, key: str) -> Optional[int]:
        """Gets the int value associated with a given key if present, otherwise
        None is returned.

        Args:
            key (str): The key for which to fetch a value

        Raises:
            ValueError: Raises an error when the value is of an incorrect
                type

        Returns:
            Optional[int]: The value associated with the key if present, otherwise None
        """
        if key in self.data:
            val = self.data[key]
            if isinstance(val, int):
                return val
            raise ValueError("Key [" + key + "] is not int")
        return None
