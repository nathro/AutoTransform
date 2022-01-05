from __future__ import annotations
from abc import ABC, abstractmethod
from git import Repo
from typing import Any, Dict, Optional, TypedDict

from batcher.base import ConvertedBatch
from sourcecontrol.base import SourceControl
from sourcecontrol.type import SourceControlType

class GitSourceControlParams(TypedDict):
    path: str
    
class GitSourceControl(SourceControl):
    params: GitSourceControlParams
    
    def __init__(self, params: GitSourceControlParams):
        SourceControl.__init__(self, params)
        self.repo = Repo(self.params["path"])
        
    def get_type(self) -> SourceControlType:
        return SourceControlType.GIT
    
    def has_changes(self, batch: ConvertedBatch) -> bool:
        return self.repo.is_dirty(untracked_files=True)
        
    def submit(self, batch: ConvertedBatch) -> None:
        self.repo.git.add(all=True)
        self.repo.index.commit(batch["metadata"]["message"])
    
    def clean(self, batch: ConvertedBatch) -> None:
        self.repo.git.reset('--hard')
    
    def rewind(self, batch: ConvertedBatch) -> None:
        self.clean(batch)
        master = self.repo.head.commit
        prev = master.parents[0]
        self.repo.git.checkout(str(prev))
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> GitSourceControl:
        path = data["path"]
        assert isinstance(path, str)
        return cls({"path": path})