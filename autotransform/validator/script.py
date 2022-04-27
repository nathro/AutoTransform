# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptValidator."""

from __future__ import annotations

import json
import subprocess
from tempfile import NamedTemporaryFile as TmpFile
from typing import Any, List, Mapping, Optional, Sequence, TypedDict

from typing_extensions import NotRequired

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.validator.base import ValidationResult, ValidationResultLevel, Validator
from autotransform.validator.type import ValidatorType


class ScriptValidatorParams(TypedDict):
    """The param type for a ScriptValidator."""

    script: str
    args: List[str]
    failure_level: ValidationResultLevel
    per_item: NotRequired[bool]
    run_on_changes: NotRequired[bool]


class ScriptValidator(Validator[ScriptValidatorParams]):
    """Runs a script with the supplied arguments to perform validation. If the per_item flag is
    set to True, the script will be invoked on each Item. If run_on_changes is set to True, the
    script will replace the Batch Items with FileItems for each changed file. The failure_level
    indicates the result level if the script returns a non-zero exit code. Sentinel values can
    be used in args to provide custom arguments for a run.
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
        _params (ScriptValidatorParams): Contains the args and set-up for the script.
    """

    _params: ScriptValidatorParams

    @staticmethod
    def get_type() -> ValidatorType:
        """Used to map Validator components 1:1 with an enum, allowing construction from JSON.

        Returns:
            ValidatorType: The unique type associated with this Validator.
        """

        return ValidatorType.SCRIPT

    def validate(self, batch: Batch) -> ValidationResult:
        """Runs the script validation against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag. If the script returns a non-zero exit
        code, the failure_level in params will be in the result.

        Args:
            batch (Batch): The transformed Batch to validate.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
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
                result = self._validate_single(item, batch.get("metadata", None))
                if result["level"] != ValidationResultLevel.NONE:
                    return result
            return {
                "level": ValidationResultLevel.NONE,
                "message": "",
                "validator": self.get_type(),
            }
        return self._validate_batch(batch)

    def _validate_single(
        self, item: Item, batch_metadata: Optional[Mapping[str, Any]]
    ) -> ValidationResult:
        """Executes a simple script to validate a single Item. Sentinel values can be used
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
        level = (
            self._params["failure_level"] if proc.returncode != 0 else ValidationResultLevel.NONE
        )
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        return {
            "level": level,
            "message": f"[{str(cmd)}]\n"
            + f"STDOUT:\n{proc.stdout.strip()}\nSTDERR:\n{proc.stderr.strip()}",
            "validator": self.get_type(),
        }

    def _validate_batch(self, batch: Batch) -> ValidationResult:
        """Executes a simple script to validate the given Batch. Sentinel values can be used
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
        level = (
            self._params["failure_level"] if proc.returncode != 0 else ValidationResultLevel.NONE
        )
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        return {
            "level": level,
            "message": f"[{str(cmd)}]\n"
            + f"STDOUT:\n{proc.stdout.strip()}\nSTDERR:\n{proc.stderr.strip()}",
            "validator": self.get_type(),
        }

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ScriptValidator:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            ScriptValidator: An instance of the ScriptValidator.
        """

        script = data["script"]
        assert isinstance(script, str)
        args = data["args"]
        assert isinstance(args, List)
        for arg in args:
            assert isinstance(arg, str)
        failure_level = data["failure_level"]
        if not ValidationResultLevel.has_value(failure_level):
            failure_level = ValidationResultLevel.from_name(failure_level)
        else:
            failure_level = ValidationResultLevel.from_value(failure_level)
        params: ScriptValidatorParams = {
            "script": script,
            "args": args,
            "failure_level": failure_level,  # type: ignore
        }

        per_item = data.get("per_item", None)
        if per_item is not None:
            assert isinstance(per_item, bool)
            params["per_item"] = per_item

        run_on_changes = data.get("run_on_changes", None)
        if run_on_changes is not None:
            assert isinstance(run_on_changes, bool)
            params["run_on_changes"] = run_on_changes

        return ScriptValidator(params)
