# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the GithubRepo component."""

from unittest.mock import patch, create_autospec

from autotransform.repo.github import GithubRepo
from autotransform.util.github import GithubUtils, PullRequest


@patch("autotransform.util.github.GithubUtils.get", autospec=True)
def test_get_outstanding_changes(mock_github_utils):
    """Tests that outstanding changes are fetched correctly."""

    autotransform_pr = create_autospec(PullRequest)
    autotransform_pr.owner_id = 1
    autotransform_pr.number = 1
    human_pr = create_autospec(PullRequest)
    human_pr.owner_id = 2
    human_pr.number = 2
    util = create_autospec(GithubUtils)
    util.get_user_id.return_value = 1
    util.get_open_pull_requests.return_value = [autotransform_pr, human_pr]
    mock_github_utils.return_value = util

    outstanding_changes = GithubRepo(
        base_branch="master", full_github_name="nathro/AutoTransform"
    ).get_outstanding_changes()

    assert len(outstanding_changes) == 1
    assert outstanding_changes[0].pull_number == autotransform_pr.number
