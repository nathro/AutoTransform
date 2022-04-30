# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Steps from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.step.base import Step, StepBundle
from autotransform.step.conditional import ConditionalStep
from autotransform.step.type import StepType


class StepFactory:
    """The factory class for Steps. Maps a type to a Step.

    Attributes:
        _map (Dict[StepType, Callable[[Mapping[str, Any]], Step]]): A mapping from
            StepType to the from_data function of the appropriate Step.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[StepType, Callable[[Mapping[str, Any]], Step]] = {
        StepType.CONDITIONAL: ConditionalStep.from_data,
    }

    @staticmethod
    def get(bundle: StepBundle) -> Step:
        """Simple get method using the _map attribute.

        Args:
            bundle (StepBundle): The bundled Step type and params.

        Returns:
            Step: An instance of the associated Step.
        """

        if bundle["type"] in StepFactory._map:
            return StepFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "STEPS") and bundle["type"] in module.STEPS:
                return module.STEPS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Step found for type {bundle['type']}")
