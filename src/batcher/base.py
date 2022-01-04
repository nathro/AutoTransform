from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

from batcher.type import BatcherType
from common.cachedfile import CachedFile

class BatchMetadata(TypedDict):
    pass

class Batch(TypedDict):
    files: List[int]
    metadata: BatchMetadata

class BatcherBundle(TypedDict):
    type: BatcherType
    params: Optional[Dict[str, Any]]

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
            "type": self.get_type(),
            "params": self.params
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Batcher:
        pass   