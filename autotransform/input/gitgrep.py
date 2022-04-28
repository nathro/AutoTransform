# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GitGrepInput."""

from __future__ import annotations

import subprocess
from typing import Any, Mapping, Sequence, TypedDict

from autotransform.input.base import Input
from autotransform.input.type import InputType
from autotransform.item.file import FileItem


class GitGrepInputParams(TypedDict):
    """The param type for a GitGrepInput."""

    pattern: str


class GitGrepInput(Input[GitGrepInputParams]):
    """An Input that uses git grep to search a repository for a pattern and returns all files
    that contain a match of the supplied pattern.

    Attributes:
        _params (GitGrepInputParams): Contains the arguments for doing a git grep search.
    """

    _params: GitGrepInputParams

    @staticmethod
    def get_type() -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input.
        """
        return InputType.GIT_GREP

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files using git grep that match the supplied pattern.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
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
            self._params["pattern"],
            "--",
            repo_dir,
        ]
        try:
            files = subprocess.check_output(git_grep_cmd, encoding="UTF-8").strip().splitlines()
        except subprocess.CalledProcessError:
            return []
        return [FileItem(repo_dir + "/" + file.replace("\\", "/")) for file in files]

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
