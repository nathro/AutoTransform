# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A simple factory for producing Runners from type and param information."""

import importlib
from typing import Any, Callable, Dict, Mapping

from autotransform.config import fetcher as Config
from autotransform.runner.base import Runner, RunnerBundle
from autotransform.runner.github import GithubRunner
from autotransform.runner.local import LocalRunner
from autotransform.runner.type import RunnerType


class RunnerFactory:
    """The factory class for Runners. Maps a type to a Runner.

    Attributes:
        _map (Dict[RunnerType, Callable[[Mapping[str, Any]], Runner]]): A mapping from
            RunnerType to the from_data function of the appropriate Runner.
    """

    # pylint: disable=too-few-public-methods

    _map: Dict[RunnerType, Callable[[Mapping[str, Any]], Runner]] = {
        RunnerType.GITHUB: GithubRunner.from_data,
        RunnerType.LOCAL: LocalRunner.from_data,
    }

    @staticmethod
    def get(bundle: RunnerBundle) -> Runner:
        """Simple get method using the _map attribute.

        Args:
            bundle (RunnerBundle): The bundled Runner type and params.

        Returns:
            Runner: An instance of the associated Runner.
        """

        if bundle["type"] in RunnerFactory._map:
            return RunnerFactory._map[bundle["type"]](bundle["params"])

        custom_component_modules = Config.get_imports_components()
        for module_string in custom_component_modules:
            module = importlib.import_module(module_string)
            if hasattr(module, "RUNNERS") and bundle["type"] in module.RUNNERS:
                return module.RUNNERS[bundle["type"]](bundle["params"])
        raise ValueError(f"No Runner found for type {bundle['type']}")
