# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for script based Filters."""

from __future__ import annotations

import json
from tempfile import NamedTemporaryFile as TmpFile
from typing import ClassVar, List, Optional, Sequence, Set

from autotransform.filter.base import BulkFilter, FilterName
from autotransform.item.base import Item
from autotransform.util.functions import replace_script_args, run_cmd


class ScriptFilter(BulkFilter):
    """A Filter that uses a script to validate Items.

    Attributes:
        args (List[str]): The arguments to supply to the script.
        script (str): The script to run.
        timeout (int): The timeout to use for the script process.
        chunk_size (Optional[int], optional): The maximum number of items per run of the
            script. If None, then no chunking is used. Defaults to None.
        name (ClassVar[FilterName]): The name of the component.
    """

    args: List[str]
    script: str
    timeout: int

    chunk_size: Optional[int] = None

    name: ClassVar[FilterName] = FilterName.SCRIPT

    def _get_valid_keys(self, items: Sequence[Item]) -> Set[str]:
        """Gets the valid keys from the Items using a script. If a <<RESULT_FILE>> arg is used
        it will be replaced with the path of a temporary file that can be used to store a JSON
        encoded list of keys for valid Items. If no such arg is used, the STDOUT of the script
        will be interpreted as a JSON encoded list of keys for valid Items. Additionally, the
        <<ITEM_FILE>> argument will be replaced with the path to a file containing a JSON
        encoded list of the items to validate.

        Args:
            items (Sequence[Item]): The Items to check for valid items.

        Returns:
            Set[str]: The keys of the valid Items.
        """

        # Get Command
        cmd = [self.script]
        cmd.extend(self.args)

        chunk_size = self.chunk_size or len(items)
        item_chunks = [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]

        valid_keys: Set[str] = set()
        for chunk in item_chunks:
            with TmpFile(mode="r+b") as res_file, TmpFile(mode="w+") as item_file:
                json.dump([item.bundle() for item in chunk], item_file)
                item_file.flush()
                arg_replacements = {
                    "<<RESULT_FILE>>": [res_file.name],
                    "<<ITEM_FILE>>": [item_file.name],
                }
                uses_result_file = "<<RESULT_FILE>>" in cmd
                replaced_cmd = replace_script_args(cmd, arg_replacements)

                # Run script
                proc = run_cmd(replaced_cmd, self.timeout)
                proc.check_returncode()

                if uses_result_file:
                    with open(res_file.name, encoding="utf-8") as results:
                        key_data = json.loads(results.read())
                else:
                    key_data = json.loads(proc.stdout.strip())
                valid_keys = valid_keys.union(set(key_data))
        return valid_keys
