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