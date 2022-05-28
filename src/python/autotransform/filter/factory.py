# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Filters from type and param information."""

import importlib
from typing import Dict, Type

from autotransform.config import fetcher as Config
from autotransform.filter.base import Filter, FilterBundle
from autotransform.filter.key_hash_shard import KeyHashShardFilter
from autotransform.filter.regex import FileContentRegexFilter, RegexFilter
from autotransform.filter.type import FilterType


class FilterFactory:
    """The factory class for Filters. Maps a type to a Filter.

    Attributes:
        _map (Dict[FilterType, Callable[[Mapping[str, Any]], Filter]]): A mapping from
            FilterType to the from_data function of the appropriate Filter.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[FilterType, Type[Filter]] = {
        FilterType.FILE_CONTENT_REGEX: FileContentRegexFilter,
        FilterType.KEY_HASH_SHARD: KeyHashShardFilter,
        FilterType.REGEX: RegexFilter,
    }

    @staticmethod
    def get(bundle: FilterBundle) -> Filter:
        """Simple get method using the _map attribute.

        Args:
            bundle (FilterBundle): The bundled Filter type and params.

        Returns:
            Filter: An instance of the associated Filter.
        """

        if bundle["type"] in FilterFactory._map:
            return FilterFactory._map[bundle["type"]].from_data(bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "FILTERS") and bundle["type"] in module.FILTERS:
                class_type = module.FILTERS[bundle["type"]]
                assert isinstance(class_type, type), "Imported component must be a Type"
                assert issubclass(class_type, Filter), "Imported component must be a Filter"
                return class_type.from_data(bundle["params"])
        raise ValueError(f"No Filter found for type {bundle['type']}")
