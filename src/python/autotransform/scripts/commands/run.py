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

from autotransform.config import get_config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.logginglevel import LoggingLevel
from autotransform.event.run import ScriptRunEvent
from autotransform.event.verbose import VerboseEvent
from autotransform.filter.base import FACTORY as filter_factory
from autotransform.runner.base import Runner
from autotransform.runner.local import LocalRunner
from autotransform.schema.builder import FACTORY as schema_builder_factory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.schema_map import SchemaMap


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
        "environment variable name, or builder name.",
    )

    parser.add_argument(
        "--filter",
        metavar="filter",
        type=str,
        help="A JSON encoded filter to add to the schema.",
    )

    parser.add_argument(
        "--max-submissions",
        metavar="max_submissions",
        type=int,
        help="An override to the maximum submissions a schema can produce.",
    )

    logging_level = parser.add_mutually_exclusive_group()
    logging_level.add_argument(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Tells the script to output verbose logs.",
    )
    logging_level.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Tells the script to output debug logs.",
    )

    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        "-b",
        "--builder",
        dest="schema_type",
        action="store_const",
        const="builder",
        help="Tells the script to interpret the schema as a builder name.",
    )
    type_group.add_argument(
        "-f",
        "--file",
        dest="schema_type",
        action="store_const",
        const="file",
        help="Tells the script to interpret the schema as a file path.",
    )
    type_group.add_argument(
        "-s",
        "--string",
        dest="schema_type",
        action="store_const",
        const="string",
        help="Tells the script to interpret the schema as a JSON encoded string",
    )
    type_group.add_argument(
        "-e",
        "--environment",
        dest="schema_type",
        action="store_const",
        const="environment",
        help="Tells the script to interpret the schema as an environment variable storing the JSON "
        "encoded schema.",
    )
    type_group.add_argument(
        "-n",
        "--name",
        dest="schema_type",
        action="store_const",
        const="name",
        help="Tells the script to interpret the schema as a name stored in schema_map.json.",
    )

    # Run Mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-l",
        "--local",
        dest="run_local",
        action="store_true",
        help="Tells the script to run locally, local is the default mode.",
    )
    mode_group.add_argument(
        "-r",
        "--remote",
        dest="run_local",
        action="store_false",
        help="Tells the script to run remote using the remote component from the config.",
    )

    parser.set_defaults(schema_type="file", run_local=True, func=run_command_main)


def run_command_main(args: Namespace) -> None:
    """The main method for the run command, handles the actual execution of a run.

    Args:
        args (Namespace): The arguments supplied to the run command, such as the schema.
    """

    event_handler = EventHandler.get()
    if args.verbose:
        event_handler.set_logging_level(LoggingLevel.VERBOSE)
    elif args.debug:
        event_handler.set_logging_level(LoggingLevel.DEBUG)

    schema = args.schema
    event_handler.handle(DebugEvent({"message": f"Schema: ({args.schema_type}) {args.schema}"}))

    if args.schema_type == "builder":
        schema = json.loads(schema) if schema else {"name": schema}
        schema = schema_builder_factory.get_instance(schema).build()
    elif args.schema_type == "file":
        with open(schema, "r", encoding="utf-8") as schema_file:
            schema = AutoTransformSchema.from_data(json.loads(schema_file.read()))
    elif args.schema_type == "environment":
        schema = AutoTransformSchema.from_data(json.loads(os.getenv(schema) or ""))
    elif args.schema_type == "name":
        schema = SchemaMap.get().get_schema(args.schema)
    else:
        schema = AutoTransformSchema.from_data(json.loads(schema))

    repo_override = get_config().repo_override
    if repo_override is not None:
        schema.repo = repo_override

    if args.filter:
        schema.filters.append(filter_factory.get_instance(json.loads(args.filter)))

    if args.max_submissions:
        schema.config.max_submissions = args.max_submissions

    event_handler.handle(VerboseEvent({"message": f"Decoded Schema: {schema!r}"}))

    event_args = {
        "schema": args.schema,
        "schema_type": args.schema_type,
        "remote": not args.run_local,
    }
    config_runner = get_config().local_runner if args.run_local else get_config().remote_runner
    runner: Runner = config_runner if config_runner else LocalRunner()

    event_handler.handle(
        VerboseEvent({"message": "Running locally" if args.run_local else "Running remote"})
    )
    if not config_runner:
        event_handler.handle(DebugEvent({"message": "No runner defined, using default"}))
    event_args["runner"] = runner
    event_handler.handle(ScriptRunEvent({"script": "run", "args": event_args}))
    runner.run(schema)
