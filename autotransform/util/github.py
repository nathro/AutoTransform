# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Github related utilities."""

from typing import Dict, Optional

from github import Github, Repository

from autotransform.config import fetcher as Config


class GithubUtils:
    """A class for utilities used to interact with Github. Stores instances of objects to prevent
    excessive API usage.

    Attributes:
        __github_object (Optional[Github]): An instance of the Github object of PyGithub.
        __github_repos (Dict[str, Repository.Repository]): A mapping of repo names to repos. Used
            for caching.
    """

    __github_object: Optional[Github] = None
    __github_repos: Dict[str, Repository.Repository] = {}

    BEGIN_SCHEMA: str = "<<<<BEGIN SCHEMA>>>>"
    END_SCHEMA: str = "<<<<END SCHEMA>>>>"

    BEGIN_BATCH: str = "<<<<BEGIN BATCH>>>>"
    END_BATCH: str = "<<<<END BATCH>>>>"

    @staticmethod
    def get_github_object() -> Github:
        """Authenticates with Github to allow API access via a token provided by AutoTransform
        configuration. If no token is provided a username + password will be used. Also allows
        use of a base URL for enterprise use cases. Stores the Github object for future use.

        Returns:
            Github: An object allowing interaction with the Github API.
        """

        if GithubUtils.__github_object is None:
            url = Config.get_credentials_github_base_url()
            token = Config.get_credentials_github_token()
            if token is not None:
                if url is not None:
                    GithubUtils.__github_object = Github(token, base_url=url)
                GithubUtils.__github_object = Github(token)
            elif url is not None:
                GithubUtils.__github_object = Github(
                    Config.get_credentials_github_username(),
                    Config.get_credentials_github_password(),
                    base_url=url,
                )
            else:
                GithubUtils.__github_object = Github(
                    Config.get_credentials_github_username(),
                    Config.get_credentials_github_password(),
                )
        return GithubUtils.__github_object

    @staticmethod
    def get_github_repo(repo_name: str) -> Repository.Repository:
        """Gets the Github repository being interacted with.

        Returns:
            Repository.Repository: The Github repository being interacted with.
        """

        if repo_name not in GithubUtils.__github_repos:
            GithubUtils.__github_repos[repo_name] = GithubUtils.get_github_object().get_repo(
                repo_name,
            )
        return GithubUtils.__github_repos[repo_name]
