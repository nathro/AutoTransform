# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Conditions from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

import autotransform.step.condition.type as condition_type
from autotransform.config import fetcher as Config
from autotransform.step.condition import aggregate, base, created, schema, state, updated


class ConditionFactory:
    """The factory class for Conditions. Maps a type to a Condition.

    Attributes:
        _map (Dict[condition_type.ConditionType, Callable[[Mapping[str, Any]], base.Condition]]):
            A mapping from ConditionType to the from_data function of the appropriate Condition.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[condition_type.ConditionType, Callable[[Mapping[str, Any]], base.Condition]] = {
        condition_type.ConditionType.AGGREGATE: aggregate.AggregateCondition.from_data,
        condition_type.ConditionType.CHANGE_STATE: state.ChangeStateCondition.from_data,
        condition_type.ConditionType.CREATED_AGO: created.CreatedAgoCondition.from_data,
        condition_type.ConditionType.SCHEMA_NAME: schema.SchemaNameCondition.from_data,
        condition_type.ConditionType.UPDATED_AGO: updated.UpdatedAgoCondition.from_data,
    }

    @staticmethod
    def get(bundle: base.ConditionBundle) -> base.Condition:
        """Simple get method using the _map attribute.

        Args:
            bundle (ConditionBundle): The bundled Condition type and params.

        Returns:
            Condition: An instance of the associated Condition.
        """

        if bundle["type"] in ConditionFactory._map:
            return ConditionFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "CONDITIONS") and bundle["type"] in module.CONDITIONS:
                return module.CONDITIONS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Condition found for type {bundle['type']}")
