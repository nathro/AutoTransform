from typing import Any, Callable, Dict

from repo.base import Repo, RepoBundle
from repo.git import GitRepo
from repo.type import RepoType

class RepoFactory:
    _getters: Dict[RepoType, Callable[[Dict[str, Any]], Repo]] = {
        RepoType.GIT: GitRepo.from_data,
    }
    
    @staticmethod
    def get(repo: RepoBundle) -> Repo:
        return RepoFactory._getters[repo["type"]](repo["params"])