from typing import Any, Dict

from batcher.base import Batcher, BatcherBundle
from batcher.single import SingleBatcher
from batcher.type import BatcherType

class BatcherFactory:
    _getters = {
        BatcherType.SINGLE: SingleBatcher.from_data
    }
    
    @staticmethod
    def get(batcher: BatcherBundle) -> Batcher:
        return BatcherFactory._getters[batcher["type"]](batcher["params"])