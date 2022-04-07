# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Transformers are the core functionality of a change. They take in the filtered files and execute
the changes to the codebase. Transformers can also modify additional files as necesary to support
the changes made to the inputsource files (i.e. as part of a rename)

Note:
    When creating custom Transformers as part of deployment for your organization, best practice
    is to include them in a subpackage named: autotransform.<organization>.transformer
"""
