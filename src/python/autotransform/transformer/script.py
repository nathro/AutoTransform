# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptTransformer."""

from __future__ import annotations

from typing import Any, ClassVar, List, Mapping, Optional

from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.transformer.base import Transformer, TransformerName
from autotransform.util.functions import run_cmd_on_items


class ScriptTransformer(Transformer[None]):
    """A Transformer that makes changes using an invoked script. Sentinel values can be
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
        script (str): The script to run.
        args (List[str]): The arguments to supply to the script.
        timeout (int): The timeout to use for the script process.
        per_item (bool, optional): Whether to run the script on each item. Defaults to False.
        name (ClassVar[TransformerName]): The name of the Component.
    """

    script: str
    args: List[str]
    timeout: int
    per_item: bool = False

    name: ClassVar[TransformerName] = TransformerName.SCRIPT

    def transform(self, batch: Batch) -> None:
        """Runs the script transformation against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag.

        Args:
            batch (Batch): The Batch being transformed.
        """

        if self.per_item:
            for item in batch["items"]:
                self._transform_single(item, batch.get("metadata", None))
        else:
            self._transform_batch(batch)

    def _transform_single(self, item: Item, batch_metadata: Optional[Mapping[str, Any]]) -> None:
        """Executes a simple script to transform a single Item. Sentinel values can be
        used in args to provide custom arguments for a run.
        The available sentinel values for args are:
            <<KEY>>: The key of an item.
            <<EXTRA_DATA>>: A JSON encoding of the Item's extra_data. If extra_data is not present
                for an item, it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
        replaced with a path to a file containing the value.

        Args:
            item (Item): The Item that will be transformed.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """

        event_handler = EventHandler.get()

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, [item], batch_metadata or {}, timeout=self.timeout)
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        proc.check_returncode()

    def _transform_batch(self, batch: Batch) -> None:
        """Executes a simple script to transform the given Batch. Sentinel values can be
        used in args to provide custom arguments for a run.
        The available sentinel values for args are:
            <<KEY>>: A json encoded list of the Items for a Batch.
            <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data.
                If extra_data is not present for an item, it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
        replaced with a path to a file containing the value.

        Args:
            batch (Batch): The batch that will be transformed.
        """

        event_handler = EventHandler.get()

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(
            cmd, batch["items"], batch.get("metadata", {}), timeout=self.timeout
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
