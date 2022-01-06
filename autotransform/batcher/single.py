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
from typing import Any, Dict, List, Mapping, TypedDict

from autotransform.batcher.base import Batch, Batcher, BatchMetadata
from autotransform.batcher.type import BatcherType
from autotransform.common.cachedfile import CachedFile

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
    
    @staticmethod
    def from_data(data: Mapping[str, Any]) -> SingleBatcher:
        metadata = data["metadata"]
        assert isinstance(metadata, Dict)
        title = metadata["title"]
        assert isinstance(title, str)
        if "summary" in metadata:
            summary = metadata["summary"]
            assert isinstance(summary, str)
        else:
            summary = None
        if "tests" in metadata:
            tests = metadata["tests"]
            assert isinstance(tests, str)
        else:
            tests = None
        return SingleBatcher(
            {
                "metadata": {
                    "title": title,
                    "summary": summary,
                    "tests": tests,
                }
            }
        )