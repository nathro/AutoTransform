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

    @staticmethod
    def _read(path: str) -> str:
        """A simple private method to read the content of a file. Used as a hook for testing
        purposes.

        Args:
            path (str): The path to read from

        Returns:
            str: The content of the file
        """

        # pylint: disable=unspecified-encoding

        with open(path, "r") as file:
            content = file.read()
        return content

    def get_content(self) -> str:
        """Gets the file contents from the cache if present. If not present, it will read the
        file contents and cache it.

        Returns:
            str: The contents of the file
        """
        if self.path not in FILE_CACHE:
            FILE_CACHE[self.path] = self._read(self.path)
        return FILE_CACHE[self.path]

    @staticmethod
    def _write(path: str, content: str) -> None:
        """A simple private method to write new content to a file. Used as a hook for testing
        purposes.

        Args:
            path (str): The path of the file to write
            content (str): The content to write to the file
        """

        # pylint: disable=unspecified-encoding

        with open(path, "w") as output:
            output.write(content)

    def write_content(self, new_content: str) -> None:
        """Updates the content of a cached file, including writing the file.

        Args:
            new_content (str): The content to put in the file
        """

        # pylint: disable=unspecified-encoding

        self._write(self.path, new_content)
        FILE_CACHE[self.path] = new_content

    def __del__(self):
        if self.path in FILE_CACHE:
            del FILE_CACHE[self.path]
