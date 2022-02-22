# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A script for triggering a Schema run from a JSON encoded Schema or a
Schema provided by a SchemaBuilder.
"""

import argparse
import time

from autotransform.coordinator import Coordinator
from autotransform.schema.factory import SchemaBuilderFactory
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.factory import WorkerFactory
from autotransform.worker.type import WorkerType


def parse_arguments() -> argparse.Namespace:
    """Parses the script arguments. Run with -h to see all arguments.

    Returns:
        argparse.Namespace: The arguments for the run
    """
    parser = argparse.ArgumentParser(description="Runs an autotransform schema")

    # Schema Arguments
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
        dest="use_builder",
        action="store_true",
        required=False,
        help="Tells the script to interpret the schema as a builder name",
    )
    type_group.add_argument(
        "-f",
        "--file",
        dest="use_builder",
        action="store_false",
        required=False,
        help="Tells the script to interpret the schema as a file",
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

    parser.set_defaults(use_builder=False, worker=WorkerType.LOCAL)
    return parser.parse_args()


def main():
    """A full run of AutoTransform from the provided Schema."""

    # pylint: disable=unspecified-encoding

    args = parse_arguments()
    schema = args.schema
    if args.use_builder:
        schema = SchemaBuilderFactory.get(schema).build()
    else:
        with open(schema, "r") as schema_file:
            schema = AutoTransformSchema.from_json(schema_file.read())

    worker = args.worker
    worker_type = WorkerFactory.get(worker)
    runner = Coordinator(schema, worker_type)
    start_time = time.time()
    runner.start()
    while not runner.is_finished() and time.time() <= start_time + args.timeout:
        time.sleep(1)
    runner.kill()


if __name__ == "__main__":
    main()
