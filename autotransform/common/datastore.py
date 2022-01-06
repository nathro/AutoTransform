# AutoTransform
# Large scale, component based code modification library
#
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
