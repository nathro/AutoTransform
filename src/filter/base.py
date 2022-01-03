from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypedDict

from common.cachedfile import CachedFile
from filter.type import FilterType

class FilterBundle(TypedDict):
    type: FilterType
    params: Optional[Dict[str, Any]]

class Filter(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Optional[Dict[str, Any]]):
        self.params = params
        
    @abstractmethod
    def is_valid(self, file: CachedFile) -> bool:
        pass
    
    @abstractmethod
    def get_type(self) -> FilterType:
        pass
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Filter:
        pass
    
    def bundle(self) -> FilterBundle:
        return {
            "type": self.get_type(),
            "params": self.params
        }
            