# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Filters from type and param information

Note:
    Imports for custom Filters should be in the custom imports section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

from typing import Any, Callable, Dict, Mapping

from autotransform.filter.base import Filter, FilterBundle
from autotransform.filter.extension import ExtensionFilter
from autotransform.filter.type import FilterType

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class FilterFactory:
    """The factory class

    Attributes:
        _getters (Dict[FilterType, Callable[[Mapping[str, Any]], Filter]]): A mapping
            from FilterType to that filters's from_data function.

    Note:
        Custom components should have their getters placed in the custom filters section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[FilterType, Callable[[bool, Mapping[str, Any]], Filter]] = {
        FilterType.EXTENSION: ExtensionFilter.from_data,
        # Section reserved for custom getters to reduce merge conflicts
        # BEGIN CUSTOM FILTERS
        # END CUSTOM FILTERS
    }

    @staticmethod
    def get(bundle: FilterBundle) -> Filter:
        """Simple get method using the _getters attribute

        Args:
            bundle (FilterBundle): The decoded bundle from which to produce a Filter instance

        Returns:
            Filter: The Filter instance of the decoded bundle
        """
        inverted = bool(bundle.get("inverted", False))
        return FilterFactory._getters[bundle["type"]](inverted, bundle["params"])
