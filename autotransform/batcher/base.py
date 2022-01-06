#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Generic, List, Mapping, Optional, TypeVar, TypedDict

from autotransform.batcher.type import BatcherType
from autotransform.common.cachedfile import CachedFile

class BatchMetadata(TypedDict):
    title: str
    summary: Optional[str]
    tests: Optional[str]

class Batch(TypedDict):
    files: List[int]
    metadata: BatchMetadata
    
class BatchWithFiles(TypedDict):
    files: List[CachedFile]
    metadata: BatchMetadata
    
class BatcherParams(TypedDict):
    pass

class BatcherBundle(TypedDict):
    params: BatcherParams
    type: BatcherType

T = TypeVar("T", bound=BatcherParams)

class Batcher(Generic[T], ABC):
    params: T
    
    def __init__(self, params: T):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> BatcherType:
        pass
        
    @abstractmethod
    def batch(self, files: List[CachedFile]) -> List[Batch]:
        pass
    
    def bundle(self) -> BatcherBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Batcher:
        pass   