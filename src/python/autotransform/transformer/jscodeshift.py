# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the JSCodeshiftTransformer. See https://github.com/facebook/jscodeshift"""

from __future__ import annotations

import subprocess
from typing import ClassVar, List

from pydantic import Field

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer


class JSCodeshiftTransformer(SingleTransformer):
    """A Transformer that makes changes using JSCodeshift.

    Attributes:
        js_transform (str): The JSCodeshift transform to execute.
        args (optional, List[str]): The arguments to supply to the transformation. Defaults to [].
        timeout (optional, int): The timeout for an individual run.
        name (ClassVar[TransformerName]): The name of the component.
    """

    js_transform: str

    args: List[str] = Field(default_factory=list)
    timeout: int = 600

    name: ClassVar[TransformerName] = TransformerName.JSCODESHIFT

    def _transform_item(self, item: Item) -> None:
        """Run the supplied JSCodeshift transform against the file.

        Args:
            item (Item): The file that will be transformed.
        """

        assert isinstance(item, FileItem)
        event_handler = EventHandler.get()

        cmd = ["jscodeshift", "-t", self.js_transform, item.get_path()]
        cmd.extend(self.args)

        # Run JSCodeshift
        event_handler.handle(DebugEvent({"message": f"Running command: {cmd}"}))
        proc = subprocess.run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            check=False,
            timeout=self.timeout,
        )
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        proc.check_returncode()
