from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic

from filter.type import FilterType

TParams = TypeVar('TParams')

class Filter(Generic[TParams], ABC):
    def __init__(self, params: TParams):
        self.params = params
        
    @abstractmethod
    def is_valid(self, file: str) -> bool:
        pass
    
    @abstractmethod
    def get_type(self) -> FilterType:
        pass
            