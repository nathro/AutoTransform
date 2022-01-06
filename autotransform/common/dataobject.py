# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Any, Dict, Optional


class FileDataObject:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data

    def get_str(self, key: str) -> str:
        val = self.data[key]
        if isinstance(val, str):
            return val
        raise ValueError("Key [" + key + "] is not string")

    def get_optional_str(self, key: str) -> Optional[str]:
        if key in self.data:
            val = self.data[key]
            if isinstance(val, str):
                return val
            raise ValueError("Key [" + key + "] is not string")
        return None

    def get_int(self, key: str) -> int:
        val = self.data[key]
        if isinstance(val, int):
            return val
        raise ValueError("Key [" + key + "] is not int")

    def get_optional_int(self, key: str) -> Optional[int]:
        if key in self.data:
            val = self.data[key]
            if isinstance(val, int):
                return val
            raise ValueError("Key [" + key + "] is not int")
        return None
