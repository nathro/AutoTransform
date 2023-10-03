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
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.util.functions import run_cmd_on_items


class ScriptCommand(Command):
    """Runs a script with the supplied arguments to perform a command. If the per_item flag is
    set, the script will be invoked on each Item. If run_on_changes is set to True, the script
    will replace the Batch Items with FileItems for each changed file. Sentinel values can be
    used in args to provide custom arguments for a run.
    The available sentinel values for args are:
        <<KEY>>: A list of the Items for a Batch. If the per_item flag is set this will simply
            be the key of an Item.
        <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If the
            per_item flag is set, this will simply be a JSON encoding of the Item's extra_data.
            If extra_data is not present for an item, it is treated as an empty Dict.
        <<METADATA>>: A JSON encoded version of the Batch's metadata.
    _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be replaced
     with a path to a file containing the value.

    Additionally, <<EXTRA_DATA/some_key>> can be used as a sentinel value to get a list of all the
    values from extra_data for each item with that key. Values will be converted to strings and
    returned as a list.

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

        items = self._get_items(batch)

        if self.per_item:
            for item in items:
                self._run_single(item, batch.get("metadata", None))
            return

        self._run_batch(batch, items)

    def _get_items(self, batch: Batch) -> Sequence[Item]:
        """Get items based on the run_on_changes flag.

        Args:
            batch (Batch): The transformed Batch to run against.

        Returns:
            Sequence[Item]: The sequence of items to be processed.
        """
        if self.run_on_changes:
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.repo
            assert repo is not None
            return [FileItem(key=file) for file in repo.get_changed_files(batch)]

        return batch["items"]

    def _run_single(self, item: Item, batch_metadata: Optional[Mapping[str, Any]]) -> None:
        """Executes a simple script to run a command on a single Item.

        Args:
            item (Item): The Item that will be validated.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """
        self._run_script([item], batch_metadata or {})

    def _run_batch(self, batch: Batch, items: Sequence[Item]) -> None:
        """Executes a simple script against the given Batch.

        Args:
            batch (Batch): The batch that will be run against.
            items (Sequence[Item]): The sequence of items to be processed.
        """
        self._run_script(items, batch.get("metadata", {}))

    def _run_script(self, items: Sequence[Item], metadata: Mapping[str, Any]) -> None:
        """Executes a simple script against the given items.

        Args:
            items (Sequence[Item]): The sequence of items to be processed.
            metadata (Mapping[str, Any]): The metadata of the Batch containing the items.
        """

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, items, metadata)
        proc.check_returncode()
