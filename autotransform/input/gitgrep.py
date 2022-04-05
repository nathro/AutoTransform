# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the GitGrepInput."""

from __future__ import annotations

import subprocess
from typing import Any, List, Mapping, TypedDict

from autotransform.input.base import Input
from autotransform.input.type import InputType


class GitGrepInputParams(TypedDict):
    """The param type for a GitGrepInput."""

    pattern: str


class GitGrepInput(Input[GitGrepInputParams]):
    """A Input that lists all files recursively within a provided directory.

    Attributes:
        params (GitGrepInputParams): Contains the arguments for doing a git grep search
    """

    params: GitGrepInputParams

    def get_type(self) -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input
        """
        return InputType.GIT_GREP

    def get_files(self) -> List[str]:
        """Gets a list of files using git grep that match the supplied pattern

        Returns:
            List[str]: The eligible files for transformation
        """
        dir_cmd = ["git", "rev-parse", "--show-toplevel"]
        repo_dir = subprocess.check_output(dir_cmd, encoding="UTF-8").replace("\\", "/").strip()
        git_grep_cmd = [
            "git",
            "grep",
            "--full-name",
            "-l",
            "--untracked",
            "-e",
            self.params["pattern"],
            "--",
            repo_dir,
        ]
        try:
            files = subprocess.check_output(git_grep_cmd, encoding="UTF-8").strip().split("\n")
        except subprocess.CalledProcessError:
            return []
        return [repo_dir + "/" + file.replace("\\", "/") for file in files]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GitGrepInput:
        """Produces a GitGrepInput from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            GitGrepInput: An instance of the GitGrepInput with the provided params
        """
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        return GitGrepInput({"pattern": pattern})
