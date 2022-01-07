# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""Batchers take filtered input and separate that input in to logical groupings
with associated metadata that can be acted on independently.
When creating custom batchers as part of deployment for your organization, best practice
is to include them in a package named: autotransform.<organization>.batcher
"""
