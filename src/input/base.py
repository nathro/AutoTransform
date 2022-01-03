from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import asdict
from typing import Any, Dict, List, TypeVar, Generic

from input.type import InputType

TParams = TypeVar('TParams')

class Input(Generic[TParams], ABC):
    def __init__(self, params: TParams):
        self.params = params
        
    @abstractmethod
    def get_files(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_type(self) -> InputType:
        pass
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Input:
        pass
    
    def bundle(self) -> Dict[str, Any]:
        return {
            "type": self.get_type(),
            "params": asdict(self.params)
        }
            