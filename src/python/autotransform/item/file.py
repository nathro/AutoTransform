# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the FileItem."""

from typing import ClassVar

from autotransform.item.base import Item, ItemName
from autotransform.util.cachedfile import CachedFile


class FileItem(Item):
    """An item representing a file that can be used by AutoTransform. Provides some utility methods
    for interacting with the file.

    Attributes:
        name (ClassVar[ItemName]): The name of the component.
    """

    name: ClassVar[ItemName] = ItemName.FILE

    def get_path(self) -> str:
        """Gets the path of the file.

        Returns:
            str: The file's path.
        """

        return self.key

    def get_content(self) -> str:
        """Gets the content of the file.

        Returns:
            str: The file's content.
        """

        return CachedFile(self.get_path()).get_content()

    def write_content(self, content: str) -> None:
        """Writes new content to the file.

        Args:
            content (str): The new content for the File.
        """

        CachedFile(self.get_path()).write_content(content)
