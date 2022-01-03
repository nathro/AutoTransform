from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

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
            