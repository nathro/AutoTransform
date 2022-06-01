# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides utility methods for interacting with the management of outstanding Changes."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.base import FACTORY as repo_factory
from autotransform.repo.base import Repo
from autotransform.runner.base import FACTORY as runner_factory
from autotransform.runner.base import Runner
from autotransform.step.base import FACTORY as step_factory
from autotransform.step.base import Step


@dataclass(kw_only=True)
class Manager:
    """The information and functionality required for managing outstanding changes.

    Attributes:
        repo (Repo): The repo to get outstanding changes for.
        runner (Runner): The runner to use when updating outstanding changes.
        steps (List[Step]): The steps to take for outstanding changes.
    """

    repo: Repo
    runner: Runner
    steps: List[Step]

    def write(self, file_path: str) -> None:
        """Writes the management information to a file as JSON.

        Args:
            file_path (str): The file to write to.
        """

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as schedule_file:
            schedule_file.write(json.dumps(self.bundle(), indent=4))
            schedule_file.flush()

    def bundle(self) -> Dict[str, Any]:
        """Generates a JSON encodable bundle.

        Returns:
            Dict[str, Any]: The encodable bundle.
        """

        return {
            "repo": self.repo.bundle(),
            "runner": self.runner.bundle(),
            "steps": [step.bundle() for step in self.steps],
        }

    @staticmethod
    def read(file_path: str) -> Manager:
        """Reads management info from a JSON encoded file.

        Args:
            file_path (str): The path where the JSON for the management info is located.

        Returns:
            Manager: The Schedule from the file.
        """

        with open(file_path, "r", encoding="UTF-8") as manager_file:
            manager_json = manager_file.read()
        EventHandler.get().handle(
            DebugEvent({"message": f"Manager: ({file_path})\n{manager_json}"})
        )
        return Manager.from_json(manager_json)

    @staticmethod
    def from_json(manager_json: str) -> Manager:
        """Builds a schedule from JSON encoded values.

        Args:
            manager_json (str): The JSON encoded Manager.

        Returns:
            Manager: The Manager from the JSON.
        """

        return Manager.from_data(json.loads(manager_json))

    @staticmethod
    def from_data(data: Dict[str, Any]) -> Manager:
        """Produces an instance of the Schedule from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.
            start_time (int): The time that the schedule is starting to run on.

        Returns:
            Schedule: An instance of the Schedule.
        """

        return Manager(
            repo=repo_factory.get_instance(data["repo"]),
            runner=runner_factory.get_instance(data["runner"]),
            steps=[step_factory.get_instance(step) for step in data.get("steps", [])],
        )
