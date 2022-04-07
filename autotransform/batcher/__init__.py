# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Batchers take filtered inputsource and separate that inputsource in to logical groupings
with associated metadata that can be acted on independently.

Note:
    When creating custom Batchers as part of deployment for your organization, best practice
    is to include them in a subpackage named: autotransform.<organization>.batcher
"""
