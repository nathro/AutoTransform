# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the DirectoryInput."""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Mapping, Sequence, TypedDict

from autotransform.input.base import Input
from autotransform.input.type import InputType
from autotransform.item.file import FileItem


class DirectoryInputParams(TypedDict):
    """The param type for a DirectoryInput."""

    path: str


class DirectoryInput(Input[DirectoryInputParams]):
    """An Input that lists all files recursively within a provided directory.

    Attributes:
        _files (List[str]): A cached list of the files provided by the Input.
        _params (DirectoryInputParams): Contains the directory to walk.
    """

    _files: List[str]
    _params: DirectoryInputParams

    def __init__(self, params: DirectoryInputParams):
        """Initializes the files for the input to an empty list to be populated later.

        Args:
            params (DirectoryInputParams): The paramaters used to set up the DirectoryInput.
        """
        Input.__init__(self, params)
        self._files = []

    @staticmethod
    def get_type() -> InputType:
        """Used to map Input components 1:1 with an enum, allowing construction from JSON.

        Returns:
            InputType: The unique type associated with this Input.
        """
        return InputType.DIRECTORY

    def populate_files(self, path: Path) -> None:
        """Populates the file cache for this input. Recursively called to walk all directories
        under the path.

        Args:
            path (Path): The path from which to populate files.
        """
        for file in path.iterdir():
            if file.is_file():
                file_name: str = str(file.absolute().resolve())
                self._files.append(file_name)
            else:
                self.populate_files(file)

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files recursively contained within the path in the DirectoryInput params.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
        """
        if not self._files:
            self.populate_files(Path(self._params["path"]))
        return [FileItem(f) for f in self._files]

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> DirectoryInput:
        """Produces a DirectoryInput from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            DirectoryInput: An instance of the DirectoryInput with the provided params.
        """

        path = data["path"]
        assert isinstance(path, str)
        return DirectoryInput({"path": path})
