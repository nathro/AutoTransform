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
from typing import Any, ClassVar, Dict, Optional, Tuple

import requests
from autotransform.change.base import Change
from autotransform.config import get_config
from autotransform.event.handler import EventHandler
from autotransform.event.verbose import VerboseEvent
from autotransform.event.warning import WarningEvent
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

    @staticmethod
    def _fetch_jenkins_crumb(
        base_url: str, auth: Tuple[str, str]
    ) -> Optional[str]:
        """Fetches the Jenkins crumb which is required for CSRF protection.

        Args:
            base_url (str): The base URL of the Jenkins server.
            auth (Tuple[str, str]): The username and token for Jenkins
            authentication.

        Returns:
            Optional[str]: The Jenkins crumb if successful, None otherwise.
        """
        response = requests.get(
            f"{base_url}/crumbIssuer/api/json",
            auth=auth,
            headers={"content-type": "application/json"},
            timeout=120,
        )
        if response.status_code == 200:
            return response.json().get("crumb")
        return None

    @staticmethod
    def _trigger_jenkins_job(
        base_url: str,
        job_name: str,
        auth: Tuple[str, str],
        params: Dict[str, Any],
        crumb: str,
    ) -> requests.Response:
        """Triggers a Jenkins job.

        Args:
            base_url (str): The base URL of the Jenkins server.
            job_name (str): The name of the Jenkins job to trigger.
            auth (Tuple[str, str]): The username and token for Jenkins
              authentication.
            params (Dict[str, Any]): The params to pass to the Jenkins job.
            crumb (str): The Jenkins crumb for CSRF protection.

        Returns:
            requests.Response: The response from the Jenkins server.
        """
        return requests.get(
            f"{base_url}/job/{job_name}/buildWithParameters",
            auth=auth,
            params=params,
            headers={
                "content-type": "application/json",
                "Jenkins-Crumb": crumb,
            },
            timeout=120,
        )

    def run(self, schema: AutoTransformSchema) -> None:
        """Triggers a full run of a Schema using a Jenkins API request.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        job_params = {
            "COMMAND": "run",
            "SCHEMA_NAME": schema.config.schema_name,
        }
        if schema.config.max_submissions:
            job_params["MAX_SUBMISSIONS"] = str(schema.config.max_submissions)
        shard_filter = [
            filt for filt in schema.filters if isinstance(filt, ShardFilter)
        ]
        if shard_filter:
            job_params["FILTER"] = json.dumps(shard_filter[0].bundle())

        self._run_jenkins_job(self.job_name, job_params)

    def update(self, change: Change) -> None:
        """Triggers an update of the Change using a Jenkins API request.

        Args:
            change (Change): The Change to update.
        """

        self._run_jenkins_job(
            self.job_name,
            {
                "COMMAND": "update",
                "CHANGE": json.dumps(change.bundle()),
            },
        )

    @staticmethod
    def _run_jenkins_job(job_name: str, params: Dict[str, Any]) -> None:
        """Runs a Jenkins job to handle a run/update of AutoTransform.

        Args:
            job_name (str): The name of the Jenkins job to trigger.
            params (Dict[str, Any]): The params to pass to the Jenkins job.
        """

        config = get_config()
        event_handler = EventHandler.get()
        jenkins_user = config.jenkins_user
        jenkins_token = config.jenkins_token
        if jenkins_user is None or jenkins_token is None:
            event_handler.handle(
                WarningEvent(
                    {
                        "message": "User and token must \
                          be provided to use Jenkins"
                    }
                )
            )
            return

        try:
            auth = (jenkins_user, jenkins_token)
            if config.jenkins_base_url is None:
                event_handler.handle(
                    WarningEvent(
                        {"message": "Jenkins base URL is not configured"}
                    )
                )
                return
            crumb = JenkinsAPIRunner._fetch_jenkins_crumb(
                config.jenkins_base_url, auth
            )
            if crumb is None:
                event_handler.handle(
                    WarningEvent({"message": "Couldn't fetch Jenkins-Crumb"})
                )
                return
            response = JenkinsAPIRunner._trigger_jenkins_job(
                config.jenkins_base_url,
                job_name,
                auth,
                params,
                crumb,
            )
            if response.status_code == 201:
                event_handler.handle(
                    VerboseEvent({"message": "Jenkins job is triggered"})
                )
            else:
                event_handler.handle(
                    WarningEvent(
                        {
                            "message": f"Failed to trigger the Jenkins job.\
                            Response code: {response.status_code}"
                        }
                    )
                )

        # pylint: disable=broad-except
        except Exception as ex:
            event_handler.handle(
                WarningEvent({"message": "Failed triggering the Jenkins job"})
            )
            event_handler.handle(WarningEvent({"message": f"Error: {str(ex)}"}))


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
        """Triggers a full run of a Schema by creating a file with
        the appropriate content.

        Args:
            schema (AutoTransformSchema): The schema that will be run.
        """

        job_params = {
            "COMMAND": "run",
            "SCHEMA_NAME": schema.config.schema_name,
        }
        if schema.config.max_submissions:
            job_params["MAX_SUBMISSIONS"] = str(schema.config.max_submissions)
        shard_filter = [
            filt for filt in schema.filters if isinstance(filt, ShardFilter)
        ]
        if shard_filter:
            job_params["FILTER"] = json.dumps(shard_filter[0].bundle())

        self._create_file(job_params)

    def update(self, change: Change) -> None:
        """Triggers an update of the Change using a Jenkins API request.

        Args:
            change (Change): The Change to update.
        """

        self._create_file(
            {
                "COMMAND": "update",
                "CHANGE": json.dumps(change.bundle()),
            }
        )

    def _create_file(self, props: Dict[str, str]) -> None:
        """Creates the file for the Jenkins job.

        Args:
            props (Dict[str, str]): The props to add to the job.
        """

        JenkinsFileRunner.num_files += 1

        cwd = os.getcwd().replace("\\", "/")
        file_path = (
            f"{cwd}/autotransform/jenkins/job_{JenkinsFileRunner.num_files}.txt"
        )

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        content = "\n".join([f"{k}={v}" for k, v in props.items()])
        with open(file_path, "w+", encoding="UTF-8") as job_file:
            job_file.write(content)
            job_file.flush()
