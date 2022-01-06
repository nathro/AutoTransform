#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from configparser import ConfigParser
from git import Repo as GitPython
from github import Github
import pathlib

from batcher.base import ConvertedBatch
from repo.git import GitRepo, GitRepoParams

class GitHubRepoParams(GitRepoParams):
    full_github_name: str

class GitHubRepo(GitRepo):
    params: GitHubRepoParams
    local_repo: GitPython
    github: Github
    
    def __init__(self, params: GitRepoParams):
        GitRepo.__init__(self, params)
        self.github = GitHubRepo.get_github_object()
        
    @staticmethod
    def get_github_object() -> Github:
        config_path: str = str(pathlib.Path(__file__).parent.parent.parent.resolve()) + "\\config.ini"
        config = ConfigParser()
        config.read(config_path)
        credentials = config['CREDENTIALS']
        url = credentials.get("github_base_url", None)
        token = credentials.get("github_token", None)
        if token != None:
            if url != None:
                return Github(token, base_url=url)
            return Github(token)
        if url != None:
            return Github(credentials["github_username"], credentials["github_password"], base_url=url)
        return Github(credentials["github_username"], credentials["github_password"])
    
    def submit(self, batch: ConvertedBatch) -> None:
        title = batch["metadata"]["title"]
        summary = batch["metadata"].get("summary", "")
        tests = batch["metadata"].get("tests", "")
        
        self.commit(batch["metadata"])
        
        commit_branch = GitRepo.get_branch_name(title)
        remote = self.local_repo.remote()
        self.local_repo.git.push(remote.name, '-u', commit_branch)
        
        github_repo = self.github.get_repo(self.params["full_github_name"])
        body= f'''
            SUMMARY
            {summary}
            
            TESTS
            {tests}
        '''
        pr = github_repo.create_pull(title=title, body=body, base=self.active_branch.name, head=commit_branch)