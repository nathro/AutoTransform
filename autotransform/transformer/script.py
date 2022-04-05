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
from tempfile import NamedTemporaryFile
from typing import Any, List, Mapping, TypedDict

from autotransform.batcher.base import Batch
from autotransform.transformer.base import Transformer
from autotransform.transformer.type import TransformerType


class ScriptTransformerParams(TypedDict):
    """The param type for a ScriptTransformer."""

    script: str
    args: List[str]
    timeout: int


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
        """Execute a transformation against the provided batch. Additional files may be modified
        based on these changes (i.e. as part of a rename) and should be done as part of this
        transform rather than using separate calls to transform. All writing should be done via
        CachedFile's write_content method to ensure operations are easily accessible to testing.

        Args:
            batch (Batch): The batch that will be transformed
        """
        cmd = [self.params["script"]]
        arg_replacements = {
            "<<INPUT>>": json.dumps(batch["files"]),
            "<<METADATA>>": json.dumps(batch["metadata"]),
        }
        with NamedTemporaryFile(mode="w+") as inp_file, NamedTemporaryFile(mode="w+") as meta_file:
            json.dump(batch["files"], inp_file)
            inp_file.flush()
            json.dump(batch["metadata"], meta_file)
            meta_file.flush()
            arg_replacements["<<INPUT_FILE>>"] = inp_file.name
            arg_replacements["<<METADATA_FILE>>"] = meta_file.name
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

        return ScriptTransformer({"script": script, "args": args, "timeout": timeout})
