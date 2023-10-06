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
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.runner import RunnerFailedEvent, RunnerRunEvent, RunnerUpdateEvent
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

        event_handler = EventHandler.get()

        # Set up inputs
        workflow_inputs = {"schema": schema.config.schema_name}
        if schema.config.max_submissions:
            workflow_inputs["max_submissions"] = str(schema.config.max_submissions)
        shard_filter = [filt for filt in schema.filters if isinstance(filt, ShardFilter)]
        if shard_filter:
            workflow_inputs["filter"] = json.dumps(shard_filter[0].bundle())

        # Dispatch a Workflow run
        workflow_url = self._create_workflow_dispatch(self.run_workflow, schema, workflow_inputs)
        if workflow_url is not None:
            event_handler.handle(
                RunnerRunEvent(
                    {
                        "schema_name": schema.config.schema_name,
                        "ref": workflow_url if workflow_url else None,
                        "runner": self,
                    }
                )
            )

    def update(self, change: Change) -> None:
        """Triggers an update of the Change by submitting a workflow run to the
        Github repo in the Schema associated with the change.

        Args:
            change (Change): The Change to update.
        """

        event_handler = EventHandler.get()

        # Dispatch a Workflow run
        workflow_url = self._create_workflow_dispatch(
            self.update_workflow, change.get_schema(), {"change": json.dumps(change.bundle())}
        )
        if workflow_url is not None:
            event_handler.handle(
                RunnerUpdateEvent(
                    {
                        "change": change,
                        "ref": workflow_url if workflow_url else None,
                        "runner": self,
                    }
                )
            )

    def _create_workflow_dispatch(
        self, workflow_name: str, schema: AutoTransformSchema, inputs: Dict[str, Any]
    ) -> Optional[str]:
        """Creates a workflow dispatch

        Args:
            workflow_name (str): The name of the workflow to dispatch.
            schema (AutoTransformSchema): The Schema that is involved with the dispatch.
            inputs (Dict[str, Any]): The inputs for the dispatch.

        Returns:
            Optional[str]: The URL for the workflow run. None is returned if no dispatch happened.
        """

        event_handler = EventHandler.get()
        repo = get_config().repo_override or schema.repo
        repo_name = None
        repo_ref = None
        if isinstance(repo, GithubRepo):
            repo_name = repo.full_github_name
            repo_ref = repo.base_branch

        if self.repo_name is not None:
            repo_name = self.repo_name
        if self.repo_ref is not None:
            repo_ref = self.repo_ref

        if repo_name is None:
            event_handler.handle(
                RunnerFailedEvent({"message": "No repo name provided", "runner": self})
            )
            return None
        if repo_ref is None:
            event_handler.handle(
                RunnerFailedEvent({"message": "No repo ref provided", "runner": self})
            )
            return None

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
        if workflow_url is None:
            event_handler.handle(
                RunnerFailedEvent({"message": "Failed to dispatch Workflow", "runner": self})
            )
        return workflow_url
