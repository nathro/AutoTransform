# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for file filters."""

from pathlib import Path
from typing import ClassVar

from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class FileExistsFilter(Filter):
    """A Filter which checks whether a File associated with the FileItem exists.

    Attributes:
        check_target_path (bool, optional): Check the target_path, rather than the key
            of the FileItem. Defaults to False.
        name (ClassVar[FilterName]): The name of the component.
    """

    check_target_path: bool = False
    name: ClassVar[FilterName] = FilterName.FILE_EXISTS

    def _is_valid(self, item: Item) -> bool:
        """Check whether the key contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        """

        if not isinstance(item, FileItem):
            return False

        path_to_check = (
            (item.extra_data or {}).get("target_path")
            if self.check_target_path
            else item.get_path()
        )

        if path_to_check is None or not isinstance(path_to_check, str):
            return False

        return Path(path_to_check).is_file()
