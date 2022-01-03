from typing import Dict, Optional

from common.FileDataObject import FileDataObject

class FileDataStore:
    def __init__(self):
        self.items: Dict[str, Optional[FileDataObject]] = {}
        
    def addObject(self, key: str, data: Optional[FileDataObject]) -> None:
        if key in self.items:
            raise KeyError("Duplicate key")
        self.items[key] = data
        
    def getObjectData(self, key: str) -> Optional[FileDataObject]:
        if key in self.items:
            return self.items[key]
        return None
    
data_store = FileDataStore()