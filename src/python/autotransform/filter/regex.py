# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for regex based filters, including RegexFilter and FileContentRegexFilter."""

from __future__ import annotations

import re
from typing import ClassVar

from autotransform.filter.base import Filter, FilterName
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class RegexFilter(Filter):
    """A Filter which only passes Items where the Item's key matches a provided regex pattern.
    Uses re.search rather than re.match.

    Attributes:
        pattern (str): The pattern to use when checking the Item's key.
        name (ClassVar[FilterName]): The name of the component.
    """

    pattern: str

    name: ClassVar[FilterName] = FilterName.REGEX

    def _is_valid(self, item: Item) -> bool:
        """Check whether the key contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        """

        return re.search(self.pattern, item.key) is not None


class RegexFileContentFilter(Filter):
    """A Filter which only passes FileItems where the file's content contains a match to the
    provided regex pattern. Uses re.search rather than re.match.

    Attributes:
        pattern (str): The pattern to use when checking the FileItem's content
        name (ClassVar[FilterName]): The name of the component.
    """

    pattern: str

    name: ClassVar[FilterName] = FilterName.REGEX_FILE_CONTENT

    def _is_valid(self, item: Item) -> bool:
        """Check whether the contents of the file contains the pattern.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the file's content.
        """

        assert isinstance(item, FileItem)
        return re.search(self.pattern, item.get_content()) is not None
