# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

"""An example module containing custom imports. Used via the custom_components config setting.
All custom component imports should follow this structure."""

from typing import Any, Callable, Dict, Mapping

from autotransform.batcher.base import Batcher

BATCHERS: Dict[str, Callable[[Mapping[str, Any]], Batcher]] = {}
