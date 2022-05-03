# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptCommand."""

from __future__ import annotations

import json
import subprocess
from tempfile import NamedTemporaryFile as TmpFile
from typing import Any, List, Mapping, Optional, Sequence

from typing_extensions import NotRequired

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.command.base import Command, CommandParams
from autotransform.command.type import CommandType
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.item.file import FileItem


class ScriptCommandParams(CommandParams):
    """The param type for a ScriptCommand."""

    script: str
    args: List[str]
    per_item: NotRequired[bool]
    run_on_changes: NotRequired[bool]


class ScriptCommand(Command[ScriptCommandParams]):
    """Runs a script with the supplied arguments to perform a command. If the per_item flag is
    set to True, the script will be invoked on each Item. If run_on_changes is set to True, the
    script will replace the Batch Items with FileItems for each changed file. Sentinel values can
    be used in args to provide custom arguments for a run.
    The available sentinel values for args are:
        <<KEY>>: A json encoded list of the Items for a Batch. If the per_item flag is set in
            params, this will simply be the key of an Item.
        <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If the
            per_item flag is set in params, this will simply be a JSON encoding of the Item's
            extra_data. If extra_data is not present for an item, it is treated as an empty Dict.
        <<METADATA>>: A JSON encoded version of the Batch's metadata.
    _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be replaced
     with a path to a file containing the value.

    Attributes:
        _params (ScriptCommandParams): Contains the args and set-up for the script.
    """

    _params: ScriptCommandParams

    @staticmethod
    def get_type() -> CommandType:
        """Used to map Command components 1:1 with an enum, allowing construction from JSON.

        Returns:
            CommandType: The unique type associated with this Command.
        """

        return CommandType.SCRIPT

    def run(self, batch: Batch) -> None:
        """Runs the script command against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag.

        Args:
            batch (Batch): The transformed Batch to run against.
        """

        if self._params.get("per_item", False):
            if self._params.get("run_on_changes", False):
                current_schema = autotransform.schema.current
                assert current_schema is not None
                repo = current_schema.get_repo()
                assert repo is not None
                items: Sequence[Item] = [FileItem(file) for file in repo.get_changed_files(batch)]
            else:
                items = batch["items"]

            for item in items:
                self._run_single(item, batch.get("metadata", None))
        return self._run_batch(batch)

    def _run_single(self, item: Item, batch_metadata: Optional[Mapping[str, Any]]) -> None:
        """Executes a simple script to run a command on a single Item. Sentinel values can be used
        in args that will be replaced when the script is invoked.
        The available sentinel values for args are:
            <<KEY>>: The key of the Item being validated.
            <<EXTRA_DATA>>: A JSON encoding of the Item's extra_data. If extra_data is not present,
                it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
            replaced with a path to a file containing the value.

        Args:
            item (Item): The Item that will be validated.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """

        event_handler = EventHandler.get()

        cmd = [self._params["script"]]

        extra_data = item.get_extra_data()
        if extra_data is None:
            extra_data = {}

        arg_replacements = {
            "<<KEY>>": item.get_key(),
            "<<EXTRA_DATA>>": json.dumps(extra_data),
            "<<METADATA>>": json.dumps(batch_metadata),
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
            json.dump(batch_metadata, meta)
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
            proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False)
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
        """Executes a simple script against the given Batch. Sentinel values can be used
        in args that will be replaced when the script is invoked.
        The available sentinel values for args are:
            <<KEY>>: A json encoded list of the Items for a batch.
            <<EXTRA_DATA>>: A JSON encoded mapping from Item key to that Item's extra_data. If
                extra_data is not present for an item, it is treated as an empty Dict.
            <<METADATA>>: A JSON encoded version of the Batch's metadata.
        _FILE can be appended to any of these (i.e. <<KEY_FILE>>) and the arg will instead be
        replaced with a path to a file containing the value.

        Args:
            batch (Batch): The batch that will be run against.
        """

        event_handler = EventHandler.get()

        cmd = [self._params["script"]]
        if self._params.get("run_on_changes", False):
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.get_repo()
            assert repo is not None
            items: Sequence[Item] = [FileItem(file) for file in repo.get_changed_files(batch)]
        else:
            items = batch["items"]

        item_keys = [item.get_key() for item in items]
        extra_data = {
            item.get_key(): item.get_extra_data()
            for item in items
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
            proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False)
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
    def _from_data(data: Mapping[str, Any]) -> ScriptCommand:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            ScriptCommand: An instance of the ScriptCommand.
        """

        script = data["script"]
        assert isinstance(script, str)
        args = data["args"]
        assert isinstance(args, List)
        for arg in args:
            assert isinstance(arg, str)
        params: ScriptCommandParams = {
            "script": script,
            "args": args,
        }

        per_item = data.get("per_item", None)
        if per_item is not None:
            assert isinstance(per_item, bool)
            params["per_item"] = per_item

        run_on_changes = data.get("run_on_changes", None)
        if run_on_changes is not None:
            assert isinstance(run_on_changes, bool)
            params["run_on_changes"] = run_on_changes

        return ScriptCommand(params)
