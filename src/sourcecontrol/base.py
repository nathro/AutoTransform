from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypedDict

from batcher.base import Batch
from sourcecontrol.type import SourceControlType

class SourceControlBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: SourceControlType

class SourceControl(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> SourceControlType:
        pass
    
    @abstractmethod
    def has_changes(self, batch: Batch) -> bool:
        pass
        
    @abstractmethod
    def submit(self, batch: Batch) -> None:
        pass
    
    @abstractmethod
    def clean(self, batch: Batch) -> None:
        pass
    
    @abstractmethod
    def rewind(self, batch: Batch) -> None:
        pass
    
    def bundle(self) -> SourceControlBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> SourceControl:
        pass