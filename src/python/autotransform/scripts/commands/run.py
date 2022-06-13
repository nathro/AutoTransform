# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The run command is used to execute a full run of a schema, either locally
or by kicking off a remote job."""

import json
import os
from argparse import ArgumentParser, Namespace

import autotransform.config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
from autotransform.runner.base import Runner
from autotransform.runner.local import LocalRunner
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to run a schema.

    Args:
        parser (ArgumentParser): The parser for the schema run.
    """

    parser.add_argument(
        "schema",
        metavar="schema",
        type=str,
        help="The schema that will be run. Could be a file path, string, "
        + "environment variable name, or builder name.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        required=False,
        help="Tells the script to output verbose logs.",
    )

    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        "-b",
        "--builder",
        dest="schema_type",
        action="store_const",
        const="builder",
        required=False,
        help="Tells the script to interpret the schema as a builder name.",
    )
    type_group.add_argument(
        "-f",
        "--file",
        dest="schema_type",
        action="store_const",
        const="file",
        required=False,
        help="Tells the script to interpret the schema as a file path.",
    )
    type_group.add_argument(
        "-s",
        "--string",
        dest="schema_type",
        action="store_const",
        const="string",
        required=False,
        help="Tells the script to interpret the schema as a JSON encoded string",
    )
    type_group.add_argument(
        "-e",
        "--environment",
        dest="schema_type",
        action="store_const",
        const="environment",
        required=False,
        help="Tells the script to interpret the schema as an environment variable storing the JSON "
        + "encoded schema.",
    )

    # Run Mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-l",
        "--local",
        dest="run_local",
        action="store_true",
        required=False,
        help="Tells the script to run locally, local is the default mode.",
    )
    mode_group.add_argument(
        "-r",
        "--remote",
        dest="run_local",
        action="store_false",
        required=False,
        help="Tells the script to run remote using the remote component from the config.",
    )

    parser.set_defaults(schema_type="file", run_local=True, func=run_command_main)


def run_command_main(args: Namespace) -> None:
    """The main method for the run command, handles the actual execution of a run.

    Args:
        args (Namespace): The arguments supplied to the run command, such as the schema.
    """

    # pylint: disable=unspecified-encoding

    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.DEBUG)
    schema = args.schema
    event_handler.handle(DebugEvent({"message": f"Schema: ({args.schema_type}) {args.schema}"}))
    event_args = {"schema": args.schema, "schema_type": args.schema_type}
    if args.schema_type == "builder":
        try:
            schema = json.loads(schema)
        except json.JSONDecodeError:
            schema = {"name": schema}
        schema = schema_builder_factory.get_instance(schema).build()
    elif args.schema_type == "file":
        with open(schema, "r") as schema_file:
            schema = AutoTransformSchema.from_data(json.loads(schema_file.read()))
    elif args.schema_type == "environment":
        schema = os.getenv(schema)
        assert isinstance(schema, str)
        schema = AutoTransformSchema.from_data(json.loads(schema))
    else:
        schema = AutoTransformSchema.from_data(json.loads(schema))

    if args.schema_type != "string":
        event_handler.handle(DebugEvent({"message": f"JSON Schema: {json.dumps(schema.bundle())}"}))

    if args.run_local:
        event_handler.handle(DebugEvent({"message": "Running locally"}))
        event_args["remote"] = False
        config_runner = autotransform.config.CONFIG.local_runner
        if config_runner is None:
            event_handler.handle(DebugEvent({"message": "No runner defined, using default"}))
            runner: Runner = LocalRunner()
        else:
            runner = config_runner
    else:
        event_handler.handle(DebugEvent({"message": "Running remote"}))
        event_args["remote"] = True
        config_runner = autotransform.config.CONFIG.remote_runner
        assert config_runner is not None
        runner = config_runner

    event_args["runner"] = runner
    event_handler.handle(ScriptRunEvent({"script": "run", "args": event_args}))
    runner.run(schema)
