from typing import Optional

class CachedFile:
    def __init__(self, path: str):
        self.path = path
        self.content: Optional[str] = None
    
    def get_content(self) -> str:
        if self.content is None:
            f = open(self.path, 'r')
            self.content = f.read()
            f.close()
        return self.content