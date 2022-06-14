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
from typing import Any, ClassVar, List, Mapping, Optional, Sequence

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.validator.base import (
    ValidationResult,
    ValidationResultLevel,
    Validator,
    ValidatorName,
)


class ScriptValidator(Validator):
    """Runs a script with the supplied arguments to perform validation. If the per_item flag is
    set to True, the script will be invoked on each Item. If run_on_changes is set to True, the
    script will replace the Batch Items with FileItems for each changed file. The failure_level
    indicates the result level if the script returns a non-zero exit code. Sentinel values can
    be used in args to provide custom arguments for a run.
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
        failure_level (ValidationResultLevel, optional): The result level to use if validation
            fails. Defaults to ValidationResultLevel.ERROR.
        per_item (bool, optional): Whether to run the script on each item. Defaults to False.
        run_on_changes (bool, optional): Whether to replace the Items in the batch with
            FileItems for the changed files. Defaults to False.
        name (ClassVar[ValidatorName]): The name of the Component.
    """

    args: List[str]
    script: str
    failure_level: ValidationResultLevel = ValidationResultLevel.ERROR
    per_item: bool = False
    run_on_changes: bool = False

    name: ClassVar[ValidatorName] = ValidatorName.SCRIPT

    def check(self, batch: Batch, _transform_data: Optional[Mapping[str, Any]]) -> ValidationResult:
        """Runs the script validation against the Batch, either on each item individually or
        on the entire Batch, based on the per_item flag. If the script returns a non-zero exit
        code, the failure_level will be in the result.

        Args:
            batch (Batch): The transformed Batch to validate.
            _transform_data (Optional[Mapping[str, Any]]): Data from the transformation. Unused.

        Returns:
            ValidationResult: The result of the validation check indicating the severity of any
                validation failures as well as an associated message
        """
        if not self.per_item:
            return self._check_batch(batch)
        if self.run_on_changes:
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.repo
            assert repo is not None
            items: Sequence[Item] = [FileItem(key=file) for file in repo.get_changed_files(batch)]
        else:
            items = batch["items"]

        for item in items:
            result = self._check_single(item, batch.get("metadata", None))
            if result.level != ValidationResultLevel.NONE:
                return result
        return ValidationResult(level=ValidationResultLevel.NONE, validator=self)

    def _check_single(
        self, item: Item, batch_metadata: Optional[Mapping[str, Any]]
    ) -> ValidationResult:
        """Executes a simple script to validate a single Item.

        Args:
            item (Item): The Item that will be validated.
            batch_metadata (Optional[Mapping[str, Any]]): The metadata of the Batch containing the
                Item.
        """

        event_handler = EventHandler.get()

        cmd = [self.script]

        extra_data = item.extra_data
        if extra_data is None:
            extra_data = {}

        arg_replacements = {
            "<<KEY>>": item.key,
            "<<EXTRA_DATA>>": json.dumps(extra_data),
            "<<METADATA>>": json.dumps(batch_metadata),
        }

        with TmpFile(mode="w+") as inp, TmpFile(mode="w+") as meta, TmpFile(mode="w+") as extra:
            # Make key file
            inp.write(item.key)
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
            for arg in self.args:
                if arg in arg_replacements:
                    cmd.append(arg_replacements[arg])
                else:
                    cmd.append(arg)

            # Run script
            event_handler.handle(DebugEvent({"message": f"Running command: {cmd}"}))
            proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False)

        # Handle output
        level = self.failure_level if proc.returncode != 0 else ValidationResultLevel.NONE
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        return ValidationResult(
            level=level,
            message=f"[{cmd}]\nSTDOUT:\n{proc.stdout.strip()}\nSTDERR:\n{proc.stderr.strip()}",
            validator=self,
        )

    def _check_batch(self, batch: Batch) -> ValidationResult:
        """Executes a simple script to validate the given Batch.

        Args:
            batch (Batch): The batch that will be validated.
        """

        event_handler = EventHandler.get()

        cmd = [self.script]

        # Get items
        if self.run_on_changes:
            current_schema = autotransform.schema.current
            assert current_schema is not None
            repo = current_schema.repo
            assert repo is not None
            items: Sequence[Item] = [FileItem(key=file) for file in repo.get_changed_files(batch)]
        else:
            items = batch["items"]

        item_keys = [item.key for item in items]
        extra_data = {item.key: item.extra_data for item in items if item.extra_data is not None}
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
            for arg in self.args:
                if arg in arg_replacements:
                    cmd.append(arg_replacements[arg])
                else:
                    cmd.append(arg)

            # Run script
            event_handler.handle(DebugEvent({"message": f"Running command: {cmd}"}))
            proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False)

        # Handle output
        level = self.failure_level if proc.returncode != 0 else ValidationResultLevel.NONE
        if proc.stdout.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDOUT"}))
        if proc.stderr.strip() != "":
            event_handler.handle(DebugEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
        else:
            event_handler.handle(DebugEvent({"message": "No STDERR"}))
        return ValidationResult(
            level=level,
            message=f"[{cmd}]\nSTDOUT:\n{proc.stdout.strip()}\nSTDERR:\n{proc.stderr.strip()}",
            validator=self,
        )
