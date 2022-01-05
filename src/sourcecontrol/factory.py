from typing import Any, Callable, Dict

from sourcecontrol.base import SourceControl, SourceControlBundle
from sourcecontrol.git import GitSourceControl
from sourcecontrol.type import SourceControlType

class SourceControlFactory:
    _getters: Dict[SourceControlType, Callable[[Dict[str, Any]], SourceControl]] = {
        SourceControlType.GIT: GitSourceControl.from_data,
    }
    
    @staticmethod
    def get(repo: SourceControlBundle) -> SourceControl:
        return SourceControlFactory._getters[repo["type"]](repo["params"])