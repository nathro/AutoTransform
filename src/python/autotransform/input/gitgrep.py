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
from typing import ClassVar, Sequence

from autotransform.input.base import Input, InputName
from autotransform.item.file import FileItem


class GitGrepInput(Input):
    """An Input that uses git grep to search a repository for a pattern and returns all files
    that contain a match of the supplied pattern.

    Attributes:
        pattern (str): The pattern to search git grep for.
        name (ClassVar[InputName]): The name of the component.
    """

    pattern: str

    name: ClassVar[InputName] = InputName.GIT_GREP

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files using git grep that match the supplied pattern.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
        """

        git_grep_cmd = [
            "git",
            "grep",
            "--full-name",
            "-l",
            "--untracked",
            "-e",
            self.pattern,
        ]

        try:
            files = subprocess.check_output(git_grep_cmd, encoding="UTF-8").strip().splitlines()
        except subprocess.CalledProcessError:
            return []
        return [FileItem(key=file.replace("\\", "/")) for file in files]
