# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides utility functions for traversing the overall package."""

import pathlib


def get_path_as_str(path: pathlib.Path) -> str:
    """Coverts a path to a string AutoTransform can use.

    Args:
        path (pathlib.Path): The path to convert.

    Returns:
        str: The path as a string.
    """

    return str(path.resolve()).replace("\\", "/")


def get_package_dir() -> pathlib.Path:
    """Gets the directory for the autotransform package

    Returns:
        pathlib.Path: The package's directory.
    """

    path = pathlib.Path(__file__).resolve()
    while path.name != "autotransform":
        path = path.parent
    return path.parent


def get_examples_dir() -> str:
    """Gets the directory where examples are located.

    Returns:
        str: The examples directory
    """

    package_dir = get_package_dir()
    examples_dir = package_dir / "examples"
    if not examples_dir.exists():
        examples_dir = package_dir / "autotransform-examples"
    if not examples_dir.exists():
        raise FileNotFoundError()
    return get_path_as_str(examples_dir)


def get_config_dir() -> str:
    """Gets the directory where the configuration is stored.

    Returns:
        str: The directory where configuration is stored.
    """
    package_dir = get_package_dir()
    config_dir = "config" if (package_dir / "examples").exists() else "autotransform-config"
    return get_path_as_str(package_dir / config_dir)
