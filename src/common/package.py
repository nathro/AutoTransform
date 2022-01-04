from __future__ import annotations
import json
from typing import List

from batcher.base import Batcher
from batcher.factory import BatcherFactory
from filter.base import Filter
from filter.factory import FilterFactory
from input.base import Input
from input.factory import InputFactory

class AutoTransformPackage:
    input: Input
    filters: List[Filter]
    batcher: Batcher
    
    def __init__(self, input: Input, filters: List[Filter], batcher: Batcher):
        self.input = input
        self.filters = filters
        self.batcher = batcher
        
    def to_json(self) -> str:
        package = {
            "input": self.input.bundle(),
            "filters": [filter.bundle() for filter in self.filters],
            "batcher": self.batcher.bundle()
        }
        return json.dumps(package)
    
    @staticmethod
    def from_json(json_package: str) -> AutoTransformPackage:
        package = json.loads(json_package)
        input = InputFactory.get(package["input"])
        filters = [FilterFactory.get(filter) for filter in package["filters"]]
        batcher = BatcherFactory.get(package["batcher"])
        
        return AutoTransformPackage(input, filters, batcher)