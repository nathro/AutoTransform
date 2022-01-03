from dataclasses import dataclass
from pathlib import Path
from typing import List

from input.Input import Input

@dataclass
class DirectoryInputParams:
    path: str

class DirectoryInput(Input[DirectoryInputParams]):
    
    def __init__(self, params: DirectoryInputParams):
        Input.__init__(self, params)
        self.files: List[str] = []
        
    def getInput(self) -> List[str]:
    
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