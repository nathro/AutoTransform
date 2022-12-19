# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptCommand."""

from __future__ import annotations

from typing import Any, ClassVar, List, Mapping, Optional, Sequence

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.command.base import Command, CommandName
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.util.functions import run_cmd_on_items


class ScriptCommand(Command):
    """Runs a script with the supplied arguments to perform a command. If the per_item flag is
    set, the script will be invoked on each Item. If run_on_changes is set to True, the script
    will replace the Batch Items with FileItems for each changed file. Sentinel values can be
    used in args to provide custom arguments for a run.
    The available sentinel values for args are:
        <<KEY>>: A json encoded list of the Items for a Batch. If the per_item flag is set
            this will simply be the key of an Item.
        <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If the
            per_item flag is set, this will simply be a JSON encoding of the Item's extra_data.
            If extra_data is not present for an item, it is treated as an empty Dict.
        <<METADATA>>: A JSON encoded version of the Batch's metadata.
    _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be replaced
     with a path to a file containing the value.

    Attributes:
        args (List[str]): The arguments to supply to the script.
        script (str): The script to run.
        per_item (bool, optional): Whether to run the script on each item. Defaults to False.
        run_on_changes (bool, optional): Whether to replace the Items in the batch with
            FileItems for the changed files. Defaults to False.
        run_pre_validation (bool, optional): Whether to run the command before validation is done.
            Defaults to False.
        name (ClassVar[CommandName]): The name of the Component.
    """

    args: List[str]
    script: str
    per_item: bool = False
    run_on_changes: bool = False
    run_pre_validation: bool = False

    name: ClassVar[CommandName] = CommandName.SCRIPT

    def run(self, batch: Batch, _transform_data: Optional[Mapping[str, Any]]) -> None:
        """Runs the script command against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag.

        Args:
            batch (Batch): The transformed Batch to run against.
            _transform_data (Optional[Mapping[str, Any]]): Data from the transformation. Unused.
        """

        if not self.per_item:
            self._run_batch(batch)
            return
        if self.run_on_changes:
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.repo
            assert repo is not None
            items: Sequence[Item] = [FileItem(key=file) for file in repo.get_changed_files(batch)]
        else:
            items = batch["items"]

        for item in items:
            self._run_single(item, batch.get("metadata", None))

    def _run_single(self, item: Item, batch_metadata: Optional[Mapping[str, Any]]) -> None:
        """Executes a simple script to run a command on a single Item.

        Args:
            item (Item): The Item that will be validated.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """

        event_handler = EventHandler.get()

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, [item], batch_metadata or {})

        # Handle output
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        proc.check_returncode()

    def _run_batch(self, batch: Batch) -> None:
        """Executes a simple script against the given Batch.

        Args:
            batch (Batch): The batch that will be run against.
        """

        event_handler = EventHandler.get()

        # Get items
        if self.run_on_changes:
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.repo
            assert repo is not None
            items: Sequence[Item] = [FileItem(key=file) for file in repo.get_changed_files(batch)]
        else:
            items = batch["items"]

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, items, batch.get("metadata", {}))

        # Handle output
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        proc.check_returncode()
