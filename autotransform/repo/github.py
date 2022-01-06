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
            return Github(token, base_url=url)
        return Github(credentials["github_username"], credentials["github_password"], base_url=url)
    
    def submit(self, batch: ConvertedBatch) -> None:
        self.commit()
        title = batch["metadata"]["title"]
        summary = batch["metadata"].get("summary", "")
        tests = batch["metadata"].get("tests", "")
        github_repo = self.github.get_repo(self.params["full_github_name"])
        body= f'''
            SUMMARY
            {summary}
            
            TESTS
            {tests}
        '''
        pr = github_repo.create_pull(title=title, body=body, head=GitRepo.get_branch_name(title), base=self.active_branch.name)