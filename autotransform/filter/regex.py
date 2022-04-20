# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for regex based filters, including RegexFilter and FileContentRegexFilter."""

from __future__ import annotations

import re
from typing import Any, Mapping, TypedDict

from autotransform.filter.base import Filter
from autotransform.filter.type import FilterType
from autotransform.util.cachedfile import CachedFile


class RegexFilterParams(TypedDict):
    """The param type for a RegexFilter."""

    pattern: str


class RegexFilter(Filter[RegexFilterParams]):
    """A Filter which only passes keys where the key matches a provided regex pattern.
    Uses re.search rather than re.match.

    Attributes:
        params (RegexFilterParams): Contains the pattern to check against the file name
    """

    _params: RegexFilterParams

    @staticmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """
        return FilterType.REGEX

    def _is_valid(self, key: str) -> bool:
        """Check whether the key contains the pattern in the params.

        Args:
            key (str): The key to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        """
        return re.search(self._params["pattern"], key) is not None

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

class FileContentRegexFilterParams(TypedDict):
    """The param type for a FileContentRegexFilter."""

    pattern: str


class FileContentRegexFilter(Filter[FileContentRegexFilterParams]):
    """A Filter which only passes keys where the key is a file path for a file containing
    content that matches the provided regex pattern. Uses re.search rather than re.match.

    Attributes:
        params (FileContentRegexFilterParams): Contains the pattern to check against the
            content of the file represented by the key.
    """

    _params: FileContentRegexFilterParams

    @staticmethod
    def get_type() -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter.
        """
        return FilterType.FILE_CONTENT_REGEX

    def _is_valid(self, key: str) -> bool:
        """Check whether the contents of the file represented by the key match the regex pattern
        in the parms.

        Args:
            key (str): The key to check.

        Returns:
            bool: Returns True if the pattern is found within the key.
        """
        file_content = CachedFile(key).get_content()
        return re.search(self._params["pattern"], file_content) is not None

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
