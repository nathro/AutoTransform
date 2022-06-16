# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the DirectoryInput."""

from __future__ import annotations

import os
from functools import cached_property
from pathlib import Path
from typing import ClassVar, List, Sequence

from autotransform.input.base import Input, InputName
from autotransform.item.file import FileItem


class DirectoryInput(Input):
    """An Input that lists all files recursively within a provided directory.

    Attributes:
        path (str): The path of the directory to fetch all files within.
        name (ClassVar[InputName]): The name of the component.
    """

    path: str

    name: ClassVar[InputName] = InputName.DIRECTORY

    @cached_property
    def _files(self) -> List[str]:
        """A cached list of files within the directory."""

        files = []
        for path, _, dir_files in os.walk(Path(self.path)):
            files.extend([f"{path}/{file}" for file in dir_files])
        files = [file.replace("\\", "/") for file in files]
        return files

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files recursively contained within the path.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
        """

        return [FileItem(key=file) for file in self._files]
