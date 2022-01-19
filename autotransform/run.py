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
import sys
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
    parser.add_argument(
        "-f",
        "--file",
        metavar="file",
        type=str,
        required=False,
        help="A file containing a JSON encoded schema",
    )
    parser.add_argument(
        "-e",
        "--encoding",
        metavar="encoding",
        type=str,
        required=False,
        help="How long in seconds to allow the process to run",
    )
    parser.add_argument(
        "-b",
        "--builder",
        metavar="builder",
        type=str,
        required=False,
        help="The name of a schema builder(see schema.name)",
    )
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
        help="The type of worker to use(see worker.type)",
    )
    return parser.parse_args()


def main():
    """A full run of AutoTransform from the provided Schema."""

    # pylint: disable=unspecified-encoding

    args = parse_arguments()
    builder = args.builder
    file = args.file
    if file is not None and builder is not None:
        print("A schema and a file were provided, only provide one")
        sys.exit(1)
    elif file is not None:
        if args.encoding is not None:
            with open(file, "r", encoding=args.encoding) as schema_file:
                schema = AutoTransformSchema.from_json(schema_file.read())
        else:
            with open(file, "r") as schema_file:
                schema = AutoTransformSchema.from_json(schema_file.read())
    elif builder is not None:
        schema = SchemaBuilderFactory.get(builder).build()
    else:
        print("Must provide either a builder name or a file containing the schema as JSON")
        sys.exit(1)

    worker = args.worker
    if worker is None:
        worker = WorkerType.LOCAL
    worker_type = WorkerFactory.get(worker)
    runner = Coordinator(schema, worker_type)
    start_time = time.time()
    runner.start()
    while not runner.is_finished() and time.time() <= start_time + args.timeout:
        time.sleep(1)
    runner.kill()


if __name__ == "__main__":
    main()
