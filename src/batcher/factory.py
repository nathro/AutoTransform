from typing import Any, Callable, Dict

from batcher.base import Batcher, BatcherBundle
from batcher.single import SingleBatcher
from batcher.type import BatcherType

class BatcherFactory:
    _getters: Dict[BatcherType, Callable[[Dict[str, Any]], Batcher]] = {
        BatcherType.SINGLE: SingleBatcher.from_data
    }
    
    @staticmethod
    def get(batcher: BatcherBundle) -> Batcher:
        return BatcherFactory._getters[batcher["type"]](batcher["params"])