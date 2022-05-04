# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A GithubberRunner component, which is used to trigger a workflow on Github which
runs a schema."""

from __future__ import annotations

import json
import time
from typing import Any, Mapping, TypedDict, Union

from autotransform.change.base import Change
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.remoterun import RemoteRunEvent
from autotransform.event.update import RemoteUpdateEvent
from autotransform.repo.github import GithubRepo
from autotransform.runner.base import Runner
from autotransform.runner.type import RunnerType
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.github import GithubUtils


class GithubRunnerParams(TypedDict):
    """The params required for a GithubRunner instance."""

    run_workflow: Union[str, int]
    update_workflow: Union[str, int]


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
        repo = schema.get_repo()

        # May add support for cross-repo usage but enforce that the workflow being invoked exists
        # in the target repo for now
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only run using schemas that have Github repos"

        # Get the Workflow object
        repo_name = str(repo.get_params().get("full_github_name"))
        github_repo = GithubUtils.get_github_repo(repo_name)
        workflow = github_repo.get_workflow(self._params["run_workflow"])
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
            RemoteRunEvent(
                {"schema_name": schema.get_config().get_name(), "ref": workflow_runs[0].html_url}
            )
        )

    def update(self, change: Change) -> None:
        """Triggers an update of the Change by submitting a workflow run to the
        Github repo in the Schema associated with the change.

        Args:
            change (Change): The Change to update.
        """

        event_handler = EventHandler.get()
        schema = change.get_schema()
        repo = schema.get_repo()

        # May add support for cross-repo usage but enforce that the workflow being invoked exists
        # in the target repo for now
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only update changes using schemas that have Github repos"

        # Get the Workflow object
        repo_name = str(repo.get_params().get("full_github_name"))
        github_repo = GithubUtils.get_github_repo(repo_name)
        workflow = github_repo.get_workflow(self._params["update_workflow"])
        event_handler.handle(DebugEvent({"message": f"Workflow found: {workflow.name}"}))

        # Dispatch an Update Workflow
        dispatch_success = workflow.create_dispatch(
            repo.get_params()["base_branch_name"],
            {"change": json.dumps(change.bundle())},
        )
        assert dispatch_success, "Failed to dispatch workflow request"
        event_handler.handle(DebugEvent({"message": "Successfully dispatched update workflow"}))

        # We wait a bit to make sure Github's API is updated before printing a best guess of the
        # Update Workflow's URL
        time.sleep(5)
        event_handler.handle(DebugEvent({"message": "Checking for update workflow URL"}))
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
            RemoteUpdateEvent({"change": change, "ref": workflow_runs[0].html_url})
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

        run_workflow = data["run_workflow"]
        assert isinstance(run_workflow, (int, str))
        update_workflow = data["update_workflow"]
        assert isinstance(update_workflow, (int, str))
        return GithubRunner({"run_workflow": run_workflow, "update_workflow": update_workflow})
