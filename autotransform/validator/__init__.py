# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Validators take in a batch that has undergone transformation and validate that the
changes do not produce any issues/errors. They may run test cases or check some linting
or type checking software

Note:
    When creating custom Validators as part of deployment for your organization, best practice
    is to include them in a subpackage named: autotransform.<organization>.validator
"""
