# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the RegexTransformer."""

from __future__ import annotations

import re
from typing import Any, Mapping, TypedDict

from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.single import SingleTransformer
from autotransform.transformer.type import TransformerType


class RegexTransformerParams(TypedDict):
    """The param type for a RegexTransformer."""

    pattern: str
    replacement: str


class RegexTransformer(SingleTransformer[RegexTransformerParams]):
    """A Transformer that makes regex based changes, replacing instances of the provided
    pattern with the provided replacement. Useful for simple transformations. Operates on
    FileItems.

    Attributes:
        _params (RegexTransformerParams): Contains the pattern and replacement.
    """

    _params: RegexTransformerParams

    @staticmethod
    def get_type() -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer.
        """

        return TransformerType.REGEX

    def _transform_item(self, item: Item) -> None:
        """Replaces all instances of a pattern in the file with the replacement string.

        Args:
            item (Item): The file that will be transformed.
        """

        # pylint: disable=unspecified-encoding

        assert isinstance(item, FileItem)
        content = item.get_content()
        new_content = re.sub(self._params["pattern"], self._params["replacement"], content)
        item.write_content(new_content)

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> RegexTransformer:
        """Produces a RegexTransformer from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            RegexTransformer: An instance of the RegexTransformer.
        """

        pattern = data["pattern"]
        assert isinstance(pattern, str)
        replacement = data["replacement"]
        assert isinstance(replacement, str)
        return RegexTransformer({"pattern": pattern, "replacement": replacement})
