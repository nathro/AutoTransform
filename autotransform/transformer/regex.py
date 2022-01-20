# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for the RegexTransformer."""

from __future__ import annotations

import re
from typing import Any, Mapping, TypedDict

from autotransform.common.cachedfile import CachedFile
from autotransform.transformer.single import SingleTransformer
from autotransform.transformer.type import TransformerType


class RegexTransformerParams(TypedDict):
    """The param type for a RegexTransformer."""

    pattern: str
    replacement: str


class RegexTransformer(SingleTransformer[RegexTransformerParams]):
    """A Transformer that makes regex based changes, replacing instances of the provided
    pattern with the provided replacement. Useful for simple transformations.

    Attributes:
        params (RegexTransformerParams): Contains the pattern and replacement
    """

    params: RegexTransformerParams

    def get_type(self) -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer
        """
        return TransformerType.REGEX

    def _transform_file(self, file: CachedFile) -> None:
        """Replaces all instances of pattern in the file with the replacement string.

        Args:
            file (CachedFile): The file that will be transformed
        """

        # pylint: disable=unspecified-encoding

        content = file.get_content()
        new_content = re.sub(self.params["pattern"], self.params["replacement"], content)
        file.write_content(new_content)

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> RegexTransformer:
        """Produces a RegexTransformer from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            RegexTransformer: An instance of the RegexTransformer
        """
        pattern = data["pattern"]
        assert isinstance(pattern, str)
        replacement = data["replacement"]
        assert isinstance(replacement, str)
        return RegexTransformer({"pattern": pattern, "replacement": replacement})
