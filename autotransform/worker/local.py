# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The implementation for a LocalWorker."""

import json
import os
import tempfile
from argparse import ArgumentParser, Namespace
from subprocess import Popen
from typing import List, Optional, Sequence

from autotransform.batcher.base import Batch
from autotransform.common.cachedfile import CachedFile
from autotransform.common.dataobject import FileDataObject
from autotransform.common.datastore import data_store
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.process import ProcessWorker
from autotransform.worker.type import WorkerType


class LocalWorker(ProcessWorker):
    """A Worker that is run locally by the Runner and merely executes the batches in a subprocess.

    Attributes:
        data_file (str): The path to a temp file containing the information required to run the
            Worker
        proc (Optional[Popen]): A handle of the subprocess the Worker spawned to execute it's work
    """

    data_file: str
    proc: Optional[Popen]

    def __init__(self, data_file: str):
        """A simple constructor

        Args:
            data_file (str): The path to a temp file containing the information required to run the
                Worker
        """
        ProcessWorker.__init__(self)
        self.data_file = data_file
        self.proc = None

    @staticmethod
    def get_type() -> WorkerType:
        """Gets the type of the worker

        Returns:
            WorkerType: The type of the worker object
        """
        return WorkerType.LOCAL

    def is_finished(self) -> bool:
        """Checks whether the subprocess has finished

        Returns:
            bool: Returns True if the subprocess is complete
        """
        proc = self.proc
        assert proc is not None
        return proc.poll() is not None

    def start(self) -> None:
        """Spawns a subprocess using autotransform.instance to run the work"""

        # pylint: disable=consider-using-with

        self.proc = ProcessWorker.spawn_proc(WorkerType.LOCAL, [self.data_file])

    @staticmethod
    def spawn_from_batches(
        schema: AutoTransformSchema, batches: List[Batch]
    ) -> Sequence[ProcessWorker]:
        """Sets up a data file with the batches and schema, creating a LocalWorker based on
        this data file.

        Args:
            schema (AutoTransformSchema): The Schema that is being run
            batches (List[Batch]): The Batches that have been found for the Schema

        Returns:
            Sequence[RunnableWorker]: A list containing a single Worker to execute all Batches
        """
        # pylint: disable=consider-using-with

        data_file = tempfile.NamedTemporaryFile(mode="w+", encoding="utf8", delete=False)
        encodable_batches = [
            {"files": [file.path for file in batch["files"]], "metadata": batch["metadata"]}
            for batch in batches
        ]
        encodable_file_data = {}
        for batch in batches:
            for file in batch["files"]:
                data_object = data_store.get_object_data(file.path)
                if data_object is not None:
                    encodable_file_data[file.path] = data_object.data
        full_data = {
            "batches": encodable_batches,
            "schema": schema.bundle(),
            "file_data": encodable_file_data,
        }
        json.dump(full_data, data_file)
        data_file.close()

        return [LocalWorker(data_file.name)]

    def kill(self):
        """Removes the temp file and kills the subprocess."""
        os.unlink(self.data_file)
        proc = self.proc
        if proc is not None:
            proc.kill()

    @staticmethod
    def add_args(parser: ArgumentParser) -> None:
        """Adds the argument to allow access to the data file

        Args:
            parser (ArgumentParser): The parser with previously added arguments
        """
        parser.add_argument(
            "data_file",
            metavar="data_file",
            type=str,
            help="The file containing a JSON encoded batch",
        )
        parser.set_defaults(func=LocalWorker.main)

    @staticmethod
    def main(args: Namespace) -> None:
        """Runs the local version of the Worker

        Args:
            args (Namespace): The arguments required to run the Worker
        """
        with open(args.data_file, "r", encoding="utf8") as data_file:
            data = json.loads(data_file.read())
            schema = AutoTransformSchema.from_bundle(data["schema"])
            encoded_batches = data["batches"]
            encoded_file_data = data["file_data"]
            for path, file_data in encoded_file_data:
                data_store.add_object(path, FileDataObject(file_data))
            batches: List[Batch] = [
                {
                    "files": [CachedFile(path) for path in batch["files"]],
                    "metadata": batch["metadata"],
                }
                for batch in encoded_batches
            ]
            for batch in batches:
                schema.execute_batch(batch)
