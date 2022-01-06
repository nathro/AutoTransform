from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, TypedDict

from inputsource.base import Input
from inputsource.type import InputType

class DirectoryInputParams(TypedDict):
    path: str

class DirectoryInput(Input):
    files: List[str]
    params: DirectoryInputParams
    
    def __init__(self, params: DirectoryInputParams):
        Input.__init__(self, params)
        self.files = []
        
    def get_type(self) -> InputType:
        return InputType.DIRECTORY
        
    def get_files(self) -> List[str]:
        def populate_files(inputsource: DirectoryInput, path: Path) -> None:
            for file in path.iterdir():
                if file.is_file():
                    file_name: str = str(file.absolute().resolve())
                    inputsource.files.append(file_name)
                else:
                    populate_files(inputsource, file)

        if not self.files:
            populate_files(self, Path(self.params["path"]))
        return self.files
    
    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> DirectoryInput:
        path = data["path"]
        assert isinstance(path, str)
        return cls({"path": path})