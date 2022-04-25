# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The base class and associated classes for Item components."""

from autotransform.item.base import Item
from autotransform.item.type import ItemType
from autotransform.util.cachedfile import CachedFile


class FileItem(Item):
    """An item representing a file that can be used by AutoTransform. Provides some utility methods
    for interacting with the file.

    Attributes:
        _extra_data (Mapping[str, Any]): Any extra data that needs to be associated with this Item.
            Should be JSON encodable.
        _key (str): A unique key used to represent this item, such as a file path.
    """

    @staticmethod
    def get_type() -> ItemType:
        """Used to map Item components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ItemType: The unique type associated with this Item.
        """

        return ItemType.FILE

    def get_path(self) -> str:
        """Gets the path of the file.

        Returns:
            str: The file's path.
        """

        return self._key

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
