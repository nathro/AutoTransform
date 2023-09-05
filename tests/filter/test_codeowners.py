# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

from autotransform.filter.codeowners import CodeownersFilter
from autotransform.filter.base import FilterName


def test_initialization():
    """Test if the CodeownersFilter class is correctly initialized."""
    codeowners_filter = CodeownersFilter(codeowners_location="location", owner="owner")
    assert codeowners_filter.codeowners_location == "location"
    assert codeowners_filter.owner == "owner"


def test_owners_property():
    """Test if the _owners property correctly parses the CodeOwners file."""
    # This test would require a mock CodeOwners file and a mock CodeOwners object


def test_formatted_owner_property():
    """Test if the _formatted_owner property correctly formats the owner attribute."""
    codeowners_filter = CodeownersFilter(codeowners_location="location", owner="@owner")
    assert codeowners_filter._formatted_owner == "owner"


def test_is_valid():
    """Test if the _is_valid method correctly identifies a file that is owned by the supplied owner."""
    # This test would require a mock Item object and a mock CodeOwners object


def test_is_valid_unowned():
    """Test if the _is_valid method correctly identifies a file that is unowned when no owner is supplied."""
    # This test would require a mock Item object and a mock CodeOwners object


def test_is_valid_not_file():
    """Test if the _is_valid method correctly returns False when the item is not a file."""
    # This test would require a mock Item object that is not a FileItem


def test_is_valid_not_owned():
    """Test if the _is_valid method correctly returns False when the file is not owned by the supplied owner."""
    # This test would require a mock Item object and a mock CodeOwners object


def test_is_valid_owned_no_owner():
    """Test if the _is_valid method correctly returns False when the file is owned and no owner is supplied."""
    # This test would require a mock Item object and a mock CodeOwners object


def test_name():
    """Test if the name class variable is correctly set to FilterName.CODEOWNERS."""
    assert CodeownersFilter.name == FilterName.CODEOWNERS
