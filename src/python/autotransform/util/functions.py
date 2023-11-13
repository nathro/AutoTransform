# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Utility functions used by multiple components."""

import json
import os
import re
import subprocess
from tempfile import NamedTemporaryFile as TmpFile
from typing import Any, Dict, List, Mapping, Optional, Sequence

from autotransform.event.handler import EventHandler
from autotransform.event.script import ScriptErrEvent, ScriptOutEvent, ScriptRunEvent
from autotransform.item.base import Item


def run_cmd_on_items(
    cmd: List[str],
    items: Sequence[Item],
    batch_metadata: Mapping[str, Any],
    timeout: Optional[int] = None,
) -> subprocess.CompletedProcess:
    """Creates and runs a subprocess based on supplied command and replacements.

    Args:
        cmd (List[str]): The command to run.
        items (Sequence[Item]): The items that are being run on.
        batch_metadata (Mapping[str, Any]): The metadata for the batch.
        timeout (optional, Optional[int]): A timeout for the subprocess run. Defaults to None.

    Returns:
        subprocess.CompletedProcess: The completed process run.
    """

    item_keys = [item.key for item in items]
    extra_data = {item.key: item.extra_data for item in items if item.extra_data is not None}

    arg_replacements = {
        "<<KEY>>": item_keys,
        "<<EXTRA_DATA>>": [json.dumps(extra_data)],
        "<<METADATA>>": [json.dumps(batch_metadata)],
    }
    for arg in cmd:
        m = re.match(r"^<<EXTRA_DATA\/(.*)>>$", arg)
        if m is not None and len(m.groups()) == 1:
            key = m.groups()[0]
            arg_replacements[f"<<EXTRA_DATA/{key}>>"] = [
                str(val.get(key)) for val in extra_data.values() if val.get(key) is not None
            ]

    with TmpFile(mode="w+") as inp, TmpFile(mode="w+") as meta, TmpFile(mode="w+") as extra:
        # Make key file
        json.dump(item_keys, inp)
        inp.flush()
        arg_replacements["<<KEY_FILE>>"] = [inp.name]

        # Make extra_data file
        json.dump(extra_data, extra)
        extra.flush()
        arg_replacements["<<EXTRA_DATA_FILE>>"] = [extra.name]

        # Make metadata file
        json.dump(batch_metadata, meta)
        meta.flush()
        arg_replacements["<<METADATA_FILE>>"] = [meta.name]

        # Create command
        replaced_cmd = replace_script_args(cmd, arg_replacements)

        return run_cmd(replaced_cmd, timeout)


def replace_script_args(args: List[str], replacements: Dict[str, List[str]]) -> List[str]:
    """Replaces arguments in a list with replacements that are supplied.

    Args:
        args (List[str]): The argument list.
        replacements (Dict[str, Tuple[List[str], bool]]): Maps a value to the list of args that
            replaces it.

    Returns:
        List[str]: The list of args with replacements.
    """

    script_replacements = os.getenv("AUTO_TRANSFORM_SCRIPT_REPLACEMENTS")
    if script_replacements:
        env_replacements: Dict[str, List[str]] = json.loads(script_replacements)
    else:
        env_replacements = {}

    replaced_args = []
    for arg in args:
        if arg in replacements:
            replaced_args.extend(replacements[arg])
        elif arg in env_replacements:
            replaced_args.extend(env_replacements[arg])
        else:
            replaced_args.append(arg)
    return replaced_args


def run_cmd(cmd: List[str], timeout: Optional[int] = None) -> subprocess.CompletedProcess:
    """Run a script

    Args:
        cmd (List[str]): The command to run.
        timeout (optional, Optional[int]): A timeout for the subprocess run. Defaults to None.

    Returns:
        subprocess.CompletedProcess: The completed process run.
    """

    event_handler = EventHandler.get()

    event_handler.handle(ScriptRunEvent({"command": cmd}))
    proc = subprocess.run(cmd, capture_output=True, encoding="utf-8", check=False, timeout=timeout)

    stdout = proc.stdout.strip()
    if stdout:
        event_handler.handle(ScriptOutEvent({"proc": proc}))

    stderr = proc.stderr.strip()
    if stderr:
        event_handler.handle(ScriptErrEvent({"proc": proc}))

    return proc
