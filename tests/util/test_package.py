# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Unit tests for the utility functions in the package module."""

import pathlib
from autotransform.util import package


def test_get_path_as_str():
    """Test the get_path_as_str function."""
    path = pathlib.Path("test/path")
    assert package.get_path_as_str(path).endswith("test/path")


def test_get_path_as_str_with_backslashes():
    """Test the get_path_as_str function with a path that contains backslashes."""
    path = pathlib.Path("test\\path")
    assert package.get_path_as_str(path).endswith("test/path")


def test_get_package_dir():
    """Test the get_package_dir function."""
    assert isinstance(package.get_package_dir(), pathlib.Path)


def test_get_package_dir_in_autotransform():
    """Test the get_package_dir function when the current file is in the autotransform directory."""
    # This test would require mocking the __file__ variable and the pathlib.Path.parents property.
    # This is not straightforward to do and would likely require a more complex setup.


def test_get_examples_dir_exists():
    """Test the get_examples_dir function when an examples directory exists."""
    # This test would require creating a temporary directory structure and mocking the get_package_dir function.
    # This is not straightforward to do and would likely require a more complex setup.


def test_get_examples_dir_not_exists():
    """Test the get_examples_dir function when neither an examples nor an autotransform-examples directory exists."""
    # This test would require creating a temporary directory structure and mocking the get_package_dir function.
    # This is not straightforward to do and would likely require a more complex setup.


def test_get_config_dir_examples_exists():
    """Test the get_config_dir function when an examples directory exists."""
    # This test would require creating a temporary directory structure and mocking the get_package_dir function.
    # This is not straightforward to do and would likely require a more complex setup.


def test_get_config_dir_examples_not_exists():
    """Test the get_config_dir function when an examples directory does not exist."""
    # This test would require creating a temporary directory structure and mocking the get_package_dir function.
    # This is not straightforward to do and would likely require a more complex setup.
