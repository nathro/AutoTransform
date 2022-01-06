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
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.type import TransformerType

class TransformerBundle(TypedDict):
    params: Mapping[str, Any]
    type: TransformerType

class Transformer(ABC):
    params: Mapping[str, Any]
    
    def __init__(self, params: Mapping[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> TransformerType:
        pass
        
    @abstractmethod
    def transform(self, file: CachedFile) -> None:
        pass
    
    def bundle(self) -> TransformerBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @staticmethod
    @abstractmethod
    def from_data(data: Mapping[str, Any]) -> Transformer:
        pass