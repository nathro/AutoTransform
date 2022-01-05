from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

from common.cachedfile import CachedFile
from transformer.type import TransformerType

class TransformerBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: TransformerType

class Transformer(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> TransformerType:
        pass
        
    @abstractmethod
    def transform(self, file: CachedFile) -> None:
        pass
    
    def bundle(self) -> TransformerBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Transformer:
        pass