from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

from batcher.type import BatcherType
from common.cachedfile import CachedFile

class Batch(TypedDict):
    files: List[int]
    metadata: Dict[str, Any] # must be JSON encodable/decodable

class BatcherBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: BatcherType

class Batcher(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Optional[Dict[str, Any]]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> BatcherType:
        pass
        
    @abstractmethod
    def batch(self, files: List[CachedFile]) -> List[Batch]:
        pass
    
    def bundle(self) -> BatcherBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Batcher:
        pass   