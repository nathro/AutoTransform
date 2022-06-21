# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the GithubRunner."""

from __future__ import annotations

import json
from typing import ClassVar

from autotransform.change.base import Change
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.remoterun import RemoteRunEvent
from autotransform.event.update import RemoteUpdateEvent
from autotransform.repo.github import GithubRepo
from autotransform.runner.base import Runner, RunnerName
from autotransform.schema.schema import AutoTransformSchema
from autotransform.util.github import GithubUtils


class GithubRunner(Runner):
    """A Runner component that is used to trigger Github workflows. See
    examples/workflows/autotransform.run.yml.

    Attributes:
        run_workflow (str): The name of the workflow to use for running a Schema.
        update_workflow (str): The name of the workflow to use for updating a Change.
        name (ClassVar[RunnerName]): The name of the component.
    """

    run_workflow: str
    update_workflow: str

    name: ClassVar[RunnerName] = RunnerName.GITHUB

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

        # Dispatch a Workflow run
        workflow_url = GithubUtils.get(repo.full_github_name).create_workflow_dispatch(
            self.run_workflow,
            repo.base_branch,
            {"schema": json.dumps(schema.bundle())},
        )
        assert workflow_url is not None, "Failed to dispatch workflow request"
        event_handler.handle(DebugEvent({"message": "Successfully dispatched workflow run"}))
        if workflow_url == "":
            event_handler.handle(DebugEvent({"message": "No guess for workflow run URL."}))
            return
        event_handler.handle(
            DebugEvent(
                {
                    "message": "Because Github REST API does not provide IDs in response, "
                    + "taking best guess at workflow URL"
                }
            )
        )
        event_handler.handle(
            RemoteRunEvent({"schema_name": schema.config.schema_name, "ref": workflow_url})
        )

    def update(self, change: Change) -> None:
        """Triggers an update of the Change by submitting a workflow run to the
        Github repo in the Schema associated with the change.

        Args:
            change (Change): The Change to update.
        """

        event_handler = EventHandler.get()
        schema = change.get_schema()
        repo = schema.repo

        # May add support for cross-repo usage but enforce that the workflow being invoked exists
        # in the target repo for now
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only update changes using schemas that have Github repos"

        # Dispatch a Workflow run
        workflow_url = GithubUtils.get(repo.full_github_name).create_workflow_dispatch(
            self.update_workflow,
            repo.base_branch,
            {"change": json.dumps(change.bundle())},
        )
        assert workflow_url is not None, "Failed to dispatch workflow request"
        event_handler.handle(DebugEvent({"message": "Successfully dispatched workflow run"}))
        if workflow_url == "":
            event_handler.handle(DebugEvent({"message": "No guess for workflow run URL."}))
            return
        event_handler.handle(
            DebugEvent(
                {
                    "message": "Because Github REST API does not provide IDs in response, "
                    + "taking best guess at workflow URL"
                }
            )
        )
        event_handler.handle(RemoteUpdateEvent({"change": change, "ref": workflow_url}))
