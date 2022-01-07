# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>


import os
from typing import Dict, Type

from autotransform.config.console import ConsoleConfigFetcher
from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.fetcher import ConfigFetcher

fetcher_to_use = os.getenv("AUTO_TRANSFORM_CONFIG")

fetchers: Dict[str, Type[ConfigFetcher]] = {
    "console": ConsoleConfigFetcher,
    "default": DefaultConfigFetcher,
}

if fetcher_to_use is not None:
    fetcher: ConfigFetcher = fetchers.get(fetcher_to_use, DefaultConfigFetcher)()
else:
    fetcher = DefaultConfigFetcher()
