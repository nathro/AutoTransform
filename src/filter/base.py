from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypedDict

from common.cachedfile import CachedFile
from filter.type import FilterType

class FilterBundle(TypedDict):
    inverted: Optional[bool]
    params: Optional[Dict[str, Any]]
    type: FilterType

class Filter(ABC):
    inverted: bool
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Optional[Dict[str, Any]]):
        self.inverted = False
        self.params = params
        
    @abstractmethod
    def get_type(self) -> FilterType:
        pass
        
    def invert(self) -> Filter:
        self.inverted = not self.inverted
        return self
        
    def is_valid(self, file: CachedFile) -> bool:
        return self.inverted != self._is_valid(file)
        
    @abstractmethod
    def _is_valid(self, file: CachedFile) -> bool:
        pass
    
    def bundle(self) -> FilterBundle:
        return {
            "inverted": self.inverted,
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    def from_data(cls, inverted: bool, data: FilterBundle) -> Filter:
        filter = cls._from_data(data)
        if inverted:
            filter.invert()
        return filter
    
    @classmethod
    @abstractmethod
    def _from_data(cls, data: FilterBundle) -> Filter:
        pass