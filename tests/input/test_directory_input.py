import pathlib
from typing import Dict

from src.input.DirectoryInput import DirectoryInput, DirectoryInputParams

def test_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    input: DirectoryInput = DirectoryInput(DirectoryInputParams(dir + "/data/directory_input_test_empty_dir"))
    assert not input.getInput()
    
def test_non_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    input: DirectoryInput = DirectoryInput(DirectoryInputParams(dir + "/data/directory_input_test_non_empty_dir"))
    files: Dict[str, None] = input.getInput()
    assert (dir + "\\data\\directory_input_test_non_empty_dir\\test.txt") in files
    