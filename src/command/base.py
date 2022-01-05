from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, TypedDict

from batcher.base import Batch
from command.type import CommandType

class CommandBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: CommandType

class Command(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> CommandType:
        pass
        
    @abstractmethod
    def run(self, batch: Batch) -> None:
        pass
    
    def bundle(self) -> CommandBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Command:
        pass