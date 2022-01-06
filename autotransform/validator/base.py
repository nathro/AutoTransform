#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, TypedDict

from batcher.base import ConvertedBatch
from validator.type import ValidatorType

class ValidationResultLevel(str, Enum):
    NONE = 0
    WARNING = 1
    ERROR = 2
    
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 
    
class ValidationResult(TypedDict):
    level: ValidationResultLevel
    message: Optional[str]
    validator: ValidatorType
    
class ValidationError(Exception):
    issue: ValidationResult
    
    def __init__(self, issue: ValidationResult):
        self.issue = issue
        self.message = issue["message"]
        super().__init__(self.message)
        
    def __str__(self):
        level = ValidationResultLevel(self.issue["level"]).name
        validator = self.issue["validator"]
        
        return f"[{level}][{validator}]: {self.message}"

class ValidatorBundle(TypedDict):
    params: Optional[Dict[str, Any]]
    type: ValidatorType

class Validator(ABC):
    params: Optional[Dict[str, Any]]
    
    def __init__(self, params: Dict[str, Any]):
        self.params = params
        
    @abstractmethod
    def get_type(self) -> ValidatorType:
        pass
        
    @abstractmethod
    def validate(self, batch: ConvertedBatch) -> ValidationResult:
        pass
    
    def bundle(self) -> ValidatorBundle:
        return {
            "params": self.params,
            "type": self.get_type(),
        }
    
    @classmethod
    @abstractmethod
    def from_data(cls, data: Dict[str, Any]) -> Validator:
        pass