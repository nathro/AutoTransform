# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the TargetInput."""

from __future__ import annotations

import re
from typing import Any, ClassVar, Dict, Sequence, Type

from autotransform.input.base import FACTORY as input_factory
from autotransform.input.base import Input, InputName
from autotransform.item.file import FileItem


class TargetInput(Input):
    """An Input that attaches a target_path to the Items returned by another Input's
    FileItems. These target_paths are used to alter where written content is sent to.

    Attributes:
        input (Input): The base Input used to generate Items.
        pattern (str): The pattern to use for regex replacement of the Item's original path.
        replacement (str): The replacement used by regex to create the target path.
        name (ClassVar[InputName]): The name of the component.
    """

    input: Input
    pattern: str
    replacement: str

    name: ClassVar[InputName] = InputName.TARGET

    def get_items(self) -> Sequence[FileItem]:
        """Gets a list of files recursively contained within the path.

        Returns:
            Sequence[FileItem]: The eligible files for transformation.
        """

        items = [item for item in self.input.get_items() if isinstance(item, FileItem)]
        for item in items:
            if item.extra_data is None:
                item.extra_data = {}
            item.extra_data["target_path"] = re.sub(self.pattern, self.replacement, item.get_path())

        return items

    @classmethod
    def from_data(cls: Type[TargetInput], data: Dict[str, Any]) -> TargetInput:
        """Produces an instance of the component from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            TargetInput: An instance of the component.
        """

        input_object = input_factory.get_instance(data["input"])
        pattern = data["pattern"]
        replacement = data["replacement"]

        return cls(
            input=input_object,
            pattern=pattern,
            replacement=replacement,
        )
