# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests for the LoggingLevel enumeration in the autotransform.event.logginglevel module."""

import pytest
from autotransform.event.logginglevel import LoggingLevel


def test_logging_level_count():
    """Test that the LoggingLevel enumeration has the correct number of levels."""
    assert len(LoggingLevel) == 5


def test_logging_level_names():
    """Test that the LoggingLevel enumeration has the correct levels."""
    assert set(level.name for level in LoggingLevel) == {
        "ERROR",
        "WARNING",
        "INFO",
        "VERBOSE",
        "DEBUG",
    }


def test_logging_level_values():
    """Test that the LoggingLevel enumeration levels have the correct associated integer values."""
    assert LoggingLevel.ERROR.value == 0
    assert LoggingLevel.WARNING.value == 1
    assert LoggingLevel.INFO.value == 2
    assert LoggingLevel.VERBOSE.value == 3
    assert LoggingLevel.DEBUG.value == 4


def test_logging_level_comparison():
    """Test that the LoggingLevel enumeration levels can be correctly compared using their integer values."""
    assert LoggingLevel.ERROR < LoggingLevel.WARNING
    assert LoggingLevel.WARNING < LoggingLevel.INFO
    assert LoggingLevel.INFO < LoggingLevel.VERBOSE
    assert LoggingLevel.VERBOSE < LoggingLevel.DEBUG


def test_logging_level_to_int_conversion():
    """Test that the LoggingLevel enumeration levels can be correctly converted to their integer values."""
    assert int(LoggingLevel.ERROR) == 0
    assert int(LoggingLevel.WARNING) == 1
    assert int(LoggingLevel.INFO) == 2
    assert int(LoggingLevel.VERBOSE) == 3
    assert int(LoggingLevel.DEBUG) == 4


def test_logging_level_from_int_conversion():
    """Test that the LoggingLevel enumeration levels can be correctly converted from their integer values."""
    assert LoggingLevel(0) == LoggingLevel.ERROR
    assert LoggingLevel(1) == LoggingLevel.WARNING
    assert LoggingLevel(2) == LoggingLevel.INFO
    assert LoggingLevel(3) == LoggingLevel.VERBOSE
    assert LoggingLevel(4) == LoggingLevel.DEBUG


def test_invalid_int_to_logging_level_conversion():
    """Test that trying to convert an invalid integer value to a LoggingLevel enumeration level raises a ValueError."""
    with pytest.raises(ValueError):
        LoggingLevel(5)


def test_invalid_type_comparison():
    """Test that trying to compare a LoggingLevel enumeration level with an invalid type raises a TypeError."""
    with pytest.raises(TypeError):
        assert LoggingLevel.ERROR < "ERROR"
