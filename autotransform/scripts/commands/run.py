# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The instance command is used to run an instance of a process worker"""

import json
import os
import time
from argparse import ArgumentParser, Namespace

from autotransform.config import fetcher as Config
from autotransform.remote.factory import RemoteFactory
from autotransform.schema.factory import SchemaBuilderFactory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.coordinator import Coordinator
from autotransform.worker.factory import WorkerFactory
from autotransform.worker.type import WorkerType


def add_args(parser: ArgumentParser) -> None:
    """Adds the run command arguments

    Args:
        parser (ArgumentParser): The parser for the command
    """

    parser.add_argument(
        "schema",
        metavar="schema",
        type=str,
        help="The schema to be used, defaults to assuming a file",
    )

    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument(
        "-b",
        "--builder",
        dest="schema_type",
        action="store_const",
        const="builder",
        required=False,
        help="Tells the script to interpret the schema as a builder name",
    )
    type_group.add_argument(
        "-f",
        "--file",
        dest="schema_type",
        action="store_const",
        const="file",
        required=False,
        help="Tells the script to interpret the schema as a file",
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
        + "encoded schema",
    )

    # Setting Arguments
    parser.add_argument(
        "-t",
        "--timeout",
        metavar="timeout",
        type=int,
        required=False,
        default=360,
        help="How long in seconds to allow the process to run",
    )
    parser.add_argument(
        "-w",
        "--worker",
        metavar="worker",
        type=str,
        required=False,
        help="The type of worker to use(see worker.type). Defaults to using local",
    )

    # Run Mode
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-l",
        "--local",
        dest="run_local",
        action="store_true",
        required=False,
        help="Tells the script to run locally, local is the default mode",
    )
    mode_group.add_argument(
        "-r",
        "--remote",
        dest="run_local",
        action="store_false",
        required=False,
        help="Tells the script to run remote using the remote component from the config",
    )

    parser.set_defaults(schema_type="file", worker="local", run_local=True, func=run_command_main)


def run_command_main(args: Namespace) -> None:
    """The main method for the run command, handles the actual execution of a run.

    Args:
        args (Namespace): The arguments supplied to the run command, such as the schema and
            worker type
    """
    # pylint: disable=unspecified-encoding

    schema = args.schema
    print(schema)
    if args.schema_type == "builder":
        schema = SchemaBuilderFactory.get(schema).build()
    elif args.schema_type == "file":
        with open(schema, "r") as schema_file:
            schema = AutoTransformSchema.from_json(schema_file.read())
    elif args.schema_type == "environment":
        schema = os.getenv(schema)
        assert isinstance(schema, str)
        schema = AutoTransformSchema.from_json(schema)
    else:
        schema = AutoTransformSchema.from_json(schema)

    worker = args.worker
    worker_type = WorkerFactory.get(worker)
    if args.run_local:
        coordinator = Coordinator(schema, worker_type)
        start_time = time.time()
        coordinator.start()
        while not coordinator.is_finished() and time.time() <= start_time + args.timeout:
            time.sleep(1)
        coordinator.kill()
    else:
        remote_str = Config.get_remote()
        assert remote_str is not None, "Remote not specified in config"
        remote = RemoteFactory.get(json.loads(remote_str))
        remote_ref = remote.run(schema)
        print(f"Remote ref: {remote_ref}")
