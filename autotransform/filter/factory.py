# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.filter.base import Filter, FilterBundle
from autotransform.filter.extension import ExtensionFilter
from autotransform.filter.type import FilterType

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class FilterFactory:
    # pylint: disable=too-few-public-methods

    _getters: Dict[FilterType, Callable[[bool, Mapping[str, Any]], Filter]] = {
        FilterType.EXTENSION: ExtensionFilter.from_data,
        # Section reserved for custom getters to reduce merge conflicts
        # BEGIN CUSTOM GETTERS
        # END CUSTOM GETTERS
    }

    @staticmethod
    def get(bundle: FilterBundle) -> Filter:
        inverted = bool(bundle.get("inverted", False))
        return FilterFactory._getters[bundle["type"]](inverted, bundle["params"])
