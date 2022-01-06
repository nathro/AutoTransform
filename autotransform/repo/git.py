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
    
    PARENT_BRANCH: str = "AUTO_TRANSFORM_PARENT"
    COMMIT_BRANCH: str = "AUTO_TRANSFORM_CHILD"
    
    def __init__(self, params: GitRepoParams):
        Repo.__init__(self, params)
        self.local_repo = GitPython(self.params["path"])
        
    def get_type(self) -> RepoType:
        return RepoType.GIT
    
    def has_changes(self, batch: ConvertedBatch) -> bool:
        return self.local_repo.is_dirty(untracked_files=True)
        
    def submit(self, batch: ConvertedBatch) -> None:
        self.commit(batch)
        
    def commit(self, batch: ConvertedBatch) -> None:
        self.local_repo.create_head(GitRepo.PARENT_BRANCH)
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(batch["metadata"]["title"])
        self.local_repo.create_head(GitRepo.COMMIT_BRANCH)
    
    def clean(self, batch: ConvertedBatch) -> None:
        self.local_repo.git.reset('--hard')
    
    def rewind(self, batch: ConvertedBatch) -> None:
        self.clean(batch)
        heads = self.local_repo.heads
        parent = None
        commit = None
        for head in heads:
            if head.name == GitRepo.PARENT_BRANCH:
                parent = head
            elif head.name == GitRepo.COMMIT_BRANCH:
                commit = head
        assert isinstance(parent, Head)
        assert isinstance(commit, Head)
        parent.checkout()
        self.local_repo.delete_head(commit, force=True)
        self.local_repo.delete_head(parent, force=True)
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> GitRepo:
        path = data["path"]
        assert isinstance(path, str)
        return cls({"path": path})