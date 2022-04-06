# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A simple factory for producing Filters from type and param information

Note:
    Imports for custom Filters should be in the CUSTOM IMPORTS section.
    This will reduce merge conflicts when merging in upstream changes.
    Do not auto organize imports when using custom imports to avoid merge conflicts
"""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.filter.base import Filter, FilterBundle
from autotransform.filter.extension import ExtensionFilter
from autotransform.filter.regex import RegexFilter
from autotransform.filter.type import FilterType


class FilterFactory:
    """The factory class

    Attributes:
        _getters (Dict[FilterType, Callable[[Mapping[str, Any]], Filter]]): A mapping
            from FilterType to that filters's from_data function.

    Note:
        Custom filters should have their getters placed in the CUSTOM FILTERS section.
        This will reduce merge conflicts when merging in upstream changes.
    """

    # pylint: disable=too-few-public-methods

    _getters: Dict[FilterType, Callable[[bool, Mapping[str, Any]], Filter]] = {
        FilterType.EXTENSION: ExtensionFilter.from_data,
        FilterType.REGEX: RegexFilter.from_data,
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
        if bundle["type"] in FilterFactory._getters:
            return FilterFactory._getters[bundle["type"]](inverted, bundle["params"])

        custom_component_modules = Config.get_custom_component_imports()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "FILTERS") and bundle["type"] in module.FILTERS:
                return module.FILTERS[bundle["type"]](inverted, bundle["params"])
        raise ValueError(f"No filter found for type {bundle['type']}")
