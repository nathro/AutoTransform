# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

import argparse
import json
import os
import subprocess
import sys
import tempfile
from typing import List, Optional

from autotransform.batcher.base import BatchWithFiles
from autotransform.common.cachedfile import CachedFile
from autotransform.common.package import AutoTransformPackage
from autotransform.worker.base import Worker


class LocalWorker(Worker):
    data_file: str
    proc: Optional[subprocess.Popen]

    def __init__(self, data_file: str):
        Worker.__init__(self)
        self.data_file = data_file
        self.proc = None

    def is_finished(self) -> bool:
        proc = self.proc
        assert proc is not None
        return proc.poll() is not None

    def start(self) -> None:
        # pylint: disable=consider-using-with
        self.proc = subprocess.Popen(
            [sys.executable, "-m", "autotransform.worker.local", self.data_file]
        )

    @staticmethod
    def spawn_from_batches(
        package: AutoTransformPackage, batches: List[BatchWithFiles]
    ) -> List[Worker]:
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


def parse_arguments():
    parser = argparse.ArgumentParser(description="A local worker running a batch")
    parser.add_argument(
        "data_file",
        metavar="data_file",
        type=str,
        help="The file containing a JSON encoded batch",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    with open(args.data_file, "r", encoding="utf8") as data_file:
        data = json.loads(data_file.read())
        package = AutoTransformPackage.from_bundle(data["package"])
        encoded_batches = data["batches"]
        batches = [
            {"files": [CachedFile(path) for path in batch["files"]], "metadata": batch["metadata"]}
            for batch in encoded_batches
        ]
        for batch in batches:
            package.execute_batch(batch)


if __name__ == "__main__":
    main()
