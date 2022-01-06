from __future__ import annotations
from git import Repo as GitPython
from typing import Any, Dict, TypedDict

from git.refs.head import Head

from batcher.base import ConvertedBatch
from repo.base import Repo
from repo.type import RepoType

class GitRepoParams(TypedDict):
    path: str
    
class GitRepo(Repo):
    params: GitRepoParams
    local_repo: GitPython
    active_branch: Head
    
    COMMIT_BRANCH_BASE: str = "AUTO_TRANSFORM_COMMIT"
    
    def __init__(self, params: GitRepoParams):
        Repo.__init__(self, params)
        self.local_repo = GitPython(self.params["path"])
        self.active_branch = self.local_repo.active_branch
        
    def get_type(self) -> RepoType:
        return RepoType.GIT
    
    def has_changes(self, batch: ConvertedBatch) -> bool:
        return self.local_repo.is_dirty(untracked_files=True)
        
    def submit(self, batch: ConvertedBatch) -> None:
        self.commit(batch)
        
    def commit(self, batch: ConvertedBatch) -> None:
        self.local_repo.git.checkout("-b " + GitRepo.COMMIT_BRANCH_BASE + ": " + batch["metadata"]["title"])
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(batch["metadata"]["title"])
    
    def clean(self, batch: ConvertedBatch) -> None:
        self.local_repo.git.reset('--hard')
    
    def rewind(self, batch: ConvertedBatch) -> None:
        self.clean(batch)
        self.local_repo.active_branch.checkout()
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> GitRepo:
        path = data["path"]
        assert isinstance(path, str)
        return cls({"path": path})