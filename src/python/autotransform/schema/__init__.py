# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Schemas are the heart of AutoTransform. They contain all necessary components and configuration
to deploy a change.
"""

from typing import Optional

# A variable to store the currently executing schema so that components can access it without
# having to thread it.
current: Optional["AutoTransformSchema"] = None

# The import statement is moved to the end to avoid circular imports
from autotransform.schema.schema import AutoTransformSchema
