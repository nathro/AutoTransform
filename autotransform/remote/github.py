# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""The base class and associated classes for Remote components."""

from __future__ import annotations

import time
from typing import Any, Mapping, TypedDict, TypeVar

from autotransform.remote.base import Remote
from autotransform.remote.type import RemoteType
from autotransform.repo.github import GithubRepo
from autotransform.schema.schema import AutoTransformSchema
from autotransform.worker.type import WorkerType

TParams = TypeVar("TParams", bound=Mapping[str, Any])


class GithubRemoteParams(TypedDict):
    """The params required for a GithubRemote instance"""

    workflow_id: int
    worker: WorkerType


class GithubRemote(Remote[GithubRemoteParams]):
    """A remote component that is used to trigger Github workflows. See the run.yml workflow
    file in github.com/nathro/autotransform for what this workflow should look like.

    Attributes:
        params (GithubRemoteParams): The paramaters that control operation of the Remote.
    """

    params: GithubRemoteParams

    def get_type(self) -> RemoteType:
        """Used to map Remote components 1:1 with an enum, allowing construction from JSON.

        Returns:
            RemoteType: The unique type associated with this Remote
        """
        return RemoteType.GITHUB

    def run(self, schema: AutoTransformSchema) -> str:
        """Triggers a remote run of the schema.

        Args:
            schema (AutoTransformSchema): The schema to schedule a remote run for
        Returns:
            str: A string representation of the remote run that can be used to monitor status
        """
        repo = schema.repo
        # May add support for cross-repo usage but enforce that the workflow being invoked exists
        # in the target repo for now
        assert isinstance(
            repo, GithubRepo
        ), "Github remote can only run using schemas that have Github repos"
        github_repo = repo.github_repo
        workflow = github_repo.get_workflow(self.params["workflow_id"])
        dispatch_success = workflow.create_dispatch(
            repo.params["base_branch_name"],
            {"schema": schema.to_json(), "worker": self.params["worker"]},
        )
        assert dispatch_success, "Failed to dispatch workflow request"
        # We wait a bit to make sure Github's API is updated
        time.sleep(15)
        workflow_runs = workflow.get_runs(
            event="workflow_dispatch",
            branch=repo.params["base_branch_name"],
            actor=repo.get_github_object().get_user().login,
        )
        print("Github does not provide URLs on dispatch, taking best guess")
        return workflow_runs[0].html_url

    @staticmethod
    def from_data(data: Mapping[str, Any]) -> GithubRemote:
        """Produces an instance of the component from decoded params.

        Args:
            data (Mapping[str, Any]): The JSON decoded params from an encoded bundle

        Returns:
            GithubRemote: An instance of the GithubRemote
        """
        workflow_id = data["workflow_id"]
        assert isinstance(workflow_id, int)
        worker = data["worker"]
        assert isinstance(worker, str)
        return GithubRemote({"workflow_id": workflow_id, "worker": worker})  # type: ignore
