# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the LibCSTTransformer. See https://github.com/Instagram/LibCST"""

from __future__ import annotations

import importlib
from functools import cached_property
from typing import Any, ClassVar, Dict

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.warning import WarningEvent
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.transformer.base import TransformerName
from autotransform.transformer.single import SingleTransformer
from libcst.codemod import (
    CodemodCommand,
    CodemodContext,
    TransformExit,
    TransformFailure,
    TransformSkip,
    TransformSuccess,
    transform_module,
)
from pydantic import Field


class LibCSTTransformer(SingleTransformer):
    """A Transformer that makes changes using LibCST.

    Attributes:
        command_module (str): The fully qualified module where the CodemodCommand is located.
        command_name (str): The name of the class for the CodemodCommand.
        command_args (optional, Dict[str, Any]): Arguments for the CodemodCommand. Defaults to {}.
        name (ClassVar[TransformerName]): The name of the component.
    """

    command_module: str
    command_name: str
    command_args: Dict[str, Any] = Field(default_factory=dict)
    name: ClassVar[TransformerName] = TransformerName.LIBCST

    def _transform_item(self, item: Item) -> None:
        """Run the supplied CodemodCommand against a FileItem.

        Args:
            item (Item): The file that will be transformed.
        """

        if not isinstance(item, FileItem):
            raise TypeError("Item must be an instance of FileItem")

        event_handler = EventHandler.get()
        event_handler.handle(DebugEvent({"message": f"Performing transform on {item.get_path()}"}))
        res = transform_module(self._command, item.get_content())

        for message in res.warning_messages:
            event_handler.handle(WarningEvent({"message": f"Warning: {message}"}))

        if isinstance(res, TransformSuccess):
            event_handler.handle(DebugEvent({"message": "Transform success"}))
            item.write_content(res.code)
        elif isinstance(res, TransformSkip):
            event_handler.handle(
                DebugEvent(
                    {"message": f"Transform skipped ({res.skip_reason}): {res.skip_description}"}
                )
            )
        elif isinstance(res, TransformFailure):
            event_handler.handle(
                WarningEvent({"message": f"Transform failed: {res.error}\n{res.traceback_str}"})
            )
        elif isinstance(res, TransformExit):
            event_handler.handle(DebugEvent({"message": "Transform exited from user interupt"}))

    @cached_property
    def _command(self) -> CodemodCommand:
        """Gets an instance of the command and caches it.

        Returns:
            CodemodCommand: An instance of the command to run.
        """

        module = importlib.import_module(self.command_module)

        if not hasattr(module, self.command_name):
            raise AttributeError(
                f"Module {self.command_module} does not have attribute {self.command_name}"
            )

        command_class = getattr(module, self.command_name)

        if not isinstance(command_class, type):
            raise TypeError("Command is not a class")

        if not issubclass(command_class, CodemodCommand):
            raise TypeError("Component must be a subclass of CodemodCommand")

        return command_class(CodemodContext(), **self.command_args)
