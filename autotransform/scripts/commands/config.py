# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The config command is used to update or list existing config values."""

import itertools
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser
from typing import Any

from autotransform.config.default import DefaultConfigFetcher
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.run import ScriptRunEvent


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to run the config comand.

    Args:
        parser (ArgumentParser): The parser for the config command.
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

    parser.set_defaults(func=config_command_main, append=False)


def config_command_main(args: Namespace) -> None:
    """The main method for the config command, handles updating the config with new values
    or listing existing config values.

    Args:
        args (Namespace): The arguments supplied to the run command, such as the schema and
            worker type
    """

    # pylint: disable=unspecified-encoding

    event_args = {}
    event_handler = EventHandler.get()

    # Get the existing config
    config = ConfigParser()
    config_path = DefaultConfigFetcher.get_config_path()
    config.read(config_path)

    # Get settings and new values
    settings = args.settings
    event_args["settings"] = args.settings
    updates = []
    should_write = False
    if args.update is not None:
        event_args["update"] = args.update
        updates = args.update.split(",")

        # Ensure an update is provided for each setting
        assert len(updates) is len(
            settings
        ), "If updates are supplied the number of updates must match the number of settings"
        should_write = True
    settings_to_values = itertools.zip_longest(settings, updates)

    event_args["append"] = "true" if args.append else "false"
    event_handler.handle(ScriptRunEvent({"script": "config", "args": event_args}))

    # Update or list settings
    for setting, update_value in settings_to_values:
        if update_value is None:
            event_handler.handle(DebugEvent({"message": f"Listing value for {setting}"}))
        else:
            event_handler.handle(DebugEvent({"message": f"Updating {setting} to {update_value}"}))

        sections = setting.split(".")
        sub_config: Any = config
        # Find the section for the config setting
        for section_index in range(len(sections) - 1):
            if sections[section_index] not in sub_config:
                sub_config[sections[section_index]] = {}
            sub_config = sub_config[sections[section_index]]

        # If no update values were provided, output the config setting
        if update_value is None:
            if sections[-1] in sub_config:
                print(f"{setting} = {sub_config[sections[-1]]}")
            else:
                print(f"No value found for {setting}")
        else:
            if sections[-1] in sub_config and args.append:
                sub_config[sections[-1]] = sub_config[sections[-1]] + "," + update_value
            else:
                sub_config[sections[-1]] = update_value

    # Update the config file
    if should_write:
        with open(config_path, "w") as config_file:
            config.write(config_file)
