from __future__ import annotations
import json

from typing import List
from filter.base import Filter
from filter.factory import FilterFactory
from input.base import Input
from input.factory import InputFactory

class AutoTransformPackage:
    def __init__(self, input: Input, filters: List[Filter]):
        self.input = input
        self.filters = filters
        
    def to_json(self) -> str:
        package = {
            "input": self.input.bundle(),
            "filters": [filter.bundle() for filter in self.filters]
        }
        return json.dumps(package)
    
    @staticmethod
    def from_json(json_package: str) -> AutoTransformPackage:
        package = json.loads(json_package)
        input = package["input"]
        input = InputFactory.get(input["type"], input["params"])
        filters = package["filters"]
        filters = [FilterFactory.get(filter["type"], filter["params"]) for filter in filters]
        
        return AutoTransformPackage(input, filters)