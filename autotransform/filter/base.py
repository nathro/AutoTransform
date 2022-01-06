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
from typing import Any, Dict, Optional, TypedDict

from common.cachedfile import CachedFile
from filter.type import FilterType

class FilterBundle(TypedDict):
    inverted: Optional[bool]
    params: Optional[Dict[str, Any]]
    type: FilterType

class Filter(ABC):
    inverted: bool
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Optional[Dict[str, Any]]):
        self.inverted = False
        self.params = params
        
    @abstractmethod
    def get_type(self) -> FilterType:
        pass
        
    def invert(self) -> Filter:
        self.inverted = not self.inverted
        return self
        
    def is_valid(self, file: CachedFile) -> bool:
        return self.inverted != self._is_valid(file)
        
    @abstractmethod
    def _is_valid(self, file: CachedFile) -> bool:
        pass
    
    def bundle(self) -> FilterBundle:
        return {
            "inverted": self.inverted,
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    def from_data(cls, inverted: bool, data: FilterBundle) -> Filter:
        filter = cls._from_data(data)
        if inverted:
            filter.invert()
        return filter
    
    @classmethod
    @abstractmethod
    def _from_data(cls, data: FilterBundle) -> Filter:
        pass