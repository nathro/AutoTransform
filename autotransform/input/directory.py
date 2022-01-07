# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Mapping, TypedDict

from autotransform.inputsource.base import Input
from autotransform.inputsource.type import InputType


class DirectoryInputParams(TypedDict):
    path: str


class DirectoryInput(Input):
    files: List[str]

    def __init__(self, params: DirectoryInputParams):
        Input.__init__(self, params)
        self.files = []

    def get_type(self) -> InputType:
        return InputType.DIRECTORY

    def populate_files(self, path: Path) -> None:
        for file in path.iterdir():
            if file.is_file():
                file_name: str = str(file.absolute().resolve())
                self.files.append(file_name)
            else:
                self.populate_files(file)

    def get_files(self) -> List[str]:
        if not self.files:
            self.populate_files(Path(self.params["path"]))
        return self.files

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> DirectoryInput:
        path = data["path"]
        assert isinstance(path, str)
        return DirectoryInput({"path": path})
