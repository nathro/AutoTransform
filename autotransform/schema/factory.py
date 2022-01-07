# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from typing import Dict

from autotransform.schema.builder import SchemaBuilder
from autotransform.schema.name import SchemaBuilderName

# Section reserved for custom imports to reduce merge conflicts
# BEGIN CUSTOM IMPORTS
# END CUSTOM IMPORTS


class SchemaBuilderFactory:
    # pylint: disable=too-few-public-methods

    _schemas: Dict[SchemaBuilderName, SchemaBuilder] = {
        # Section reserved for custom schemas to reduce merge conflicts
        # BEGIN CUSTOM SCHEMA
        # END CUSTOM SCHEMA
    }

    @staticmethod
    def get(schema: SchemaBuilderName) -> SchemaBuilder:
        return SchemaBuilderFactory._schemas[schema]
