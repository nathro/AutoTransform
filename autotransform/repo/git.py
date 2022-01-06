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
from git import Repo as GitPython
from typing import Any, Dict, TypedDict

from git.refs.head import Head

from batcher.base import BatchMetadata, ConvertedBatch
from repo.base import Repo
from repo.type import RepoType

class GitRepoParams(TypedDict):
    path: str
    
class GitRepo(Repo):
    params: GitRepoParams
    local_repo: GitPython
    active_branch: Head
    
    COMMIT_BRANCH_BASE: str = "AUTO_TRANSFORM_COMMIT"
    
    @staticmethod
    def get_branch_name(title: str) -> str:
        return GitRepo.COMMIT_BRANCH_BASE + "_" + title.replace(" ", "_")
    
    def __init__(self, params: GitRepoParams):
        Repo.__init__(self, params)
        self.local_repo = GitPython(self.params["path"])
        self.active_branch = self.local_repo.active_branch
        
    def get_type(self) -> RepoType:
        return RepoType.GIT
    
    def has_changes(self, batch: ConvertedBatch) -> bool:
        return self.local_repo.is_dirty(untracked_files=True)
        
    def submit(self, batch: ConvertedBatch) -> None:
        self.commit(batch["metadata"])
    
    def commit(self, metadata: BatchMetadata) -> None:
        self.local_repo.git.checkout("-b", GitRepo.get_branch_name(metadata["title"]))
        self.local_repo.git.add(all=True)
        self.local_repo.index.commit(metadata["title"])
    
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