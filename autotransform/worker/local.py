# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import json
import os
import tempfile
from argparse import ArgumentParser, Namespace
from subprocess import Popen
from typing import List, Optional, Sequence

from autotransform.batcher.base import BatchWithFiles
from autotransform.common.cachedfile import CachedFile
from autotransform.common.package import AutoTransformPackage
from autotransform.worker.runnable import RunnableWorker
from autotransform.worker.type import WorkerType


class LocalWorker(RunnableWorker):
    data_file: str
    proc: Optional[Popen]

    def __init__(self, data_file: str):
        RunnableWorker.__init__(self)
        self.data_file = data_file
        self.proc = None

    def is_finished(self) -> bool:
        proc = self.proc
        assert proc is not None
        return proc.poll() is not None

    def start(self) -> None:
        # pylint: disable=consider-using-with
        self.proc = RunnableWorker.spawn_proc(WorkerType.LOCAL, [self.data_file])

    @staticmethod
    def spawn_from_batches(
        package: AutoTransformPackage, batches: List[BatchWithFiles]
    ) -> Sequence[RunnableWorker]:
        # pylint: disable=consider-using-with

        data_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf8", delete=False)
        encodable_batches = [
            {"files": [file.path for file in batch["files"]], "metadata": batch["metadata"]}
            for batch in batches
        ]
        full_data = {"batches": encodable_batches, "package": package.bundle()}
        json.dump(full_data, data_file)
        data_file.close()

        return [LocalWorker(data_file.name)]

    def kill(self):
        os.unlink(self.data_file)
        proc = self.proc
        if proc is not None:
            proc.kill()

    @staticmethod
    def parse_arguments() -> Namespace:
        parser = ArgumentParser(description="A local worker running a batch")
        parser.add_argument(
            "data_file",
            metavar="data_file",
            type=str,
            help="The file containing a JSON encoded batch",
        )
        args, _ = parser.parse_known_args()
        return args

    @staticmethod
    def main(args: Namespace) -> None:
        with open(args.data_file, "r", encoding="utf8") as data_file:
            data = json.loads(data_file.read())
            package = AutoTransformPackage.from_bundle(data["package"])
            encoded_batches = data["batches"]
            batches: List[BatchWithFiles] = [
                {
                    "files": [CachedFile(path) for path in batch["files"]],
                    "metadata": batch["metadata"],
                }
                for batch in encoded_batches
            ]
            for batch in batches:
                package.execute_batch(batch)
