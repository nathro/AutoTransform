import pathlib
from typing import Dict

from autotransform.inputsource.directory import DirectoryInput, DirectoryInputParams

def test_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    inputsource: DirectoryInput = DirectoryInput(DirectoryInputParams(dir + "/data/directory_inputsource_test_empty_dir"))
    assert not inputsource.getInput()
    
def test_non_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    inputsource: DirectoryInput = DirectoryInput(DirectoryInputParams(dir + "/data/directory_inputsource_test_non_empty_dir"))
    files: Dict[str, None] = inputsource.getInput()
    assert (dir + "\\data\\directory_inputsource_test_non_empty_dir\\test.txt") in files
    