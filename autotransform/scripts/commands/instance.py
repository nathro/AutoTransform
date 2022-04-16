# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The instance command is used to run an instance of a ProcessWorker."""

import importlib
from argparse import ArgumentParser

from autotransform.config import fetcher as Config
from autotransform.worker.factory import WorkerFactory
from autotransform.worker.process import ProcessWorker
from autotransform.worker.type import WorkerType


def add_args(parser: ArgumentParser) -> None:
    """Adds the args to a subparser that are required to run the instance comand.

    Args:
        parser (ArgumentParser): The parser for the instance command.
    """
    subparsers = parser.add_subparsers()
    for worker_type in WorkerType:
        worker = WorkerFactory.get(worker_type)
        if issubclass(worker, ProcessWorker):
            # Each worker gets it's own subparser
            worker_parser = subparsers.add_parser(worker_type.value)
            worker.add_args(worker_parser)

    # Check for custom module workers
    custom_component_modules = Config.get_imports_components()
    for module_string in custom_component_modules:
        module = importlib.import_module(module_string)
        if hasattr(module, "WORKERS"):
            for worker_type, worker in module.WORKERS.items():
                if issubclass(worker, ProcessWorker):
                    # Each worker gets it's own subparser
                    worker_parser = subparsers.add_parser(worker_type)
                    worker.add_args(worker_parser)
