# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the RegexFilter."""

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
    """A Filter which only passes files where the file name contains a match for the provided
    regex pattern. This uses re.search rather than re.match.

    Attributes:
        params (RegexFilterParams): Contains the pattern to check against the file name
    """

    params: RegexFilterParams

    def get_type(self) -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter
        """
        return FilterType.REGEX

    def _is_valid(self, file: CachedFile) -> bool:
        """Check whether a file name contains the provided regex pattern.

        Args:
            file (CachedFile): The file to check

        Returns:
            bool: Returns True if the pattern is found within the file path
        """
        return re.search(self.params["pattern"], file.path) is not None

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> RegexFilter:
        """Produces a RegexFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            RegexFilter: An instance of the RegexFilter with the provided params
        """
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        return RegexFilter({"pattern": pattern})
