from __future__ import annotations
import re
from typing import Any, Dict, List, TypedDict

from common.cachedfile import CachedFile
from transformer.base import Transformer
from transformer.type import TransformerType

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
        output = open(file.path, "w")
        output.write(re.sub(self.params["pattern"], self.params["replacement"], file.get_content()))
        output.close()
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> RegexTransformer:
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        replacement = data["replacement"]
        assert isinstance(replacement, str)
        return cls({"pattern": pattern, "replacement": replacement})