# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A subclass for all workers that spawn local processes using the autotransform.instance script."""

from __future__ import annotations

import sys
from abc import abstractmethod
from argparse import ArgumentParser, Namespace
from subprocess import Popen
from typing import List

from autotransform.worker.base import Worker
from autotransform.worker.type import WorkerType


class ProcessWorker(Worker):
    """The base for all Workers that leverage the autotransform.instance script for process
    spawning.
    """

    @staticmethod
    @abstractmethod
    def add_args(parser: ArgumentParser) -> None:
        """Adds the arguments needed for the worker as a subparser command

        Args:
            subparsers (_SubParsersAction): The subparsers action to add the parser to
        """

    @staticmethod
    @abstractmethod
    def main(args: Namespace) -> None:
        """Run the Worker with the provided arguments

        Args:
            args (Namespace): The arguments required to run the Worker
        """

    @staticmethod
    def spawn_proc(worker_type: WorkerType, worker_args: List[str]) -> Popen:
        """Spawn a process locally to run a Worker using the autotransform.instance script.

        Args:
            worker_type (WorkerType): The type of Worker to spawn
            worker_args (List[str]): Any arguments needed by the worker

        Returns:
            Popen: A handle for the process running the Worker
        """
        args = [sys.executable, "-m", "autotransform.scripts.main", "i", worker_type.value]
        for arg in worker_args:
            args.append(arg)
        return Popen(args)
