# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""CachedFile is a utility class used by AutoTransform to cache file content on read/write to
reduce excessive file reads and speed up processing. The FILE_CACHE variable stores cached
file contents, while a CachedFile object is used to interact with the cache. All writes
should go through the CachedFile object to ensure the cache is properly updated."""

from typing import Dict

FILE_CACHE: Dict[str, str] = {}


class CachedFile:

    """A wrapper that allows accessing cached file contents. Content is stored in the
    FILE_CACHE variable. Writing files outside the CachedFile write method can lead to
    invalid cache data.

    Attributes:
        path (str): The path of the file being cached.
    """

    path: str

    def __init__(self, path: str):
        """A simple constructor.

        Args:
            path (str): The path of the file being cached.
        """

        self.path = path

    @staticmethod
    def _read(path: str) -> str:
        """A simple method to read the content of a file. Used as a hook for testing
        purposes. Simply handles reading and does not interact with the cache.

        Args:
            path (str): The path to read from.

        Returns:
            str: The content of the file.
        """

        # pylint: disable=unspecified-encoding

        with open(path, "r") as file:
            content = file.read()
        return content

    def get_content(self) -> str:
        """Gets the file contents from the cache if present. If not present, it will read the
        file contents and cache it before returning.

        Returns:
            str: The contents of the file represented by this object.
        """

        if self.path not in FILE_CACHE:
            FILE_CACHE[self.path] = self._read(self.path)
        return FILE_CACHE[self.path]

    @staticmethod
    def _write(path: str, content: str) -> None:
        """A simple private method to write new content to a file. Used as a hook for testing
        purposes. Simply handles writing and does not interact with the cache.

        Args:
            path (str): The path to write the file content to.
            content (str): The content to write to the file.
        """

        # pylint: disable=unspecified-encoding

        with open(path, "w") as file:
            file.write(content)
            file.flush()

    def write_content(self, new_content: str) -> None:
        """Updates the content of a cached file, including writing the file.

        Args:
            new_content (str): The content to put in the file.
        """

        # pylint: disable=unspecified-encoding

        self._write(self.path, new_content)
        FILE_CACHE[self.path] = new_content
