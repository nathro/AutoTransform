# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Optional


class CachedFile:
    # pylint: disable=too-few-public-methods

    path: str
    content: Optional[str]

    def __init__(self, path: str):
        self.path = path
        self.content: Optional[str] = None

    def get_content(self) -> str:
        if self.content is None:
            # pylint: disable=unspecified-encoding
            with open(self.path, "r") as file:
                self.content = file.read()
        return self.content
