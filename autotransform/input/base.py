from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypedDict

from inputsource.type import InputType

class InputBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: InputType

class Input(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> InputType:
        pass
        
    @abstractmethod
    def get_files(self) -> List[str]:
        pass
    
    def bundle(self) -> InputBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Input:
        pass