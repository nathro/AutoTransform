# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A script for running instances of RunnableWorker on a machine."""

import argparse

from autotransform.worker.factory import WorkerFactory
from autotransform.worker.process import ProcessWorker


def parse_arguments() -> argparse.Namespace:
    """Parses the script arguments. These should not be directly interacted with by an end user,
    they should be handled by the RunnableWorker object.

    Returns:
        argparse.Namespace: The arguments for the run
    """
    parser = argparse.ArgumentParser(description="Runs an autotransform package")
    parser.add_argument(
        "-w",
        "--worker",
        metavar="worker",
        type=str,
        required=True,
        help="The name of the worker type to use",
    )
    args, _ = parser.parse_known_args()
    return args


def main():
    """Runs the Worker."""
    args = parse_arguments()
    worker_type = WorkerFactory.get(args.worker)
    assert issubclass(worker_type, ProcessWorker)
    worker_args = worker_type.parse_arguments()
    worker_type.main(worker_args)


if __name__ == "__main__":
    main()
