from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

from input.InputType import InputType

TParams = TypeVar('TParams')

class Input(Generic[TParams], ABC):
    def __init__(self, params: TParams):
        self.params = params
        
    @abstractmethod
    def getFiles(self) -> List[str]:
        pass
    
    @abstractmethod
    def getType(self) -> InputType:
        pass
            