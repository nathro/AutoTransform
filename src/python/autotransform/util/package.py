# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides utility functions for traversing the overall package."""

import pathlib


def get_package_dir() -> str:
    """Gets the top level directory where the package is installed
    (the directory that contains src/).

    Returns:
        str: The package's directory.
    """

    path = pathlib.Path(__file__)
    # File is located in {package_dir}/src/python/autotransform/util/
    # Need to go up parent 5 times
    for _ in range(5):
        path = path.parent
    return str(path.resolve()).replace("\\", "/")


def get_examples_dir() -> str:
    """Gets the directory where examples are located.

    Returns:
        str: The examples directory
    """

    return f"{get_package_dir()}/examples"


def get_config_dir() -> str:
    """Gets the directory where the configuration is stored.

    Returns:
        str: The directory where configuration is stored.
    """

    return f"{get_package_dir()}/config"
