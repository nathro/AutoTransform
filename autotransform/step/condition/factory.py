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

import autotransform.step.condition.aggregate as aggregate_condition
from autotransform.config import fetcher as Config
from autotransform.step.condition.base import Condition, ConditionBundle
from autotransform.step.condition.created import CreatedAgoCondition
from autotransform.step.condition.schema import SchemaNameCondition
from autotransform.step.condition.state import ChangeStateCondition
from autotransform.step.condition.type import ConditionType
from autotransform.step.condition.updated import UpdatedAgoCondition


class ConditionFactory:
    """The factory class for Conditions. Maps a type to a Condition.

    Attributes:
        _map (Dict[ConditionType, Callable[[Mapping[str, Any]], Condition]]): A mapping from
            ConditionType to the from_data function of the appropriate Condition.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[ConditionType, Callable[[Mapping[str, Any]], Condition]] = {
        ConditionType.AGGREGATE: aggregate_condition.AggregateCondition.from_data,
        ConditionType.CHANGE_STATE: ChangeStateCondition.from_data,
        ConditionType.CREATED_AGO: CreatedAgoCondition.from_data,
        ConditionType.SCHEMA_NAME: SchemaNameCondition.from_data,
        ConditionType.UPDATED_AGO: UpdatedAgoCondition.from_data,
    }

    @staticmethod
    def get(bundle: ConditionBundle) -> Condition:
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
