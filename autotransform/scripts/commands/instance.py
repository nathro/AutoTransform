# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The instance command is used to run an instance of a process worker"""

from argparse import ArgumentParser

from autotransform.worker.factory import WorkerFactory
from autotransform.worker.process import ProcessWorker
from autotransform.worker.type import WorkerType


def add_args(parser: ArgumentParser) -> None:
    """Adds the instance command arguments

    Args:
        subparsers (_SubParsersAction[ArgumentParser]): The subparsers for the command
    """
    subparsers = parser.add_subparsers()
    for worker_type in WorkerType:
        worker = WorkerFactory.get(worker_type)
        if issubclass(worker, ProcessWorker):
            worker_parser = subparsers.add_parser(worker_type.value)
            worker.add_args(worker_parser)
