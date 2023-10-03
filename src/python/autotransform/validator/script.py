# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptValidator."""

from __future__ import annotations

from typing import Any, ClassVar, List, Mapping, Optional, Sequence

import autotransform.schema
from autotransform.batcher.base import Batch
from autotransform.item.base import Item
from autotransform.item.file import FileItem
from autotransform.util.functions import run_cmd_on_items
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

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, [item], batch_metadata or {})

        # Handle output
        level = self.failure_level if proc.returncode != 0 else ValidationResultLevel.NONE
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

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        proc = run_cmd_on_items(cmd, items, batch.get("metadata", {}))

        # Handle output
        level = self.failure_level if proc.returncode != 0 else ValidationResultLevel.NONE
        return ValidationResult(
            level=level,
            message=f"[{cmd}]\nSTDOUT:\n{proc.stdout.strip()}\nSTDERR:\n{proc.stderr.strip()}",
            validator=self,
        )
