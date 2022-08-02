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
from typing import Any, Dict, List, Optional

from autotransform.change.base import ChangeState
from autotransform.event.action import ManageActionEvent
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.base import FACTORY as repo_factory
from autotransform.repo.base import Repo, RepoName
from autotransform.repo.git import GitRepo
from autotransform.repo.github import GithubRepo
from autotransform.runner.base import FACTORY as runner_factory
from autotransform.runner.base import Runner
from autotransform.step.action.source import AbandonAction, MergeAction, UpdateAction
from autotransform.step.base import FACTORY as step_factory
from autotransform.step.base import Step
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.state import ChangeStateCondition
from autotransform.step.condition.updated import UpdatedAgoCondition
from autotransform.step.conditional import ConditionalStep
from autotransform.util.component import ComponentModel
from autotransform.util.console import (
    choose_options_from_list,
    choose_yes_or_no,
    get_str,
    input_int,
)


class Manager(ComponentModel):
    """The information and functionality required for managing outstanding changes.

    Attributes:
        repo (Repo): The repo to get outstanding changes for.
        runner (Runner): The runner to use when updating outstanding changes.
        steps (List[Step]): The steps to take for outstanding changes.
    """

    repo: Repo
    runner: Runner
    steps: List[Step]

    def run(self) -> None:
        """Runs the management."""

        changes = self.repo.get_outstanding_changes()
        for change in changes:
            EventHandler.get().handle(DebugEvent({"message": f"Checking steps for {str(change)}"}))
            for step in self.steps:
                EventHandler.get().handle(DebugEvent({"message": f"Checking step {str(step)}"}))
                actions = step.get_actions(change)
                for action in actions:
                    EventHandler.get().handle(
                        ManageActionEvent({"action": action, "change": change, "step": step})
                    )
                    change.take_action(action, self.runner)

                if actions and not step.continue_management(change):
                    EventHandler.get().handle(
                        DebugEvent({"message": f"Steps ended for change {str(change)}"})
                    )
                    break

    def write(self, file_path: str) -> None:
        """Writes the management information to a file as JSON.

        Args:
            file_path (str): The file to write to.
        """

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w+", encoding="UTF-8") as manager_file:
            manager_file.write(json.dumps(self.bundle(), indent=4))
            manager_file.flush()

    @staticmethod
    def read(file_path: str) -> Manager:
        """Reads management info from a JSON encoded file.

        Args:
            file_path (str): The path where the JSON for the management info is located.

        Returns:
            Manager: The Manager from the file.
        """

        with open(file_path, "r", encoding="UTF-8") as manager_file:
            manager_json = manager_file.read()
        EventHandler.get().handle(
            DebugEvent({"message": f"Manager: ({file_path})\n{manager_json}"})
        )
        return Manager.from_json(manager_json)

    @staticmethod
    def from_json(manager_json: str) -> Manager:
        """Builds a Manager from JSON encoded values.

        Args:
            manager_json (str): The JSON encoded Manager.

        Returns:
            Manager: The Manager from the JSON.
        """

        return Manager.from_data(json.loads(manager_json))

    @staticmethod
    def from_data(data: Dict[str, Any]) -> Manager:
        """Produces an instance of the Manager from decoded data.

        Args:
            data (Mapping[str, Any]): The JSON decoded data.

        Returns:
            Manager: An instance of the Manager.
        """

        return Manager(
            repo=repo_factory.get_instance(data["repo"]),
            runner=runner_factory.get_instance(data["runner"]),
            steps=[step_factory.get_instance(step) for step in data.get("steps", [])],
        )

    # pylint: disable=too-many-branches
    @staticmethod
    def init_from_console(
        repo_name: Optional[RepoName] = None,
        prev_runner: Optional[Runner] = None,
        simple: bool = False,
    ) -> Manager:
        """Gets a Manager using console inputs.

        Args:
            repo_name (Optional[RepoName], optional): The name of the repo to use. Defaults to None.
            prev_runner (Optional[Runner], optional): A previously input runner. Defaults to None.
            simple (bool, optional): Whether to use simple options for setting up the manager.
                Defaults to False.

        Returns:
            Manager: The input Manager.
        """

        if repo_name == RepoName.GITHUB:
            base_branch = get_str(
                "Enter the name of the base branch for the repo(i.e. main, master): "
            )
            github_name = get_str("Enter the fully qualified name of the github repo(owner/repo): ")
            repo: Repo = GithubRepo(base_branch=base_branch, full_github_name=github_name)
        elif repo_name == RepoName.GIT:
            base_branch = get_str(
                "Enter the name of the base branch for the repo(i.e. main, master): "
            )
            repo = GitRepo(base_branch=base_branch)
        else:
            input_repo = repo_factory.from_console("repo", allow_none=False)
            assert input_repo is not None
            repo = input_repo

        # Get the runner
        args: Dict[str, Any] = {"simple": simple, "allow_none": False}
        if prev_runner is not None:
            args["previous_value"] = prev_runner
        runner = runner_factory.from_console("manager runner", **args)
        assert runner is not None

        # Merge approved changes
        steps: List[Step] = []
        if simple or choose_yes_or_no("Automatically merge approved changes?"):
            steps.append(
                ConditionalStep(
                    condition=ChangeStateCondition(
                        comparison=ComparisonType.EQUAL, value=ChangeState.APPROVED
                    ),
                    actions=[MergeAction()],
                )
            )

        # Abandon rejected changes
        if simple or choose_yes_or_no("Automatically abandon rejected changes?"):
            steps.append(
                ConditionalStep(
                    condition=ChangeStateCondition(
                        comparison=ComparisonType.EQUAL, value=ChangeState.CHANGES_REQUESTED
                    ),
                    actions=[AbandonAction()],
                )
            )

        # Update stale changes
        if simple or choose_yes_or_no("Automatically update stale changes?"):
            if simple:
                days_stale = 7
            else:
                days_stale = input_int("Enter number of days until stale", min_val=1)
            steps.append(
                ConditionalStep(
                    condition=UpdatedAgoCondition(
                        comparison=ComparisonType.GREATER_THAN_OR_EQUAL,
                        value=days_stale * 24 * 60 * 60,
                    ),
                    actions=[UpdateAction()],
                )
            )

        return Manager(repo=repo, runner=runner, steps=steps)

    @staticmethod
    def from_console(prev_manager: Optional[Manager] = None) -> Manager:
        """Gets a Manager using console inputs.

        Args:
            prev_manager (Optional[Manager], optional): A previously input Manager.
                Defaults to None.

        Returns:
            Manager: The input Manager.
        """

        args: Dict[str, Any] = {"allow_none": False}
        if prev_manager is not None:
            args["previous_value"] = prev_manager.repo
        repo = repo_factory.from_console("repo", **args)
        assert repo is not None

        args = {"allow_none": False}
        if prev_manager is not None:
            args["previous_value"] = prev_manager.runner
        runner = runner_factory.from_console("runner", **args)
        assert runner is not None

        if prev_manager is not None and bool(prev_manager.steps):
            steps = choose_options_from_list(
                "Choose steps to keep",
                [(step, f"{step!r}") for step in prev_manager.steps],
                min_choices=0,
                max_choices=len(prev_manager.steps),
            )
        else:
            steps = []
        while choose_yes_or_no("Would you like to add another step?"):
            step = step_factory.from_console("step", allow_none=False)
            assert step is not None
            steps.append(step)

        return Manager(repo=repo, runner=runner, steps=steps)
