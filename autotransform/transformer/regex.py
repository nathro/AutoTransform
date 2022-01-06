# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

import re
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.base import Transformer
from autotransform.transformer.type import TransformerType


class RegexTransformerParams(TypedDict):
    pattern: str
    replacement: str


class RegexTransformer(Transformer):
    params: RegexTransformerParams

    def __init__(self, params: RegexTransformerParams):
        Transformer.__init__(self, params)

    def get_type(self) -> TransformerType:
        return TransformerType.REGEX

    def transform(self, file: CachedFile) -> None:
        # pylint: disable=unspecified-encoding
        content = file.get_content()
        output = open(file.path, "w")
        new_content = re.sub(self.params["pattern"], self.params["replacement"], content)
        output.write(new_content)
        output.close()

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> RegexTransformer:
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        replacement = data["replacement"]
        assert isinstance(replacement, str)
        return RegexTransformer({"pattern": pattern, "replacement": replacement})
