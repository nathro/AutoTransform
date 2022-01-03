from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Dict, List, TypeVar, Generic

from common.cachedfile import CachedFile
from filter.type import FilterType

TParams = TypeVar('TParams')

class Filter(Generic[TParams], ABC):
    def __init__(self, params: TParams):
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
    
    def bundle(self) -> Dict[str, Any]:
        return {
            "type": self.get_type(),
            "params": asdict(self.params)
        }
            