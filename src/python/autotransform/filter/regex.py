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
from typing import Any, Mapping

from autotransform.filter.base import Filter, FilterParams
from autotransform.filter.type import FilterType
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class RegexFilterParams(FilterParams):
    """The param type for a RegexFilter."""

    pattern: str


class RegexFilter(Filter[RegexFilterParams]):
    """A Filter which only passes Items where the Item's key matches a provided regex pattern.
    Uses re.search rather than re.match.

    Attributes:
        _params (RegexFilterParams): Contains the pattern to check against the key.
    """

    _params: RegexFilterParams

    @staticmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """

        return FilterType.REGEX

    def _is_valid(self, item: Item) -> bool:
        """Check whether the key contains the pattern in the params.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        """

        return re.search(self._params["pattern"], item.get_key()) is not None

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> RegexFilter:
        """Produces a RegexFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            RegexFilter: An instance of the RegexFilter with the provided params.
        """

        pattern = data["pattern"]
        assert isinstance(pattern, str)
        return RegexFilter({"pattern": pattern})


class FileContentRegexFilterParams(FilterParams):
    """The param type for a FileContentRegexFilter."""

    pattern: str


class FileContentRegexFilter(Filter[FileContentRegexFilterParams]):
    """A Filter which only passes FileItems where the file's content contains a match to the
    provided regex pattern. Uses re.search rather than re.match.

    Attributes:
        _params (FileContentRegexFilterParams): Contains the pattern to check against the
            content of the file.
    """

    _params: FileContentRegexFilterParams

    @staticmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """

        return FilterType.FILE_CONTENT_REGEX

    def _is_valid(self, item: Item) -> bool:
        """Check whether the contents of the file match the regex pattern in the parms.

        Args:
            item (Item): The Item to check.

        Returns:
            bool: Returns True if the pattern is found within the file's content.
        """

        assert isinstance(item, FileItem)
        return re.search(self._params["pattern"], item.get_content()) is not None

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> FileContentRegexFilter:
        """Produces a FileContentRegexFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            FileContentRegexFilter: An instance of the FileContentRegexFilter with the provided
                params.
        """

        pattern = data["pattern"]
        assert isinstance(pattern, str)
        return FileContentRegexFilter({"pattern": pattern})
