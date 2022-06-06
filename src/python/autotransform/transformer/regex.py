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
from typing import ClassVar

from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer


class RegexTransformer(SingleTransformer):
    """A Transformer that makes regex based changes, replacing instances of the provided
    pattern with the provided replacement. Useful for simple transformations. Operates on
    FileItems.

    Attributes:
        pattern (str): The pattern to search for.
        replacement (str): The value to replace the pattern with.
        name (ClassVar[TransformerName]): The name of the component.
    """

    pattern: str
    replacement: str

    name: ClassVar[TransformerName] = TransformerName.REGEX

    def _transform_item(self, item: Item) -> None:
        """Replaces all instances of a pattern in the file with the replacement string.

        Args:
            item (Item): The file that will be transformed.
        """

        # pylint: disable=unspecified-encoding

        assert isinstance(item, FileItem)
        content = item.get_content()
        new_content = re.sub(self.pattern, self.replacement, content)
        item.write_content(new_content)
