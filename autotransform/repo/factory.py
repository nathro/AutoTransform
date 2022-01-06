#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Callable, Dict, Mapping

from autotransform.repo.base import Repo, RepoBundle
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.repo.type import RepoType

class RepoFactory:
    _getters: Dict[RepoType, Callable[[Mapping[str, Any]], Repo]] = {
        RepoType.GIT: GitRepo.from_data,
        RepoType.GITHUB: GithubRepo.from_data,
    }
    
    @staticmethod
    def get(repo: RepoBundle) -> Repo:
        return RepoFactory._getters[repo["type"]](repo["params"])