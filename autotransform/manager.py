# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import argparse
import sys
import time

from autotransform.common.package import AutoTransformPackage
from autotransform.common.runner import Runner
from autotransform.schema.factory import SchemaFactory
from autotransform.worker.factory import WorkerFactory


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Runs an autotransform package")
    parser.add_argument(
        "-f",
        "--file",
        metavar="file",
        type=str,
        required=False,
        help="A file containing a JSON encoded package",
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
        "-s",
        "--schema",
        metavar="schema",
        type=str,
        required=False,
        help="The name of a schema",
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
        help="The name of the worker type to use",
    )
    return parser.parse_args()


def main():
    # pylint: disable=unspecified-encoding
    args = parse_arguments()
    schema = args.schema
    file = args.file
    if file is not None and schema is not None:
        print("A schema and a file were provided, only provide one")
        sys.exit(1)
    elif file is not None:
        if args.encoding is not None:
            with open(file, "r", encoding=args.encoding) as package_file:
                package = AutoTransformPackage.from_json(package_file.read())
        else:
            with open(file, "r") as package_file:
                package = AutoTransformPackage.from_json(package_file.read())
    elif schema is not None:
        package = SchemaFactory.get(schema)
    else:
        print("Must provide either a schema name or a file containing the package")
        sys.exit(1)

    worker_type = WorkerFactory.get(args.worker)
    runner = Runner(package, worker_type)
    start_time = time.time()
    runner.start()
    while not runner.is_finished() and time.time() <= start_time + args.timeout:
        time.sleep(1)
    runner.kill()


if __name__ == "__main__":
    main()
