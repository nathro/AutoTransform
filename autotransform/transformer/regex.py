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
import re
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.base import Transformer
from autotransform.transformer.type import TransformerType

class RegexTransformerParams(TypedDict):
    pattern: str
    replacement: str

class RegexTransformer(Transformer):
    params: RegexTransformerParams
    
    def __init__(self, params: RegexTransformerParams):
        Transformer.__init__(self, params)
        
    def get_type(self) -> TransformerType:
        return TransformerType.REGEX
    
    def transform(self, file: CachedFile) -> None:
        content = file.get_content()
        output = open(file.path, "w")
        new_content = re.sub(self.params["pattern"], self.params["replacement"], content)
        output.write(new_content)
        output.close()
    
    @staticmethod
    def from_data(data: Mapping[str, Any]) -> RegexTransformer:
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        replacement = data["replacement"]
        assert isinstance(replacement, str)
        return RegexTransformer({"pattern": pattern, "replacement": replacement})