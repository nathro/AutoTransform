#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import pathlib
from typing import Dict

from autotransform.input.directory import DirectoryInput, DirectoryInputParams

def test_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    input: DirectoryInput = DirectoryInput({"path": dir + "/data/directory_input_test_empty_dir"})
    assert not input.getInput()
    
def test_non_empty_dir():
    dir: str = str(pathlib.Path(__file__).parent.resolve())
    input: DirectoryInput = DirectoryInput({"path": dir + "/data/directory_input_test_non_empty_dir"})
    files: Dict[str, None] = input.getInput()
    assert (dir + "\\data\\directory_input_test_non_empty_dir\\test.txt") in files
    