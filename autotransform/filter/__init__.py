# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Filters take inputsource files and check that they pass some criteria. Filters should be named
based on what they use to validate a file and should follow an allowlist approach, using the
invert() function to blocklist.

Note:
    When creating custom Filters as part of deployment for your organization, best practice
    is to include them in a subpackage named: autotransform.<organization>.filter
"""
