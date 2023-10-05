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
from functools import cached_property
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError

import pytz
from autotransform.config import get_config
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.event.warning import WarningEvent
from autotransform.repo.git import GitRepo
from fastcore.basics import AttrDict  # type: ignore
from ghapi.all import GhApi, gh2date  # type: ignore


class GithubUtils:
    """A class for utilities used to interact with Github. Stores instances of objects to prevent
    excessive API usage.

    Attributes:
        __instances (Dict[str, GithubUtils]): A mapping of repo names to Util objects.
        _api (GhApi): The API object used to handle requests to Github.
        _fully_qualified_repo (str): The fully qualified name of the Github repo.
        _gists (Dict[str, Gist]): A mapping from id to Gist.
        _pulls (Dict[int, PullRequest]): A mapping from pull number to PullRequest.
    """

    __instances: Dict[str, GithubUtils] = {}

    _api: GhApi
    _fully_qualified_repo: str
    _gists: Dict[str, Gist]
    _pulls: Dict[int, PullRequest]

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
        token = get_config().github_token
        url = get_config().github_base_url
        repo_parts = fully_qualified_repo.split("/")
        self._api = GhApi(token=token, gh_host=url, owner=repo_parts[0], repo=repo_parts[1])
        self._fully_qualified_repo = fully_qualified_repo
        self._gists: Dict[str, Gist] = {}
        self._pulls: Dict[int, PullRequest] = {}

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
        return PullRequest(self._api, pull.number)

    def get_pull_request(self, pull_number: int) -> PullRequest:
        """Gets a pull request.

        Args:
            pull_number (int): The number of the pull request.

        Returns:
            PullRequest: The pull request.
        """

        if pull_number not in self._pulls:
            self._pulls[pull_number] = PullRequest(self._api, pull_number)
        return self._pulls[pull_number]

    def create_gist(
        self, files: Dict[str, Dict[str, str]], description: str, public: bool = True
    ) -> Gist:
        """Creates a Gist containing the supplied information

        Args:
            files (Dict[str, Dict[str, str]]): The files to include in the gist.
            description (str): A simple description of the gist.
            public (bool, optional): Whether the gist should be public. Defaults to True.

        Returns:
            Gist: The created gist.
        """

        res = self._api.gists.create(description=description, files=files, public=public)
        return Gist(self._api, res.id)

    def get_gist(self, gist_id: str) -> Gist:
        """Gets a wrapper around the requested gist.

        Args:
            gist_id (str): The id of the gist.

        Returns:
            Gist: The requested gist.
        """

        if gist_id not in self._gists:
            self._gists[gist_id] = Gist(self._api, gist_id)
        return self._gists[gist_id]

    def get_open_pull_requests(self, base: Optional[str] = None) -> List[PullRequest]:
        """Gets all outstanding pull requests from the repo.

        Args:
            base (Optional[str], optional): The base branch to fetch pull requests against.
                Defaults to None.

        Returns:
            List[PullRequest]: The list of all requests outstanding for the repo.
        """

        username = self._api.users.get_authenticated().login
        query = f"type:pr state:open author:{username} repo:{self._fully_qualified_repo}"
        if base is not None:
            query = f"{query} base:{base}"
        page = 1
        num_per_page = 100
        fetch_more = True
        all_pulls: Set[int] = set()
        while fetch_more:
            prs = self._api.search.issues_and_pull_requests(
                q=query, sort="created", order="desc", per_page=num_per_page, page=page
            )
            fetch_more = len(prs["items"]) == num_per_page
            page = page + 1
            all_pulls = all_pulls.union([pr.number for pr in prs["items"]])

        pulls = [self.get_pull_request(pull_number) for pull_number in all_pulls]

        return [pull for pull in pulls if pull.branch.startswith(GitRepo.BRANCH_NAME_PREFIX)]

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

        current_time = datetime.now().replace(microsecond=0)
        check_time = current_time - timedelta(days=1)
        self._api.actions.create_workflow_dispatch(workflow_id=workflow, ref=ref, inputs=inputs)
        # We wait a bit to make sure Github's API is updated before printing a best guess of the
        # Workflow run's URL
        time.sleep(2)
        EventHandler.get().handle(DebugEvent({"message": "Checking for workflow run URL"}))
        res = self._api.actions.list_workflow_runs(
            workflow_id=workflow,
            actor=self._api.users.get_authenticated().login,
            branch=ref,
            event="workflow_dispatch",
            created=f">={check_time.isoformat()}",
        )
        if not res.workflow_runs:
            return ""
        return res.workflow_runs[0].html_url


# pylint: disable=too-many-public-methods
class PullRequest:
    """A wrapper around GhApi pull request response for simplified access to pull request info.

    Attributes:
        number (int): The number of the pull request.
        _api (GhApi): The API object used to access Github's API.
    """

    number: int

    _api: GhApi

    def __init__(self, api: GhApi, pull_number: int):
        self.number = pull_number
        self._api = api

    @property
    def body(self) -> str:
        """Gets the body of the pull request.

        Returns:
            str: The body of the pull request.
        """

        return self._detailed_info.body

    @property
    def branch(self) -> str:
        """Gets the name of the head branch for the pull request.

        Returns:
            str: The name of the head branch.
        """

        return self._detailed_info.head.ref

    @property
    def merged(self) -> bool:
        """Whether the pull request has been merged.

        Returns:
            bool: Whether the pull request was merged.
        """

        return self._detailed_info.merged

    @property
    def owner_id(self) -> int:
        """The ID of the user that created the pull request.

        Returns:
            int: The ID of the owner of the pull request.
        """

        return self._detailed_info.user.id

    def is_open(self) -> bool:
        """A simple check if the pull request is open.

        Returns:
            bool: Whether the pull request is open.
        """

        return self._detailed_info.state == "open"

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
        reviews = self._api.pulls.list_reviews(pull_number=self.number)
        reviews.reverse()
        for review in reviews:
            if review.state in review_states:
                return review.state
        return None

    def get_test_state(self) -> Optional[str]:
        """Gets the state of tests on the PR using the checks API.

        Returns:
            Optional[str]: The combined state of test runs.
        """

        possible_conclusions = [
            "action_required",
            "canceled",
            "timed_out",
            "failure",
            "neutral",
            "success",
        ]

        checks = self._api.checks.list_for_ref(ref=self.branch)
        for check in checks.check_runs:
            if check.status != "completed":
                return "pending"
        results = {run.conclusion for run in checks.check_runs}
        for conclusion in possible_conclusions:
            if conclusion in results:
                return conclusion
        return "success"

    def get_labels(self) -> List[str]:
        """Gets the labels for a Pull Request.

        Returns:
            List[str]: The labels for a Pull Request.
        """

        labels = self._api.issues.list_labels_on_issue(issue_number=self.number)
        return [label["name"] for label in labels]

    def get_reviewers(self) -> List[str]:
        """Gets the requested reviewers for a Pull Request.

        Returns:
            List[str]: The requested reviewers for a Pull Request.
        """

        return self._reviewers[0]

    def get_team_reviewers(self) -> List[str]:
        """Gets the requested team reviewers for a Pull Request.

        Returns:
            List[str]: The requested team reviewers for a Pull Request.
        """

        return self._reviewers[1]

    @cached_property
    def _detailed_info(self) -> AttrDict:
        """A cached value of the detailed info from the Github API.

        Returns:
            AttrDict: The detailed info of the PR.
        """

        return self._api.pulls.get(pull_number=self.number)

    @cached_property
    def _reviewers(self) -> Tuple[List[str], List[str]]:
        """A cached value of the reviewers of the change.

        Returns:
            Tuple[List[str], List[str]]: A tuple containing user reviewers and team reviewers.
        """

        requested_reviewers = self._api.pulls.list_requested_reviewers(pull_number=self.number)
        per_page = 50
        page = 1
        user_reviewers = [reviewer["login"] for reviewer in requested_reviewers["users"]]
        team_reviewers = [reviewer["name"] for reviewer in requested_reviewers["teams"]]
        more_reviewers = True
        while more_reviewers:
            reviews = self._api.pulls.list_reviews(
                pull_number=self.number, page=page, per_page=per_page
            )
            user_reviewers.extend(review["user"]["login"] for review in reviews)
            more_reviewers = len(reviews) == per_page
        return (list(set(user_reviewers)), list(set(team_reviewers)))

    def get_created_at(self) -> int:
        """Gets the created at timestamp.

        Returns:
            int: The timestamp for when the pull request was created.
        """
        return int(pytz.utc.localize(gh2date(self._detailed_info.created_at)).timestamp())

    def get_updated_at(self) -> int:
        """Gets the updated at timestamp.

        Returns:
            int: The timestamp for when the pull request was updated.
        """
        return int(pytz.utc.localize(gh2date(self._detailed_info.updated_at)).timestamp())

    def get_mergeable_state(self) -> str:
        """Gets the mergeable state of the PR.

        Returns:
            str: The mergeable state.
        """
        return (
            str(self._detailed_info.mergeable_state)
            if "mergeable_state" in self._detailed_info
            else "unknown"
        )

    def add_labels(self, labels: List[str]) -> None:
        """Adds a list of labels to the pull request.

        Args:
            labels (List[str]): The labels to add to the pull request.
        """

        self._api.issues.add_labels(issue_number=self.number, labels=labels)

    def add_reviewers(self, reviewers: List[str], team_reviewers: List[str]) -> None:
        """Adds a list of labels to the pull request.

        Args:
            reviewers (List[str]): The reviewers to request for the pull request.
            team_reviewers (List[str]): The team reviewers to request for the pull request.
        """

        self._api.pulls.request_reviewers(
            pull_number=self.number,
            reviewers=list(set(reviewers)),
            team_reviewers=list(set(team_reviewers)),
        )

    def create_comment(self, body: str) -> None:
        """Adds a comment to the pull request.

        Args:
            body (str): The body of the comment.
        """

        self._api.issues.create_comment(issue_number=self.number, body=body)

    def merge(self) -> bool:
        """Merges the pull request.

        Returns:
            bool: Whether the pull request was successfully merged.
        """

        try:
            res = self._api.pulls.merge(pull_number=self.number)
            return res.merged
        except HTTPError as err:
            EventHandler.get().handle(
                WarningEvent({"message": f"Failed merge pull request {self.number}: {err}"})
            )
            return False

    def remove_label(self, label: str) -> None:
        """Removes a label from the pull request.

        Args:
            label (str): The label to remove from the pull request.
        """

        self._api.issues.remove_label(issue_number=self.number, name=label)

    def close(self) -> bool:
        """Closes the pull request.

        Returns:
            bool: Whether the update happened successfully.
        """

        try:
            res = self._api.pulls.update(pull_number=self.number, state="closed")
            return res.state == "closed"
        except HTTPError as err:
            EventHandler.get().handle(
                WarningEvent({"message": f"Failed to close pull request {self.number}: {err}"})
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
                WarningEvent({"message": f"Failed to delete branch {self.branch}: {err}"})
            )
            return False


class Gist:
    """A wrapper around GhApi gist response for simplified access to gist info.

    Attributes:
        id (str): The id of the gist.
        _api (GhApi): The API object used to access Github's API.
    """

    gist_id: str

    _api: GhApi

    def __init__(self, api: GhApi, gist_id: str):
        self.gist_id = gist_id
        self._api = api

    @cached_property
    def _detailed_info(self) -> AttrDict:
        """A cached value of the detailed info from the Github API.

        Returns:
            AttrDict: The detailed info of the gist.
        """

        return self._api.gists.get(gist_id=self.gist_id)

    def get_description(self) -> str:
        """Gets the description of the gist.

        Returns:
            str: The description of the gist.
        """

        return self._detailed_info.description

    def get_file_content(self, file_name: str) -> Optional[str]:
        """Gets the content of the requested file within the gist.

        Args:
            file_name (str): The name of the file to get the content for.

        Returns:
            Optional[str]: The contents of the file. None if the gist does not have a file with
                the supplied name.
        """

        if file_name not in self._detailed_info.files:
            return None
        return self._detailed_info.files[file_name].content
