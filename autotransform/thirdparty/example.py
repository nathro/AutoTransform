# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An example module containing custom imports. Used via the custom_components config setting.
All custom component imports should follow this structure. Component types that do not have any
custom implementations do not need to be included (i.e. if there are no custom batchers, the
BATCHERS variable can be left out."""

from typing import Any, Callable, Dict, Mapping, Type

from autotransform.batcher.base import Batcher
from autotransform.command.base import Command
from autotransform.filter.base import Filter
from autotransform.inputsource.base import Input
from autotransform.remote.base import Remote
from autotransform.schema.builder import SchemaBuilder
from autotransform.transformer.base import Transformer
from autotransform.validator.base import Validator
from autotransform.worker.base import Worker

BATCHERS: Dict[str, Callable[[Mapping[str, Any]], Batcher]] = {}
COMMANDS: Dict[str, Callable[[Mapping[str, Any]], Command]] = {}
FILTERS: Dict[str, Callable[[bool, Mapping[str, Any]], Filter]] = {}
INPUTS: Dict[str, Callable[[Mapping[str, Any]], Input]] = {}
SCHEMAS: Dict[str, Type[SchemaBuilder]] = {}
TRANSFORMERS: Dict[str, Callable[[Mapping[str, Any]], Transformer]] = {}
VALIDATORS: Dict[str, Callable[[Mapping[str, Any]], Validator]] = {}
WORKERS: Dict[str, Type[Worker]] = {}
REMOTES: Dict[str, Callable[[Mapping[str, Any]], Remote]]
