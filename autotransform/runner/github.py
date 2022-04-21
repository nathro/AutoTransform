# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""A GithubberRunner component, which is used to trigger a workflow on Github which
runs a schema."""

from __future__ import annotations

import time
from typing import Any, Mapping, TypedDict, Union

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.repo.github import GithubRepo
from autotransform.runner.base import Runner
from autotransform.runner.type import RunnerType
from autotransform.schema.schema import AutoTransformSchema


class GithubRunnerParams(TypedDict):
    """The params required for a GithubRunner instance."""

    workflow: Union[str, int]


class GithubRunner(Runner[GithubRunnerParams]):
    """A Runner component that is used to trigger Github workflows. See
    data/workflows/autotransform_runner.yml.

    Attributes:
        _params (GithubRunnerParams): The paramaters that control operation of the Runner.
    """

    _params: GithubRunnerParams

    @staticmethod
    def get_type() -> RunnerType:
        """Used to map Runner components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RunnerType: The unique type associated with this Runner.
        """

        return RunnerType.GITHUB

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema by submitting a workflow run to the
        Github repo in the Schema.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        event_handler = EventHandler.get()
        repo = schema.repo

        # May add support for cross-repo usage but enforce that the workflow being invoked exists
        # in the target repo for now
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only run using schemas that have Github repos"

        # Get the Workflow object
        github_repo = repo.get_github_repo()
        workflow = github_repo.get_workflow(self._params["workflow"])
        event_handler.handle(DebugEvent({"message": f"Workflow found: {workflow.name}"}))

        # Dispatch a Workflow run
        dispatch_success = workflow.create_dispatch(
            repo.get_params()["base_branch_name"],
            {"schema": schema.to_json()},
        )
        assert dispatch_success, "Failed to dispatch workflow request"
        event_handler.handle(DebugEvent({"message": "Successfully dispatched workflow run"}))

        # We wait a bit to make sure Github's API is updated before printing a best guess of the
        # Workflow run's URL
        time.sleep(5)
        event_handler.handle(DebugEvent({"message": "Checking for workflow run URL"}))
        workflow_runs = workflow.get_runs()
        event_handler.handle(
            DebugEvent(
                {
                    "message": "Because Github REST API does not provide IDs in response, "
                    + "taking best guess at workflow URL"
                }
            )
        )
        event_handler.handle(
            DebugEvent({"message": f"Best Guess URL: {workflow_runs[0].html_url}"})
        )

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GithubRunner:
        """Produces an instance of the component from decoded params. Implementations should
        assert that the data provided matches expected types and is valid.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle.

        Returns:
            GithubRunner: An instance of the GithubRunner.
        """

        workflow = data["workflow"]
        assert isinstance(workflow, (int, str))
        return GithubRunner({"workflow": workflow})
