# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Dict

from autotransform.schema.base import AutoTransformSchema
from autotransform.schema.name import SchemaName


class SchemaFactory:
    _schemas: Dict[SchemaName, AutoTransformSchema] = {}

    @staticmethod
    def get(schema: SchemaName) -> AutoTransformSchema:
        return SchemaFactory._schemas[schema]
