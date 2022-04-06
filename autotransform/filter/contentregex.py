# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the ContentRegexFilter."""

from __future__ import annotations

import re
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.filter.base import Filter
from autotransform.filter.type import FilterType


class ContentRegexFilterParams(TypedDict):
    """The param type for a ContentRegexFilter."""

    pattern: str


class ContentRegexFilter(Filter[ContentRegexFilterParams]):
    """A Filter which only passes files where the file content contains a match for the provided
    regex pattern. This uses re.search rather than re.match.

    Attributes:
        params (ContentRegexFilterParams): Contains the pattern to check against the file content
    """

    params: ContentRegexFilterParams

    def get_type(self) -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter
        """
        return FilterType.CONTENT_REGEX

    def _is_valid(self, file: CachedFile) -> bool:
        """Check whether a file's content contains the provided regex pattern.

        Args:
            file (CachedFile): The file to check

        Returns:
            bool: Returns True if the pattern is found within the file path
        """
        return re.search(self.params["pattern"], file.get_content()) is not None

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> ContentRegexFilter:
        """Produces a ContentRegexFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            ContentRegexFilter: An instance of the ContentRegexFilter with the provided params
        """
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        return ContentRegexFilter({"pattern": pattern})
