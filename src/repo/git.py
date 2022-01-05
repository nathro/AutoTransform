from __future__ import annotations
from abc import ABC, abstractmethod
from git import Repo as GitPython
from typing import Any, Dict, Optional, TypedDict

from batcher.base import ConvertedBatch
from repo.base import Repo
from repo.type import RepoType

class GitRepoParams(TypedDict):
    path: str
    
class GitRepo(Repo):
    params: GitRepoParams
    repo: GitPython
    
    def __init__(self, params: GitRepoParams):
        Repo.__init__(self, params)
        self.repo = GitPython(self.params["path"])
        
    def get_type(self) -> RepoType:
        return RepoType.GIT
    
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
    def from_data(cls, data: Dict[str, Any]) -> GitRepo:
        path = data["path"]
        assert isinstance(path, str)
        return cls({"path": path})