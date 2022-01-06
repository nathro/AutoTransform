#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Mapping

from autotransform.input.base import Input, InputParams
from autotransform.input.type import InputType

class DirectoryInputParams(InputParams):
    path: str

class DirectoryInput(Input[DirectoryInputParams]):
    files: List[str]
    
    def __init__(self, params: DirectoryInputParams):
        Input.__init__(self, params)
        self.files = []
        
    def get_type(self) -> InputType:
        return InputType.DIRECTORY
        
    def get_files(self) -> List[str]:
        def populate_files(input: DirectoryInput, path: Path) -> None:
            for file in path.iterdir():
                if file.is_file():
                    file_name: str = str(file.absolute().resolve())
                    input.files.append(file_name)
                else:
                    populate_files(input, file)

        if not self.files:
            populate_files(self, Path(self.params["path"]))
        return self.files
    
    @staticmethod
    def from_data(data: Mapping[str, Any]) -> DirectoryInput:
        path = data["path"]
        assert isinstance(path, str)
        return DirectoryInput({"path": path})