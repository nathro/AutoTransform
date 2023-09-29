# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the LocalRunner."""

import pytest
from unittest.mock import Mock, MagicMock

from autotransform.change.base import Change
from autotransform.runner.local import LocalRunner
from autotransform.schema.schema import AutoTransformSchema


def test_run_with_valid_schema():
    """Test the run method with a valid AutoTransformSchema object."""
    schema = Mock(spec=AutoTransformSchema)
    runner = LocalRunner()
    runner.run(schema)
    schema.run.assert_called_once()


def test_run_with_invalid_schema():
    """Test the run method with an invalid AutoTransformSchema object."""
    schema = MagicMock()
    schema.run.side_effect = AttributeError  # Raises AttributeError when 'run' is called
    runner = LocalRunner()
    with pytest.raises(AttributeError):
        runner.run(schema)


def test_update_with_valid_change():
    """Test the update method with a valid Change object."""
    change = Mock(spec=Change)
    schema = Mock(spec=AutoTransformSchema)
    batch = Mock()
    change.get_schema.return_value = schema
    change.get_batch.return_value = batch
    runner = LocalRunner()
    runner.update(change)
    schema.execute_batch.assert_called_once_with(batch, change)


def test_update_with_invalid_change():
    """Test the update method with an invalid Change object."""
    change = MagicMock()
    change.get_schema.side_effect = (
        AttributeError  # Raises AttributeError when 'get_schema' is called
    )
    runner = LocalRunner()
    with pytest.raises(AttributeError):
        runner.update(change)


def test_update_with_none_schema():
    """Test the update method with a Change object that has a None schema."""
    change = Mock(spec=Change)
    change.get_schema.return_value = None
    runner = LocalRunner()
    with pytest.raises(AttributeError):
        runner.update(change)


def test_update_with_none_batch():
    """Test the update method with a Change object that has a None batch."""
    change = Mock(spec=Change)
    schema = Mock(spec=AutoTransformSchema)
    change.get_schema.return_value = schema
    change.get_batch.return_value = None
    runner = LocalRunner()
    runner.update(change)
    schema.execute_batch.assert_called_once_with(None, change)
