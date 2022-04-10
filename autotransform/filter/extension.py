# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the ExtensionFilter."""

from __future__ import annotations

from enum import Enum
from typing import Any, List, Mapping, Sequence, TypedDict

from autotransform.filter.base import Filter
from autotransform.filter.type import FilterType
from autotransform.util.cachedfile import CachedFile


class Extensions(str, Enum):
    """A list of extensions for eash use by the Extension filter"""

    PYTHON = ".py"
    TEXT = ".txt"


class ExtensionFilterParams(TypedDict):
    """The param type for a ExtensionFilter."""

    extensions: Sequence[Extensions]


class ExtensionFilter(Filter[ExtensionFilterParams]):
    """A Filter which only passes files ending with one of a set of extensions.

    Attributes:
        params (ExtensionFilterParams): Contains the extensions that are considered valid
    """

    params: ExtensionFilterParams

    def get_type(self) -> FilterType:
        """Used to map Filter components 1:1 with an enum, allowing construction from JSON.

        Returns:
            FilterType: The unique type associated with this Filter
        """
        return FilterType.EXTENSION

    def _is_valid(self, file: CachedFile) -> bool:
        """Check whether a file ends with one of the allowed extensions.

        Args:
            file (CachedFile): The file to check

        Returns:
            bool: Returns True if the file ends with any of the allowed extensions
        """
        for extension in self.params["extensions"]:
            file_name = file.path.replace("\\", "/").split("/")[-1]
            if file_name.endswith(extension) and file_name != extension:
                return True
        return False

    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> ExtensionFilter:
        """Produces a ExtensionFilter from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            ExtensionFilter: An instance of the ExtensionFilter with the provided params
        """
        extensions = data["extensions"]
        assert isinstance(extensions, List)
        for extension in extensions:
            assert isinstance(extension, str)
        return ExtensionFilter({"extensions": extensions})
