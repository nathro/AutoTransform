# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that Manager functions as expected."""

import json
import pathlib

from autotransform.change.base import ReviewState
from autotransform.repo.github import GithubRepo
from autotransform.step.action.source import AbandonAction, MergeAction, UpdateAction
from autotransform.step.condition.comparison import ComparisonType
from autotransform.step.condition.state import ReviewStateCondition
from autotransform.step.condition.updated import UpdatedAgoCondition
from autotransform.step.conditional import ConditionalStep
from autotransform.util.manager import Manager


def get_sample_manager() -> Manager:
    """Gets a sample Manager.

    Returns:
        Manager: The sample Manager.
    """

    return Manager(
        repo=GithubRepo(base_branch="main", full_github_name="nathro/ATTest"),
        steps=[
            ConditionalStep(
                actions=[MergeAction()],
                condition=ReviewStateCondition(
                    comparison=ComparisonType.EQUAL, value=ReviewState.APPROVED
                ),
            ),
            ConditionalStep(
                actions=[AbandonAction()],
                condition=ReviewStateCondition(
                    comparison=ComparisonType.EQUAL, value=ReviewState.CHANGES_REQUESTED
                ),
            ),
            ConditionalStep(
                actions=[UpdateAction()],
                condition=UpdatedAgoCondition(
                    comparison=ComparisonType.GREATER_THAN_OR_EQUAL, value=259200
                ),
            ),
        ],
    )


def test_decoding():
    """Tests that the Manager component is decoded properly."""

    parent_dir = pathlib.Path(__file__).parent.resolve()
    manager = Manager.read(parent_dir / "data" / "manager.json")
    assert manager == get_sample_manager()


def test_encoding():
    """Tests that the Manager component is encoded properly."""

    parent_dir = pathlib.Path(__file__).parent.resolve()
    with open(parent_dir / "data" / "manager.json", "r", encoding="UTF-8") as file:
        assert json.dumps(get_sample_manager().bundle(), indent=4) == file.read()
