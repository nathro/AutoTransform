from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from input.base import Input
from input.type import InputType

@dataclass
class DirectoryInputParams:
    path: str

class DirectoryInput(Input[DirectoryInputParams]):
    
    def __init__(self, params: DirectoryInputParams):
        Input.__init__(self, params)
        self.files: List[str] = []
        
    def get_files(self) -> List[str]:
        def populate_files(input: DirectoryInput, path: Path) -> None:
            for file in path.iterdir():
                if file.is_file():
                    file_name: str = str(file.absolute().resolve())
                    input.files.append(file_name)
                else:
                    populate_files(input, file)

        if not self.files:
            populate_files(self, Path(self.params.path))
        return self.files
    
    def get_type(self) -> InputType:
        return InputType.DIRECTORY
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> DirectoryInput:
        path = data["path"]
        assert isinstance(path, str)
        return cls(DirectoryInputParams(path))