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

    with pytest.raises(ValueError, match="Either reviewers or team reviewers must be supplied"):
        AddReviewersAction()

    with pytest.raises(ValueError, match="Either reviewers or team reviewers must be supplied"):
        AddReviewersAction(reviewers=[])

    with pytest.raises(ValueError, match="Either reviewers or team reviewers must be supplied"):
        AddReviewersAction(team_reviewers=[])

    with pytest.raises(ValueError, match="Either reviewers or team reviewers must be supplied"):
        AddReviewersAction(reviewers=[], team_reviewers=[])


def test_empty_strings():
    """Checks that actions with empty strings can not be created."""

    with pytest.raises(ValueError, match="Reviewers must be non-empty strings"):
        AddReviewersAction(reviewers=[""])

    with pytest.raises(ValueError, match="Reviewers must be non-empty strings"):
        AddReviewersAction(reviewers=["nathro", "", "nathro"])

    with pytest.raises(ValueError, match="Team reviewers must be non-empty strings"):
        AddReviewersAction(team_reviewers=["slack", "", "slack"])

    with pytest.raises(ValueError, match="Team reviewers must be non-empty strings"):
        AddReviewersAction(reviewers=["nathro"], team_reviewers=[""])

    with pytest.raises(ValueError, match="Reviewers must be non-empty strings"):
        AddReviewersAction(reviewers=[""], team_reviewers=["slack"])
