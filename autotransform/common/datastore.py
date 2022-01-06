#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Dict, Optional

from autotransform.common.dataobject import FileDataObject

class FileDataStore:
    def __init__(self):
        self.items: Dict[str, Optional[FileDataObject]] = {}
        
    def add_object(self, key: str, data: Optional[FileDataObject]) -> None:
        if key in self.items:
            raise KeyError("Duplicate key")
        self.items[key] = data
        
    def get_object_data(self, key: str) -> Optional[FileDataObject]:
        if key in self.items:
            return self.items[key]
        return None
    
data_store = FileDataStore()