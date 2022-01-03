from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from common.cachedfile import CachedFile
from filter.base import Filter
from filter.type import FilterType

class Extensions(str, Enum):
    PYTHON = ".py"
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 

@dataclass
class ExtensionFilterParams:
    extensions: List[Extensions]

class ExtensionFilter(Filter[ExtensionFilterParams]):
    
    def __init__(self, params: ExtensionFilterParams):
        Filter.__init__(self, params)
        
    def is_valid(self, file: CachedFile) -> bool:
        for extension in self.params.extensions:
            if file.path.endswith(extension):
                return True
        return False
            
    
    def get_type(self) -> FilterType:
        return FilterType.EXTENSION
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> ExtensionFilter:
        extensions = data["extensions"]
        assert isinstance(extensions, List)
        for extension in extensions:
            assert Extensions.has_value(extension)
        return cls(ExtensionFilterParams(extensions))