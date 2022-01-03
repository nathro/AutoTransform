from typing import Any, Dict, Optional

class FileDataObject:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data
        
    def getStr(self, property: str) -> str:
        p = self.data[property]
        if isinstance(p, str):
            return p
        raise ValueError("Property [" + property + "] is not string")
    
    def getOptionalStr(self, property: str) -> Optional[str]:
        if property in self.data:
            p = self.data[property]
            if isinstance(p, str):
                return p
            raise ValueError("Property [" + property + "] is not string")
        return None
    
    def getInt(self, property: str) -> int:
        p = self.data[property]
        if isinstance(p, int):
            return p
        raise ValueError("Property [" + property + "] is not int")
    
    def getOptionalInt(self, property: str) -> Optional[int]:
        if property in self.data:
            p = self.data[property]
            if isinstance(p, int):
                return p
            raise ValueError("Property [" + property + "] is not int")
        return None