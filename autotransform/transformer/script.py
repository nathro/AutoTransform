# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptTransformer."""

from __future__ import annotations

import json
import subprocess
from tempfile import NamedTemporaryFile as TmpFile
from typing import Any, List, Mapping, Optional, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.transformer.base import Transformer
from autotransform.transformer.type import TransformerType


class ScriptTransformerParams(TypedDict):
    """The param type for a ScriptTransformer."""

    script: str
    args: List[str]
    timeout: int
    per_item: NotRequired[bool]


class ScriptTransformer(Transformer[ScriptTransformerParams]):
    """A Transformer that makes changes using an invoked script. Sentinel values can be used in the
    args to supply information from the Batch.
    The available sentinel values for args are:
        <<KEY>>: A json encoded list of the Items for a batch. If the per_item flag is set in
            params, this will simply be the key of an Item.
        <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If the
            per_item flag is set in params, this will simply be a JSON encoding of the Item's
            extra_data. If extra_data is not present for an item, it is treated as an empty Dict.
        <<METADATA>>: A JSON encoded version of the Batch's metadata.
    _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be replaced
     with a path to a file containing the value.

    Attributes:
        _params (ScriptTransformerParams): The script and args, along with the timeout and a
            per_item flag for invoking the script on each Item.
    """

    _params: ScriptTransformerParams

    @staticmethod
    def get_type() -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer.
        """

        return TransformerType.SCRIPT

    def transform(self, batch: Batch) -> None:
        """Runs the script transformation against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag.

        Args:
            batch (Batch): The Batch being transformed.
        """

        if self._params.get("per_item", False):
            for item in batch["items"]:
                self._transform_single(item, batch.get("metadata", None))
        else:
            self._transform_batch(batch)

    def _transform_single(self, item: Item, batch_metadata: Optional[Mapping[str, Any]]) -> None:
        """Executes a simple script to transform a single Item. Sentinel values can be used
        in args that will be replaced when the script is invoked.
        The available sentinel values for args are:
            <<KEY>>: The key of the Item being transformed.
            <<EXTRA_DATA>>: A JSON encoding of the Item's extra_data. If extra_data is not present,
                it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
            replaced with a path to a file containing the value.

        Args:
            item (Item): The Item that will be transformed.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """

        event_handler = EventHandler.get()

        cmd = [self._params["script"]]

        extra_data = item.get_extra_data()
        if extra_data is None:
            extra_data = {}
        metadata = batch_metadata if batch_metadata is not None else {}

        arg_replacements = {
            "<<KEY>>": item.get_key(),
            "<<EXTRA_DATA>>": json.dumps(extra_data),
            "<<METADATA>>": json.dumps(metadata),
        }

        with TmpFile(mode="w+") as inp, TmpFile(mode="w+") as meta, TmpFile(mode="w+") as extra:
            # Make key file
            inp.write(item.get_key())
            inp.flush()
            arg_replacements["<<KEY_FILE>>"] = inp.name

            # Make extra_data file
            json.dump(extra_data, extra)
            extra.flush()
            arg_replacements["<<EXTRA_DATA_FILE>>"] = extra.name

            # Make metadata file
            json.dump(metadata, meta)
            meta.flush()
            arg_replacements["<<METADATA_FILE>>"] = meta.name

            # Create command
            for arg in self._params["args"]:
                if arg in arg_replacements:
                    cmd.append(arg_replacements[arg])
                else:
                    cmd.append(arg)

            # Run Script
            event_handler.handle(DebugEvent({"message": f"Running command: {str(cmd)}"}))
            proc = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                check=False,
                timeout=self._params["timeout"],
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

    def _transform_batch(self, batch: Batch) -> None:
        """Executes a simple script to transform the given Batch. Sentinel values can be used
        in args that will be replaced when the script is invoked.
        The available sentinel values for args are:
            <<KEY>>: A json encoded list of the Items for a batch.
            <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If
                extra_data is not present for an item, it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
        replaced with a path to a file containing the value.

        Args:
            batch (Batch): The batch that will be transformed.
        """

        event_handler = EventHandler.get()

        cmd = [self._params["script"]]

        item_keys = [item.get_key() for item in batch["items"]]
        extra_data = {
            item.get_key(): item.get_extra_data()
            for item in batch["items"]
            if item.get_extra_data() is not None
        }
        metadata = batch.get("metadata", {})
        arg_replacements = {
            "<<KEY>>": json.dumps(item_keys),
            "<<EXTRA_DATA>>": json.dumps(extra_data),
            "<<METADATA>>": json.dumps(metadata),
        }

        with TmpFile(mode="w+") as inp, TmpFile(mode="w+") as meta, TmpFile(mode="w+") as extra:
            # Make key file
            json.dump(item_keys, inp)
            inp.flush()
            arg_replacements["<<KEY_FILE>>"] = inp.name

            # Make extra_data file
            json.dump(extra_data, extra)
            extra.flush()
            arg_replacements["<<EXTRA_DATA_FILE>>"] = extra.name

            # Make metadata file
            json.dump(metadata, meta)
            meta.flush()
            arg_replacements["<<METADATA_FILE>>"] = meta.name

            # Create command
            for arg in self._params["args"]:
                if arg in arg_replacements:
                    cmd.append(arg_replacements[arg])
                else:
                    cmd.append(arg)

            # Run script
            event_handler.handle(DebugEvent({"message": f"Running command: {str(cmd)}"}))
            proc = subprocess.run(
                cmd,
                capture_output=True,
                encoding="utf-8",
                check=False,
                timeout=self._params["timeout"],
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

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ScriptTransformer:
        """Produces a ScriptTransformer from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            ScriptTransformer: An instance of the ScriptTransformer.
        """

        script = data["script"]
        assert isinstance(script, str)
        args = data["args"]
        assert isinstance(args, List)
        args = [str(arg) for arg in args]
        timeout = data["timeout"]
        assert isinstance(timeout, int)

        params: ScriptTransformerParams = {"script": script, "args": args, "timeout": timeout}

        per_item = data.get("per_item", None)
        if per_item is not None:
            assert isinstance(per_item, bool)
            params["per_item"] = per_item

        return ScriptTransformer(params)
