# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides configuration to AutoTransform. By default this configuration is pulled from
data/config.ini (see data/sample_config.ini). The configuration fetcher used can be overridden
using the AUTO_TRANSFORM_CONFIG environment variable. This can support different methods of
configuration, such as console input or environment variables.
"""


import os
from typing import Dict, Type

from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.envvar import EnvironmentVariableConfigFetcher
from autotransform.config.fetcher import ConfigFetcher

fetcher_to_use = os.getenv("AUTO_TRANSFORM_CONFIG")

fetchers: Dict[str, Type[ConfigFetcher]] = {
    "default": DefaultConfigFetcher,
    "environment": EnvironmentVariableConfigFetcher,
}

if fetcher_to_use is not None:
    fetcher: ConfigFetcher = fetchers.get(fetcher_to_use, DefaultConfigFetcher)()
else:
    fetcher = DefaultConfigFetcher()
