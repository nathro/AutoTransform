#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.filter.extension import ExtensionFilter
from autotransform.filter.base import Filter, FilterBundle
from autotransform.filter.type import FilterType

class FilterFactory:
    _getters: Dict[FilterType, Callable[[bool, Mapping[str, Any]], Filter]] = {
        FilterType.EXTENSION: ExtensionFilter.from_data,
    }
    
    @staticmethod
    def get(filter: FilterBundle) -> Filter:
        inverted = bool(filter.get("inverted", False))
        return FilterFactory._getters[filter["type"]](inverted, filter["params"])