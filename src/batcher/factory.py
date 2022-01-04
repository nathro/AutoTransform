from typing import Any, Dict

from batcher.base import Batcher
from batcher.single import SingleBatcher
from batcher.type import BatcherType

class BatcherFactory:
    _getters = {
        BatcherType.SINGLE: SingleBatcher.from_data
    }
    
    @staticmethod
    def get(type: BatcherType, data: Dict[str, Any]) -> Batcher:
        return BatcherFactory._getters[type](data)