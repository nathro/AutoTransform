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
from typing import Any, Dict, List, Optional, TypedDict

from batcher.type import BatcherType
from common.cachedfile import CachedFile

class BatchMetadata(TypedDict):
    title: str
    summary: Optional[str]
    tests: Optional[str]

class Batch(TypedDict):
    files: List[int]
    metadata: BatchMetadata
    
class ConvertedBatch(TypedDict):
    files: List[CachedFile]
    metadata: BatchMetadata

class BatcherBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: BatcherType

class Batcher(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Optional[Dict[str, Any]]):
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
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Batcher:
        pass   