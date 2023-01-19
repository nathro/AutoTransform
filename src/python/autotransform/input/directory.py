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
from typing import Any, ClassVar, Dict, List, Sequence

from autotransform.input.base import Input, InputName
from autotransform.item.file import FileItem
from pydantic import root_validator


class DirectoryInput(Input):
    """An Input that lists all files recursively within a provided directory.

    Attributes:
        paths (List[str]): The paths of the directories to fetch all files within.
        name (ClassVar[InputName]): The name of the component.
    """

    paths: List[str]

    name: ClassVar[InputName] = InputName.DIRECTORY

    @root_validator(pre=True)
    @classmethod
    def path_legacy_setting_validator(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validates paths using legacy path setting.

        Args:
            values (Dict[str, Any]): The values used to configure the DirectoryInput.

        Raises:
            ValueError: Raised if both path and paths are supplied.

        Returns:
            Mapping[str, Any]: The fixed values.
        """

        if "path" in values:
            if "paths" in values:
                raise ValueError("Can not supply both path and paths for DirectoryInput")
            values["paths"] = set([str(values["path"])])
        values["paths"] = list(set(values["paths"]))
        return values

    @cached_property
    def _files(self) -> List[str]:
        """A cached list of files within the directory."""

        files = []
        for directory in self.paths:
            for path, _, dir_files in os.walk(Path(directory)):
                files.extend([f"{path}/{file}" for file in dir_files])
            # Clean up file paths for consistency of use
            files = [file.replace("\\", "/").removeprefix("./") for file in files]
        return files

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files recursively contained within the path.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
        """

        return [FileItem(key=file) for file in self._files]
