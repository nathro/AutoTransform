# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for script based Inputs."""

from __future__ import annotations

import json
import subprocess
from tempfile import NamedTemporaryFile
from typing import ClassVar, List, Sequence

from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.input.base import Input, InputName
from autotransform.item.base import FACTORY as item_factory
from autotransform.item.base import Item
from autotransform.util.functions import replace_script_args


class ScriptInput(Input):
    """An Input that uses a script to generate a list of Items.

    Attributes:
        args (List[str]): The arguments to supply to the script.
        script (str): The script to run.
        timeout (int): The timeout to use for the script process.
        name (ClassVar[InputName]): The name of the component.
    """

    args: List[str]
    script: str
    timeout: int

    name: ClassVar[InputName] = InputName.SCRIPT

    def get_items(self) -> Sequence[Item]:
        """Uses a simple script to generate a list of Items. If a <<RESULT_FILE>> arg is used
        it will be replaced with the path of a temporary file that can be used to store a JSON
        encoded list of Items that will be returned. If no such arg is used, the STDOUT of the
        script will be interpreted as a JSON encoded list of Items.

        Returns:
            Sequence[Item]: The supplied Items.
        """

        event_handler = EventHandler.get()

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        with NamedTemporaryFile(mode="r+b") as result_file:
            arg_replacements = {"<<RESULT_FILE>>": [result_file.name]}
            uses_result_file = "<<RESULT_FILE>>" in cmd
            replaced_cmd = replace_script_args(cmd, arg_replacements)

            # Run script
            event_handler.handle(VerboseEvent({"message": f"Running command: {replaced_cmd}"}))
            proc = subprocess.run(
                replaced_cmd,
                capture_output=True,
                encoding="utf-8",
                check=False,
                timeout=self.timeout,
            )

            if proc.stdout.strip() != "" and uses_result_file:
                event_handler.handle(VerboseEvent({"message": f"STDOUT:\n{proc.stdout.strip()}"}))
            elif uses_result_file:
                event_handler.handle(VerboseEvent({"message": "No STDOUT"}))

            if proc.stderr.strip() != "":
                event_handler.handle(VerboseEvent({"message": f"STDERR:\n{proc.stderr.strip()}"}))
            else:
                event_handler.handle(VerboseEvent({"message": "No STDERR"}))
            proc.check_returncode()
            if uses_result_file:
                with open(result_file.name, encoding="utf-8") as results:
                    item_data = json.loads(results.read())
            else:
                item_data = json.loads(proc.stdout.strip())
        return [item_factory.get_instance(item) for item in item_data]
