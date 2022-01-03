from typing import Any, Dict

from filter.extension import ExtensionFilter
from filter.base import Filter
from filter.type import FilterType

class FilterFactory:
    _getters = {
        FilterType.EXTENSION: ExtensionFilter.from_data
    }
    
    @staticmethod
    def get(type: FilterType, data: Dict[str, Any]) -> Filter:
        return FilterFactory._getters[type](data)