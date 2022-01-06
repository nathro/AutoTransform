#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Dict, Optional

class FileDataObject:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data
        
    def get_str(self, property: str) -> str:
        p = self.data[property]
        if isinstance(p, str):
            return p
        raise ValueError("Property [" + property + "] is not string")
    
    def get_optional_str(self, property: str) -> Optional[str]:
        if property in self.data:
            p = self.data[property]
            if isinstance(p, str):
                return p
            raise ValueError("Property [" + property + "] is not string")
        return None
    
    def get_int(self, property: str) -> int:
        p = self.data[property]
        if isinstance(p, int):
            return p
        raise ValueError("Property [" + property + "] is not int")
    
    def get_optional_int(self, property: str) -> Optional[int]:
        if property in self.data:
            p = self.data[property]
            if isinstance(p, int):
                return p
            raise ValueError("Property [" + property + "] is not int")
        return None