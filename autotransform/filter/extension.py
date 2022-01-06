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
from enum import Enum
from typing import Any, Dict, List, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.filter.base import Filter
from autotransform.filter.type import FilterType

class Extensions(str, Enum):
    PYTHON = ".py"
    TEXT = ".txt"
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 

class ExtensionFilterParams(TypedDict):
    extensions: List[Extensions]

class ExtensionFilter(Filter):
    params: ExtensionFilterParams
    
    def __init__(self, params: ExtensionFilterParams):
        Filter.__init__(self, params)
    
    def get_type(self) -> FilterType:
        return FilterType.EXTENSION
        
    def _is_valid(self, file: CachedFile) -> bool:
        for extension in self.params["extensions"]:
            if file.path.endswith(extension):
                return True
        return False
    
    @staticmethod
    def _from_data(data: Mapping[str, Any]) -> ExtensionFilter:
        extensions = data["extensions"]
        assert isinstance(extensions, List)
        for extension in extensions:
            assert Extensions.has_value(extension)
        return ExtensionFilter({"extensions": extensions})