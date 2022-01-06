# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Dict

FILE_CACHE: Dict[str, str] = {}


class CachedFile:
    # pylint: disable=too-few-public-methods

    path: str

    def __init__(self, path: str):
        self.path = path

    def get_content(self) -> str:
        if self.path not in FILE_CACHE:
            # pylint: disable=unspecified-encoding
            with open(self.path, "r") as file:
                FILE_CACHE[self.path] = file.read()
        return FILE_CACHE[self.path]

    def __del__(self):
        if self.path in FILE_CACHE:
            del FILE_CACHE[self.path]
