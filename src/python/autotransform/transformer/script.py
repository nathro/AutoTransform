# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the ScriptTransformer."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List, Optional

from autotransform.batcher.base import Batch
from autotransform.transformer.base import Transformer, TransformerName
from autotransform.util.functions import run_cmd_on_items
from pydantic import root_validator, validator


class ScriptTransformer(Transformer[None]):
    """A Transformer that makes changes using an invoked script. Sentinel values can be
    used in args to provide custom arguments for a run.
    The available sentinel values for args are:
        <<KEY>>: A list of the Items for a Batch. If the per_item flag is set this will simply
            be the key of an Item.
        <<TARGET_PATH>>: A list of target_path extra_data field for a Batch. If the per_item flag
            is set this will simply be the target_path of an Item.
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
        timeout (int): The timeout to use for the script process.
        chunk_size (Optional[int], optional): The size of chunks to operate on. None indicates no
            chunking. Defaults to None.
        name (ClassVar[TransformerName]): The name of the Component.
    """

    args: List[str]
    script: str
    timeout: int
    chunk_size: Optional[int] = None

    name: ClassVar[TransformerName] = TransformerName.SCRIPT

    @validator("chunk_size")
    @classmethod
    def chunk_size_must_be_positive(cls, v: Optional[int]) -> Optional[int]:
        """Validates that chunk

        Args:
            v (Optional[int]): The chunk_size that was set.

        Raises:
            ValueError: Raised if chunk_size is not None and is less than 1.

        Returns:
            Optional[int]: The validated chunk_size.
        """

        if v is not None and v < 1:
            raise ValueError(f"Chunk size must be greater than 0, {v} provided")
        return v

    @root_validator(pre=True)
    @classmethod
    def per_item_legacy_setting_validator(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validates chunk size using legacy per_item setting.

        Args:
            values (Dict[str, Any]): The values used to configure the ScriptTransformer.

        Raises:
            ValueError: Raised if per item is set with a chunk_size that is not 1.

        Returns:
            Mapping[str, Any]: The fixed values.
        """

        if "per_item" in values and values["per_item"]:
            if "chunk_size" in values and values["chunk_size"] != 1:
                raise ValueError("Per item can not be specified with a chunk size that is not 1")
            values["chunk_size"] = 1
        return values

    def transform(self, batch: Batch) -> None:
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

        metadata = batch.get("metadata", {})
        items = batch["items"]
        num_items = max(len(items), 1)
        chunk_size = self.chunk_size or num_items

        # Get Command
        for i in range(0, num_items, chunk_size):
            chunk_items = items[i : i + chunk_size]
            cmd = [self.script]
            cmd.extend(self.args)

            proc = run_cmd_on_items(cmd, chunk_items, metadata, timeout=self.timeout)
            proc.check_returncode()
