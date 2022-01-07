# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

import sys
from abc import abstractmethod
from argparse import ArgumentParser, Namespace
from subprocess import Popen
from typing import List

from autotransform.worker.base import Worker
from autotransform.worker.type import WorkerType


class RunnableWorker(Worker):
    @staticmethod
    @abstractmethod
    def _parse_arguments(parser: ArgumentParser) -> Namespace:
        pass

    @classmethod
    def parse_arguments(cls) -> Namespace:
        parser = ArgumentParser(description="A local worker running a batch")
        parser.add_argument(
            "-w",
            "--worker",
            metavar="worker",
            type=str,
            required=False,
            help="The name of the worker type to use",
        )
        return cls._parse_arguments(parser)

    @staticmethod
    @abstractmethod
    def main(args: Namespace) -> None:
        pass

    @staticmethod
    def spawn_proc(worker_type: WorkerType, worker_args: List[str]) -> Popen:
        args = [sys.executable, "-m", "autotransform.instance", "-w", worker_type]
        for arg in worker_args:
            args.append(arg)
        return Popen(args)
