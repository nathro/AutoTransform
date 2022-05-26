# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Inputs produce a list of Items that are used to make changes to the codebase.
These Items can represent anything and only need to be understood by the components of the Schema.
Most use cases will return FileItems.
"""
