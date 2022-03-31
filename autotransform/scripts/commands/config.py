# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The instance command is used to run an instance of a process worker"""

import itertools
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from typing import Any

from autotransform.config.default import DefaultConfigFetcher


def add_args(parser: ArgumentParser) -> None:
    """Adds the config command arguments

    Args:
        parser (ArgumentParser): The parser for the command
    """

    parser.add_argument(
        "-u",
        "--update",
        metavar="update",
        type=str,
        required=False,
        help="A JSON encoded list of values to supply for the settings.",
    )
    parser.add_argument(
        "-a",
        "--append",
        dest="append",
        action="store_true",
        required=False,
        help="Appends the update value to the end of the existing value as a comma separated list.",
    )
    parser.add_argument(
        "settings",
        metavar="setting",
        type=str,
        nargs="+",
        help="The setting in the config file being listed or updated. Sections should be separated"
        + " with periods: <SECTION>.<SETTING>",
    )

    parser.set_defaults(func=run_config_main)


def run_config_main(args: Namespace) -> None:
    """The main method for the config command, handles updating the config with new values.

    Args:
        args (Namespace): The arguments supplied to the run command, such as the schema and
            worker type
    """

    # pylint: disable=unspecified-encoding

    config = ConfigParser()
    config_path = DefaultConfigFetcher.get_config_path()
    config.read(config_path)
    settings = args.settings
    updates = []
    should_write = False
    if args.update is not None:
        updates = args.update.split(",")
        assert len(updates) is len(
            settings
        ), "If updates are supplied the number of updates must match the number of settings"
        should_write = True

    settings_to_values = itertools.zip_longest(settings, updates)
    for setting, update_value in settings_to_values:
        sections = setting.split(".")
        sub_config: Any = config
        for section_index in range(len(sections) - 1):
            if sections[section_index] not in sub_config:
                sub_config[sections[section_index]] = {}
            sub_config = sub_config[sections[section_index]]
        if update_value is None:
            if sections[-1] in sub_config:
                print(f"{setting} = {sub_config[sections[-1]]}")
            else:
                print(f"No value found for {setting}")
        else:
            if sections[-1] in sub_config:
                sub_config[sections[-1]] = sub_config[sections[-1]] + "," + update_value
            else:
                sub_config[sections[-1]] = update_value
    if should_write:
        with open(config_path, "w") as config_file:
            config.write(config_file)
