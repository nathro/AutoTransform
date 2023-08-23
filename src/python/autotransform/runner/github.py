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
from typing import Any, ClassVar, Dict, Optional

from autotransform.change.base import Change
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.remoterun import RemoteRunEvent
from autotransform.event.verbose import VerboseEvent
from autotransform.filter.shard import ShardFilter
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
        repo_name (optional, Optional[str]): The name of the Github repo to trigger actions from.
            If not provided, the repo of the Schema will be used. Defaults to None.
        repo_ref (optional, Optional[str]): The ref of the Github repo to trigger actions from.
            If not provided, the base branch of the Schema's repo will be used. Defaults to None.
        target_repo_name (optional, Optional[str]): The name of the Github repo to checkout.
            If not provided, the workflow is expected to define the repo on it's own.
            Defaults to None.
        target_repo_ref (optional, Optional[str]): The ref of the Github repo to checkout.
            If not provided, the workflow is expected to define the repo on it's own.
            Defaults to None.
        name (ClassVar[RunnerName]): The name of the component.
    """

    run_workflow: str
    update_workflow: str

    repo_name: Optional[str] = None
    repo_ref: Optional[str] = None
    target_repo_name: Optional[str] = None
    target_repo_ref: Optional[str] = None

    name: ClassVar[RunnerName] = RunnerName.GITHUB

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema by submitting a workflow run to the
        Github repo in the Schema.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        # Set up inputs
        workflow_inputs = self._setup_workflow_inputs(schema)

        # Dispatch a Workflow run
        self._dispatch_workflow_run(self.run_workflow, schema, workflow_inputs)

    def update(self, change: Change) -> None:
        """Triggers an update of the Change by submitting a workflow run to the
        Github repo in the Schema associated with the change.

        Args:
            change (Change): The Change to update.
        """

        # Dispatch a Workflow run
        self._dispatch_workflow_run(
            self.update_workflow, change.get_schema(), {"change": json.dumps(change.bundle())}
        )

    def _setup_workflow_inputs(self, schema: AutoTransformSchema) -> Dict[str, Any]:
        """Set up workflow inputs

        Args:
            schema (AutoTransformSchema): The schema that will be run.

        Returns:
            Dict[str, Any]: The inputs for the dispatch.
        """

        workflow_inputs = {"schema": schema.config.schema_name}
        if schema.config.max_submissions:
            workflow_inputs["max_submissions"] = str(schema.config.max_submissions)
        shard_filter = [filt for filt in schema.filters if isinstance(filt, ShardFilter)]
        if shard_filter:
            workflow_inputs["filter"] = json.dumps(shard_filter[0].bundle())
        return workflow_inputs

    def _dispatch_workflow_run(
        self, workflow_name: str, schema: AutoTransformSchema, inputs: Dict[str, Any]
    ) -> None:
        """Dispatch a Workflow run

        Args:
            workflow_name (str): The name of the workflow to dispatch.
            schema (AutoTransformSchema): The Schema that is involved with the dispatch.
            inputs (Dict[str, Any]): The inputs for the dispatch.
        """

        workflow_url = self._create_workflow_dispatch(workflow_name, schema, inputs)
        assert workflow_url is not None, "Failed to dispatch workflow request"

        EventHandler.get().handle(VerboseEvent({"message": "Successfully dispatched workflow run"}))
        if workflow_url == "":
            EventHandler.get().handle(DebugEvent({"message": "No guess for workflow run URL."}))
            return
        EventHandler.get().handle(
            DebugEvent(
                {
                    "message": "Because Github REST API does not provide IDs in response, "
                    + "taking best guess at workflow URL"
                }
            )
        )
        EventHandler.get().handle(
            RemoteRunEvent({"schema_name": schema.config.schema_name, "ref": workflow_url})
        )

    def _create_workflow_dispatch(
        self, workflow_name: str, schema: AutoTransformSchema, inputs: Dict[str, Any]
    ) -> str:
        """Creates a workflow dispatch

        Args:
            workflow_name (str): The name of the workflow to dispatch.
            schema (AutoTransformSchema): The Schema that is involved with the dispatch.
            inputs (Dict[str, Any]): The inputs for the dispatch.

        Returns:
            str: The URL for the workflow run.
        """

        repo_name = self.repo_name or self._get_repo_name(schema)
        repo_ref = self.repo_ref or self._get_repo_ref(schema)

        # Allow controlling the target repo with the Runner
        if self.target_repo_name is not None:
            inputs["target_repo_name"] = self.target_repo_name
        if self.target_repo_ref is not None:
            inputs["target_repo_ref"] = self.target_repo_ref

        # Dispatch a Workflow run
        workflow_url = GithubUtils.get(repo_name).create_workflow_dispatch(
            workflow_name,
            repo_ref,
            inputs,
        )
        assert workflow_url is not None, "Failed to dispatch workflow request"
        return workflow_url

    def _get_repo_name(self, schema: AutoTransformSchema) -> str:
        """Get the repo name

        Args:
            schema (AutoTransformSchema): The Schema that is involved with the dispatch.

        Returns:
            str: The repo name.
        """

        repo = schema.repo
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only run using schemas that have Github repos"
        return repo.full_github_name

    def _get_repo_ref(self, schema: AutoTransformSchema) -> str:
        """Get the repo ref

        Args:
            schema (AutoTransformSchema): The Schema that is involved with the dispatch.

        Returns:
            str: The repo ref.
        """

        repo = schema.repo
        assert isinstance(
            repo, GithubRepo
        ), "GithubRunner can only run using schemas that have Github repos"
        return repo.base_branch
