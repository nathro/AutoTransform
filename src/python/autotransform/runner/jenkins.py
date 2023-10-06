# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation for the JenkinsRunner."""

from __future__ import annotations

import json
import os
from typing import Any, ClassVar, Dict

import requests
from autotransform.change.base import FACTORY as change_factory
from autotransform.change.base import Change
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.runner import RunnerFailedEvent, RunnerRunEvent, RunnerUpdateEvent
from autotransform.filter.shard import ShardFilter
from autotransform.runner.base import Runner, RunnerName
from autotransform.schema.schema import AutoTransformSchema


class JenkinsAPIRunner(Runner):
    """A Runner component that uses Jenkins API requests for remote runs.

    Attributes:
        job_name (str): The name of the Jenkins job.
        name (ClassVar[RunnerName]): The name of the component.
    """

    job_name: str

    name: ClassVar[RunnerName] = RunnerName.JENKINS_API

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema using a Jenkins API request.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        job_params = {"COMMAND": "run", "SCHEMA_NAME": schema.config.schema_name}
        if schema.config.max_submissions:
            job_params["MAX_SUBMISSIONS"] = str(schema.config.max_submissions)
        shard_filter = [filt for filt in schema.filters if isinstance(filt, ShardFilter)]
        if shard_filter:
            job_params["FILTER"] = json.dumps(shard_filter[0].bundle())

        self._run_jenkins_job(self.job_name, job_params)

    def update(self, change: Change) -> None:
        """Triggers an update of the Change using a Jenkins API request.

        Args:
            change (Change): The Change to update.
        """

        self._run_jenkins_job(
            self.job_name, {"COMMAND": "update", "CHANGE": json.dumps(change.bundle())}
        )

    def _run_jenkins_job(self, job_name: str, params: Dict[str, Any]) -> None:
        """Runs a Jenkins job to handle a run/update of AutoTransform.

        Args:
            job_name (str): The name of the Jenkins job to trigger.
            params (Dict[str, Any]): The params to pass to the Jenkins job.
        """

        config = get_config()
        event_handler = EventHandler.get()
        jenkins_user = config.jenkins_user
        jenkins_token = config.jenkins_token
        if jenkins_user is None:
            event_handler.handle(
                RunnerFailedEvent({"message": "No Jenkins user provided", "runner": self})
            )
            return
        if jenkins_token is None:
            event_handler.handle(
                RunnerFailedEvent({"message": "No Jenkins token provided", "runner": self})
            )
            return

        auth = (jenkins_user, jenkins_token)
        crumb_data = requests.get(
            f"{config.jenkins_base_url}/crumbIssuer/api/json",
            auth=auth,
            headers={"content-type": "application/json"},
            timeout=120,
        )
        if str(crumb_data.status_code) == "200":
            data = requests.get(
                f"{config.jenkins_base_url}/job/{job_name}/buildWithParameters",
                auth=auth,
                params=params,
                headers={
                    "content-type": "application/json",
                    "Jenkins-Crumb": crumb_data.json()["crumb"],
                },
                timeout=120,
            )

            if str(data.status_code) == "201":
                if params["COMMAND"] == "run":
                    event_handler.handle(
                        RunnerRunEvent(
                            {"schema_name": params["SCHEMA_NAME"], "ref": None, "runner": self}
                        )
                    )
                else:
                    event_handler.handle(
                        RunnerUpdateEvent(
                            {
                                "change": change_factory.get_instance(json.loads(params["CHANGE"])),
                                "ref": None,
                                "runner": self,
                            }
                        )
                    )
            else:
                event_handler.handle(
                    RunnerFailedEvent(
                        {"message": f"Jenkins job failed: {data.status_code}", "runner": self}
                    )
                )

        else:
            event_handler.handle(
                RunnerFailedEvent(
                    {
                        "message": f"Couldn't fetch Jenkins-Crumb: {crumb_data.status_code}",
                        "runner": self,
                    }
                )
            )


class JenkinsFileRunner(Runner):
    """A Runner component that creates files to trigger Jenkins jobs
    using https://plugins.jenkins.io/parameterized-trigger/.

    Attributes:
        name (ClassVar[RunnerName]): The name of the component.
        num_files (ClassVar[int]): The number of files created by the runner.
    """

    name: ClassVar[RunnerName] = RunnerName.JENKINS_FILE
    num_files: ClassVar[int] = 0

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema by creating a file with the appropriate content.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        job_params = {"COMMAND": "run", "SCHEMA_NAME": schema.config.schema_name}
        if schema.config.max_submissions:
            job_params["MAX_SUBMISSIONS"] = str(schema.config.max_submissions)
        shard_filter = [filt for filt in schema.filters if isinstance(filt, ShardFilter)]
        if shard_filter:
            job_params["FILTER"] = json.dumps(shard_filter[0].bundle())

        self._create_file(job_params)

    def update(self, change: Change) -> None:
        """Triggers an update of the Change using a Jenkins API request.

        Args:
            change (Change): The Change to update.
        """

        self._create_file({"COMMAND": "update", "CHANGE": json.dumps(change.bundle())})

    def _create_file(self, props: Dict[str, str]) -> None:
        """Creates the file for the Jenkins job.

        Args:
            props (Dict[str, str]): The props to add to the job.
        """

        JenkinsFileRunner.num_files += 1

        cwd = os.getcwd().replace("\\", "/")
        file_path = f"{cwd}/autotransform/jenkins/job_{JenkinsFileRunner.num_files}.txt"

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = "\n".join([f"{k}={v}" for k, v in props.items()])
        with open(file_path, "w+", encoding="UTF-8") as job_file:
            job_file.write(content)
            job_file.flush()
