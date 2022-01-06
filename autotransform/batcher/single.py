from __future__ import annotations
from typing import Any, Dict, List, TypedDict

from batcher.base import Batch, Batcher, BatchMetadata
from batcher.type import BatcherType
from common.cachedfile import CachedFile

class SingleBatcherParams(TypedDict):
    metadata: BatchMetadata

class SingleBatcher(Batcher):
    params: SingleBatcherParams
    
    def __init__(self, params: SingleBatcherParams):
        Batcher.__init__(self, params)
        
    def get_type(self) -> BatcherType:
        return BatcherType.SINGLE
        
    def batch(self, files: List[CachedFile]) -> List[Batch]:
        batch: Batch = {
            "files": list(range(len(files))),
            "metadata": self.params["metadata"],
        }
        return [batch]
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> SingleBatcher:
        metadata = data["metadata"]
        assert isinstance(metadata, Dict)
        assert isinstance(metadata["title"], str)
        if "summary" in metadata and metadata["tests"] != None:
            assert isinstance(metadata["summary"], str)
        if "tests" in metadata and metadata["tests"] != None:
            assert isinstance(metadata["tests"], str)
        return cls({"metadata": metadata})