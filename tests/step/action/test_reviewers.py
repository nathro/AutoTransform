# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that the labels actions works as expected."""

import pytest

from autotransform.step.action.reviewers import AddReviewersAction


def test_no_reviewers_provided():
    """Checks that an action with no reviewers can not be created."""

    AddReviewersAction(reviewers=["nathro"])
    AddReviewersAction(team_reviewers=["slack"])

    error_message = "Either reviewers or team reviewers must be supplied"
    with pytest.raises(ValueError, match=error_message):
        AddReviewersAction()

    with pytest.raises(ValueError, match=error_message):
        AddReviewersAction(reviewers=[])

    with pytest.raises(ValueError, match=error_message):
        AddReviewersAction(team_reviewers=[])

    with pytest.raises(ValueError, match=error_message):
        AddReviewersAction(reviewers=[], team_reviewers=[])


def test_empty_strings():
    """Checks that actions with empty strings can not be created."""

    reviewers_error_message = "Reviewers must be non-empty strings"
    team_reviewers_error_message = "Team reviewers must be non-empty strings"

    with pytest.raises(ValueError, match=reviewers_error_message):
        AddReviewersAction(reviewers=[""])

    with pytest.raises(ValueError, match=reviewers_error_message):
        AddReviewersAction(reviewers=["nathro", "", "nathro"])

    with pytest.raises(ValueError, match=team_reviewers_error_message):
        AddReviewersAction(team_reviewers=["slack", "", "slack"])

    with pytest.raises(ValueError, match=team_reviewers_error_message):
        AddReviewersAction(reviewers=["nathro"], team_reviewers=[""])

    with pytest.raises(ValueError, match=reviewers_error_message):
        AddReviewersAction(reviewers=[""], team_reviewers=["slack"])
