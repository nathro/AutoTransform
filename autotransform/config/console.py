# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>


from getpass import getpass
from typing import Dict, Optional

from autotransform.config.fetcher import ConfigFetcher


class ConsoleConfigFetcher(ConfigFetcher):
    config: Dict[str, Optional[str]]

    def __init__(self):
        self.config = {}

    def get_github_token(self) -> Optional[str]:
        if "github_token" in self.config:
            return self.config["github_token"]
        token: Optional[str] = getpass("Github Token(empty to use username and password): ")
        if token == "":
            token = None
        self.config["github_token"] = token
        return token

    def get_github_username(self) -> Optional[str]:
        if "github_username" in self.config:
            return self.config["github_username"]
        username: Optional[str] = input("Github Username: ")
        if username == "":
            username = None
        self.config["github_username"] = username
        return username

    def get_github_password(self) -> Optional[str]:
        if "github_password" in self.config:
            return self.config["github_password"]
        password: Optional[str] = getpass("Github Password: ")
        if password == "":
            password = None
        self.config["github_password"] = password
        return password

    def get_github_base_url(self) -> Optional[str]:
        if "github_base_url" in self.config:
            return self.config["github_base_url"]
        base_url: Optional[str] = input("Github Base URL(empty for default): ")
        if base_url == "":
            base_url = None
        self.config["github_base_url"] = base_url
        return base_url
