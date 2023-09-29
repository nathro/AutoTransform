# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from unittest.mock import Mock
from autotransform.step.action.source import AbandonAction, MergeAction, NoneAction, UpdateAction
from autotransform.change.base import Change
from autotransform.runner.base import Runner


def test_abandon_action_run():
    """Test the run method of AbandonAction."""
    change = Mock(spec=Change)
    action = AbandonAction()
    assert action.run(change) == change.abandon.return_value


def test_merge_action_run():
    """Test the run method of MergeAction."""
    change = Mock(spec=Change)
    action = MergeAction()
    assert action.run(change) == change.merge.return_value


def test_none_action_run():
    """Test the run method of NoneAction."""
    change = Mock(spec=Change)
    action = NoneAction()
    assert action.run(change) is True


def test_update_action_set_runner():
    """Test the set_runner method of UpdateAction."""
    runner = Mock(spec=Runner)
    UpdateAction.set_runner(runner)
    assert UpdateAction._runner == runner


def test_update_action_run():
    """Test the run method of UpdateAction."""
    change = Mock(spec=Change)
    runner = Mock(spec=Runner)
    UpdateAction.set_runner(runner)
    action = UpdateAction()
    assert action.run(change) == change.update.return_value
