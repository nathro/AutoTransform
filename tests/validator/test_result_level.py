# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Tests that ValidationResultLevel works as expected."""

from autotransform.validator.base import ValidationResultLevel

# pylint: disable=unneeded-not


def test_gt():
    """Test that > checks work"""
    assert not ValidationResultLevel.ERROR > ValidationResultLevel.ERROR
    assert ValidationResultLevel.ERROR > ValidationResultLevel.WARNING
    assert ValidationResultLevel.ERROR > ValidationResultLevel.NONE
    assert not ValidationResultLevel.WARNING > ValidationResultLevel.ERROR
    assert not ValidationResultLevel.WARNING > ValidationResultLevel.WARNING
    assert ValidationResultLevel.WARNING > ValidationResultLevel.NONE
    assert not ValidationResultLevel.NONE > ValidationResultLevel.ERROR
    assert not ValidationResultLevel.NONE > ValidationResultLevel.WARNING
    assert not ValidationResultLevel.NONE > ValidationResultLevel.NONE


def test_ge():
    """Test that >= checks work"""
    assert ValidationResultLevel.ERROR >= ValidationResultLevel.ERROR
    assert ValidationResultLevel.ERROR >= ValidationResultLevel.WARNING
    assert ValidationResultLevel.ERROR >= ValidationResultLevel.NONE
    assert not ValidationResultLevel.WARNING >= ValidationResultLevel.ERROR
    assert ValidationResultLevel.WARNING >= ValidationResultLevel.WARNING
    assert ValidationResultLevel.WARNING >= ValidationResultLevel.NONE
    assert not ValidationResultLevel.NONE >= ValidationResultLevel.ERROR
    assert not ValidationResultLevel.NONE >= ValidationResultLevel.WARNING
    assert ValidationResultLevel.NONE >= ValidationResultLevel.NONE


def test_lt():
    """Test that < checks work"""
    assert not ValidationResultLevel.ERROR < ValidationResultLevel.ERROR
    assert not ValidationResultLevel.ERROR < ValidationResultLevel.WARNING
    assert not ValidationResultLevel.ERROR < ValidationResultLevel.NONE
    assert ValidationResultLevel.WARNING < ValidationResultLevel.ERROR
    assert not ValidationResultLevel.WARNING < ValidationResultLevel.WARNING
    assert not ValidationResultLevel.WARNING < ValidationResultLevel.NONE
    assert ValidationResultLevel.NONE < ValidationResultLevel.ERROR
    assert ValidationResultLevel.NONE < ValidationResultLevel.WARNING
    assert not ValidationResultLevel.NONE < ValidationResultLevel.NONE


def test_le():
    """Test that <= checks work"""
    assert ValidationResultLevel.ERROR <= ValidationResultLevel.ERROR
    assert not ValidationResultLevel.ERROR <= ValidationResultLevel.WARNING
    assert not ValidationResultLevel.ERROR <= ValidationResultLevel.NONE
    assert ValidationResultLevel.WARNING <= ValidationResultLevel.ERROR
    assert ValidationResultLevel.WARNING <= ValidationResultLevel.WARNING
    assert not ValidationResultLevel.WARNING <= ValidationResultLevel.NONE
    assert ValidationResultLevel.NONE <= ValidationResultLevel.ERROR
    assert ValidationResultLevel.NONE <= ValidationResultLevel.WARNING
    assert ValidationResultLevel.NONE <= ValidationResultLevel.NONE


def test_eq():
    """Test that == checks work"""
    assert ValidationResultLevel.ERROR == ValidationResultLevel.ERROR
    assert not ValidationResultLevel.ERROR == ValidationResultLevel.WARNING
    assert not ValidationResultLevel.ERROR == ValidationResultLevel.NONE
    assert not ValidationResultLevel.WARNING == ValidationResultLevel.ERROR
    assert ValidationResultLevel.WARNING == ValidationResultLevel.WARNING
    assert not ValidationResultLevel.WARNING == ValidationResultLevel.NONE
    assert not ValidationResultLevel.NONE == ValidationResultLevel.ERROR
    assert not ValidationResultLevel.NONE == ValidationResultLevel.WARNING
    assert ValidationResultLevel.NONE == ValidationResultLevel.NONE


def test_ne():
    """Test that != checks work"""
    assert not ValidationResultLevel.ERROR != ValidationResultLevel.ERROR
    assert ValidationResultLevel.ERROR != ValidationResultLevel.WARNING
    assert ValidationResultLevel.ERROR != ValidationResultLevel.NONE
    assert ValidationResultLevel.WARNING != ValidationResultLevel.ERROR
    assert not ValidationResultLevel.WARNING != ValidationResultLevel.WARNING
    assert ValidationResultLevel.WARNING != ValidationResultLevel.NONE
    assert ValidationResultLevel.NONE != ValidationResultLevel.ERROR
    assert ValidationResultLevel.NONE != ValidationResultLevel.WARNING
    assert not ValidationResultLevel.NONE != ValidationResultLevel.NONE
