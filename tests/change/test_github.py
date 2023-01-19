# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for GithubChange component."""

import mock
from autotransform.batcher.single import SingleBatcher
from autotransform.change.base import ChangeState, ReviewState
from autotransform.change.github import GithubChange
from autotransform.filter.regex import RegexFilter
from autotransform.input.directory import DirectoryInput
from autotransform.item.file import FileItem
from autotransform.repo.github import GithubRepo
from autotransform.schema.config import SchemaConfig
from autotransform.schema.schema import AutoTransformSchema
from autotransform.transformer.regex import RegexTransformer
from autotransform.util.github import GithubUtils, PullRequest


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_data_from_body(mock_get_pull_request):
    """Tests the get_schema() and get_batch() methods from the Change."""

    repo = GithubRepo(
        base_branch="master",
        full_github_name="nathro/ATTest",
    )
    schema = AutoTransformSchema(
        input=DirectoryInput(paths="."),
        batcher=SingleBatcher(title="foo", metadata={"body": "bar"}),
        transformer=RegexTransformer(pattern="input", replacement="inputsource"),
        config=SchemaConfig(schema_name="Sample", owners=["foo", "bar"]),
        filters=[RegexFilter(pattern=".*\\.py$")],
        repo=repo,
    )
    batch = {"title": "fizz", "metadata": {"body": "bar"}, "items": [FileItem(key="foo.py")]}
    pull_request = mock.create_autospec(PullRequest)
    pull_request.body = repo.get_automation_info(schema, batch)
    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_batch() == batch


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_state_merged(mock_get_pull_request):
    """Tests the get_state() method from the Change returns merged for merged Changes."""

    pull_request = mock.create_autospec(PullRequest)
    pull_request.merged = True
    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_state() == ChangeState.MERGED


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_state_closed(mock_get_pull_request):
    """Tests the get_state() method from the Change returns closed for closed Changes."""

    pull_request = mock.create_autospec(PullRequest)
    pull_request.merged = False
    # pylint: disable=protected-access
    pull_request.is_closed.return_value = True

    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_state() == ChangeState.CLOSED


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_state_approved(mock_get_pull_request):
    """Tests the get_state() method from the Change returns approved for approved Changes."""

    pull_request = mock.create_autospec(PullRequest)
    pull_request.merged = False
    # pylint: disable=protected-access
    pull_request.is_closed.return_value = False
    pull_request.get_review_state.return_value = "APPROVED"

    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_review_state() == ReviewState.APPROVED


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_state_changes_requested(mock_get_pull_request):
    """Tests the get_state() method from the Change returns changes_requested for
    changes_requested Changes."""

    pull_request = mock.create_autospec(PullRequest)
    pull_request.merged = False
    # pylint: disable=protected-access
    pull_request.is_closed.return_value = False
    pull_request.get_review_state.return_value = "CHANGES_REQUESTED"

    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_review_state() == ReviewState.CHANGES_REQUESTED


@mock.patch.object(GithubUtils, "get_pull_request")
def test_get_state_open(mock_get_pull_request):
    """Tests the get_state() method from the Change returns open for open Changes."""

    pull_request = mock.create_autospec(PullRequest)
    pull_request.merged = False
    # pylint: disable=protected-access
    pull_request.is_closed.return_value = False
    pull_request.get_review_state.return_value = None

    mock_get_pull_request.return_value = pull_request

    change = GithubChange(full_github_name="nathro/ATTest", pull_number=1)

    assert change.get_state() == ChangeState.OPEN
