# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from __future__ import annotations

import sys
from abc import abstractmethod
from argparse import Namespace
from subprocess import Popen
from typing import List

from autotransform.worker.base import Worker
from autotransform.worker.type import WorkerType


class RunnableWorker(Worker):
    @staticmethod
    @abstractmethod
    def parse_arguments() -> Namespace:
        pass

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
