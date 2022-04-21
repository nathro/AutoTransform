# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Transformer components."""

from __future__ import annotations

import json
import subprocess
from tempfile import NamedTemporaryFile as TmpFile
from typing import Any, List, Mapping, TypedDict

from typing_extensions import NotRequired

from autotransform.batcher.base import Batch
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
    args to supply information from the inputs.
    The available sentinel values for args are:
        <<INPUT>>: A json encoded list of the input files for a batch
        <<METADATA>>: A json encoded version of the metadata
    _FILE can be appended to any of these (i.e. <<INPUT_FILE>>) and the arg will instead be replaced
     with a path to a file containing the value.

    Attributes:
        params (ScriptTransformerParams): Contains the pattern and replacement
    """

    params: ScriptTransformerParams

    def get_type(self) -> TransformerType:
        """Used to map Transformer components 1:1 with an enum, allowing construction from JSON.

        Returns:
            TransformerType: The unique type associated with this Transformer
        """

        return TransformerType.SCRIPT

    def transform(self, batch: Batch) -> None:
        if self.params["per_item"]:
            for item in batch["items"]:
                self._transform_single(item)
        else:
            self._transform_batch(batch)

    def _transform_single(self, item: Item) -> None:
        """Executes a simple script to transform a single Item. Sentinel values can be used
        in args that will be replaced when the script is invoked. Possible values include:
            <<KEY>>: The key of the Item.
            <<EXTRA_DATA>>: A JSON encoded mapping of the extra data associated with the Item.

        Args:
            item (Item): The Item that will be transformed.
        """

        cmd = [self.params["script"]]
        extra_data = item.get_extra_data()
        if extra_data is None:
            extra_data = {}
        arg_replacements = {
            "<<ITEM>>": item.get_key(),
            "<<EXTRA_DATA>>": json.dumps(extra_data),
        }
        for arg in self.params["args"]:
            if arg in arg_replacements:
                cmd.append(arg_replacements[arg])
            else:
                cmd.append(arg)
        subprocess.check_output(cmd, timeout=self.params["timeout"])

    def _transform_batch(self, batch: Batch) -> None:
        """Executes a simple script to transform the given batch. Sentinel values can be used
        in args that will be replaced when the script is invoked. Possible values include:
            <<KEY>>: A JSON encoded list of the inputs in the batch
            <<METADATA>>: A JSON encoded representation of the batch metadata
            <<EXTRA_DATA>>: A JSON encoded mapping from input to extra data stored
                in FileDataStore
            Additionally, _FILE can be appended to the value to use a path to a file containing
            the value (i.e. <<INPUT_FILE>> would be a path to a tmp file containing the JSON
            encoded input)

        Args:
            batch (Batch): The batch that will be transformed
        """

        cmd = [self.params["script"]]
        item_keys = [item.get_key() for item in batch["items"]]
        extra_data = {
            item.get_key(): item.get_extra_data()
            for item in batch["items"] if item.get_extra_data() is not None
        }
        arg_replacements = {
            "<<KEY>>": json.dumps(item_keys),
            "<<METADATA>>": json.dumps(batch["metadata"]),
            "<<EXTRA_DATA>>": json.dumps(extra_data),
        }
        with TmpFile(mode="w+") as inp, TmpFile(mode="w+") as meta, TmpFile(mode="w+") as extra:
            json.dump(item_keys, inp)
            inp.flush()
            json.dump(batch["metadata"], meta)
            meta.flush()
            json.dump(extra_data, extra)
            extra.flush()
            arg_replacements["<<KEY_FILE>>"] = inp.name
            arg_replacements["<<METADATA_FILE>>"] = meta.name
            arg_replacements["<<EXTRA_DATA_FILE>>"] = extra.name
            for arg in self.params["args"]:
                if arg in arg_replacements:
                    cmd.append(arg_replacements[arg])
                else:
                    cmd.append(arg)
            subprocess.check_output(cmd, timeout=self.params["timeout"])

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> ScriptTransformer:
        """Produces a ScriptTransformer from the provided data.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            ScriptTransformer: An instance of the ScriptTransformer
        """
        script = data["script"]
        assert isinstance(script, str)
        args = data["args"]
        assert isinstance(args, List)
        args = [str(arg) for arg in args]
        timeout = data["timeout"]
        assert isinstance(timeout, int)
        per_item = bool(data.get("per_item", False))

        return ScriptTransformer(
            {"script": script, "args": args, "timeout": timeout, "per_item": per_item}
        )
