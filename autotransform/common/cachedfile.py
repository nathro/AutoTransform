# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Provides a caching mechanism for file data so that files do not have to be reread repeatedly."""

from typing import Dict

FILE_CACHE: Dict[str, str] = {}


class CachedFile:

    """A wrapper that allows accessing cached file contents.

    Attributes:
        path (str): The path of the cached file
    """

    # pylint: disable=too-few-public-methods

    path: str

    def __init__(self, path: str):
        """A simple constructor.

        Args:
            path (str): The path to the file
        """
        self.path = path

    def get_content(self) -> str:
        """Gets the file contents from the cache if present. If not present, it will read the
        file contents and cache it.

        Returns:
            str: The contents of the file
        """
        if self.path not in FILE_CACHE:
            # pylint: disable=unspecified-encoding
            with open(self.path, "r") as file:
                FILE_CACHE[self.path] = file.read()
        return FILE_CACHE[self.path]

    def __del__(self):
        if self.path in FILE_CACHE:
            del FILE_CACHE[self.path]
