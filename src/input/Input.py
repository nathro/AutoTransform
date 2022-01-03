from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

TParams = TypeVar('TParams')

class Input(Generic[TParams], ABC):
    def __init__(self, params: TParams):
        self.params = params
        
    @abstractmethod
    def getInput(self) -> List[str]:
        pass