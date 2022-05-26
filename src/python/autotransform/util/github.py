# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Github related utilities."""

from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError

import pytz
from fastcore.basics import AttrDict  # type: ignore
from ghapi.all import GhApi, gh2date  # type: ignore

from autotransform.config import fetcher as Config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler


class GithubUtils:
    """A class for utilities used to interact with Github. Stores instances of objects to prevent
    excessive API usage.

    Attributes:
        __instances (Dict[str, GithubUtils]): A mapping of repo names to Util objects.
        _api (GhApi): The API object used to handle requests to Github.
    """

    __instances: Dict[str, GithubUtils] = {}

    _api: GhApi

    BEGIN_SCHEMA: str = "<<<<BEGIN SCHEMA>>>>"
    END_SCHEMA: str = "<<<<END SCHEMA>>>>"

    BEGIN_BATCH: str = "<<<<BEGIN BATCH>>>>"
    END_BATCH: str = "<<<<END BATCH>>>>"

    def __init__(self, fully_qualified_repo: str):
        """A simple constructor.

        Args:
            fully_qualified_repo (str): The fully qualified name of the repo, uses the
                format {owner}/{repo}.
        """
        assert fully_qualified_repo not in GithubUtils.__instances
        token = Config.get_credentials_github_token()
        url = Config.get_credentials_github_base_url()
        repo_parts = fully_qualified_repo.split("/")
        self._api = GhApi(token=token, gh_host=url, owner=repo_parts[0], repo=repo_parts[1])

    @staticmethod
    def get(fully_qualified_repo: str) -> GithubUtils:
        """Gets an instance of the GithubUtils for a specific repo which is stored in a cache.

        Args:
            fully_qualified_repo (str): The fully qualified name of the repo, uses the
                format {owner}/{repo}.

        Returns:
            GithubUtils: A util class with a cached API object for requests.
        """
        if fully_qualified_repo not in GithubUtils.__instances:
            util = GithubUtils(fully_qualified_repo)
            GithubUtils.__instances[fully_qualified_repo] = util
        return GithubUtils.__instances[fully_qualified_repo]

    def get_user_id(self) -> int:
        """Gets the user ID of the authenticated user.

        Returns:
            int: The user ID of the authenticated user.
        """

        return self._api.users.get_authenticated().id

    def create_pull_request(self, title: str, body: str, base: str, head: str) -> PullRequest:
        """Create a pull request with the given information.

        Args:
            title (str): The title of the pull request.
            body (str): The body of the pull request.
            base (str): The base branch the pull request is against.
            head (str): The head to apply to the base branch.

        Returns:
            PullRequest: The created pull request.
        """

        pull = self._api.pulls.create(title=title, head=head, base=base, body=body)
        return PullRequest(self._api, pull)

    def get_pull_request(self, pull_number: int) -> PullRequest:
        """Gets a pull request from the Github API.

        Args:
            pull_number (int): The number of the pull request.

        Returns:
            PullRequest: The pull request.
        """

        return PullRequest(self, pull_number)

    def get_open_pull_requests(self, base: Optional[str] = None) -> List[PullRequest]:
        """Gets all outstanding pull requests from the repo.

        Args:
            base (Optional[str], optional): The base branch to fetch pull requests against.
                Defaults to None.

        Returns:
            List[PullRequest]: The list of all requests outstanding for the repo.
        """

        pulls = self._api.pulls.list(state="open", base=base, sort="created", direction="desc")
        return [PullRequest(self._api, pull) for pull in pulls]

    def create_workflow_dispatch(
        self, workflow: str | int, ref: str, inputs: Dict[str, Any]
    ) -> Optional[str]:
        """Creates a workflow dispatch event and runs it.

        Args:
            workflow (str | int): The ID or filename of the workflow to run.
            ref (str): The ref to run the workflow on.
            inputs (Dict[str, Any]): Any inputs the workflow needs.

        Returns:
            Optional[str]: The best guess URL of the workflow run. None if failed.
        """

        try:
            current_time = datetime.now().replace(microsecond=0)
            check_time = current_time - timedelta(days=1)
            self._api.actions.create_workflow_dispatch(workflow, ref, inputs)
            # We wait a bit to make sure Github's API is updated before printing a best guess of the
            # Workflow run's URL
            time.sleep(2)
            EventHandler.get().handle(DebugEvent({"message": "Checking for workflow run URL"}))
            res = self._api.actions.list_workflow_runs(
                workflow,
                self._api.users.get_authenticated().login,
                ref,
                "workflow_dispatch",
                created=f">={check_time.isoformat()}",
            )
            if not res.workflow_runs:
                return ""
            return res.workflow_runs[0].html_url
        except HTTPError as err:
            EventHandler.get().handle(
                DebugEvent({"message": f"Failed dispatch workflow {workflow}: {err}"})
            )
            return None


class PullRequest:
    """A wrapper around GhApi pull request response for simplified access to pull request info.

    Attributes:
        body (str): The body of the pull request.
        branch (str): The branch of the pull request.
        merged (bool): Whether the pull request has been merged.
        number (int): The number of the pull request.
        _api (GhApi): The API object used to access Github's API.
        _state (str): The state of the pull request.
    """

    # pylint: disable=too-many-instance-attributes

    body: str
    branch: str
    merged: bool
    number: int
    owner_id: int

    _api: GhApi
    _state: str

    def __init__(self, api: GhApi, pull: AttrDict):

        self.body = pull.body
        self.branch = pull.head.ref
        self.merged = pull.merged
        self.number = pull.number
        self.owner_id = pull.user.id
        self._created_at = pull.created_at
        self._updated_at = pull.updated_at
        self._api = api
        self._state = pull.state

    @staticmethod
    def get_from_number(api: GhApi, pull_number: int) -> PullRequest:
        """Gets a pull request with the given number.

        Args:
            api (GhApi): The API object used to access Github's API.
            pull_number (int): The number of the pull request.

        Returns:
            PullRequest: The pull request associated with the number.
        """

        pull = api.pulls.get(pull_number)
        return PullRequest(api, pull)

    def is_open(self) -> bool:
        """A simple check if the pull request is open.

        Returns:
            bool: Whether the pull request is open.
        """

        return self._state == "open"

    def is_closed(self) -> bool:
        """A simple check if the pull request is closed.

        Returns:
            bool: Whether the pull request is closed.
        """

        return not self.is_open()

    def get_review_state(self) -> Optional[str]:
        """The state of the most recent review, only checking reviews that are
        "APPROVED" or "CHANGES_REQUESTED". If there are no approving or change_requested
        reviews, returns None.

        Returns:
            Optional[str]: The state of the review.
        """

        review_states = ["APPROVED", "CHANGES_REQUESTED"]
        reviews = self._api.pulls.list_reviews(self.number)
        reviews.reverse()
        for review in reviews:
            if review.state in review_states:
                return review.state
        return None

    def get_created_at(self) -> int:
        """Gets the created at timestamp.

        Returns:
            int: The timestamp for when the pull request was created.
        """
        return int(pytz.utc.localize(gh2date(self._created_at)).timestamp())

    def get_updated_at(self) -> int:
        """Gets the updated at timestamp.

        Returns:
            int: The timestamp for when the pull request was updated.
        """
        return int(pytz.utc.localize(gh2date(self._updated_at)).timestamp())

    def add_labels(self, labels: List[str]) -> None:
        """Adds a list of labels to the pull request.

        Args:
            labels (List[str]): the labels to add to the pull request.
        """

        self._api.issues.add_labels(self.number, labels)

    def merge(self) -> bool:
        """Merges the pull request.

        Returns:
            bool: Whether the pull request was successfully merged.
        """

        try:
            res = self._api.pulls.merge(self.number)
            return res.merged
        except HTTPError as err:
            EventHandler.get().handle(
                DebugEvent({"message": f"Failed merge pull request {self.number}: {err}"})
            )
            return False

    def close(self) -> bool:
        """Closes the pull request.

        Returns:
            bool: Whether the update happened successfully.
        """

        try:
            res = self._api.pulls.update(self.number, state="closed")
            return res.state == "closed"
        except HTTPError as err:
            EventHandler.get().handle(
                DebugEvent({"message": f"Failed to close pull request {self.number}: {err}"})
            )
            return False

    def delete_branch(self) -> bool:
        """Deletes the branch associated with the pull request.

        Returns:
            bool: Whether the deletion was successful.
        """

        try:
            self._api.delete_branch(self.branch)
            return True
        except HTTPError as err:
            EventHandler.get().handle(
                DebugEvent({"message": f"Failed to delete branch {self.branch}: {err}"})
            )
            return False
