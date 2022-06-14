# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""Provides configuration to AutoTransform. By default this configuration is pulled from
config files. The configuration fetcher used can be overridden using the AUTO_TRANSFORM_CONFIG
environment variable. This can support different methods of configuration, such as environment
variables or a custom approach where the environment variable is set to
"{'class_name': <A ConfigFetcher Class>, 'module': <The module where the class is located>}".
"""


import importlib
import json
import os
from typing import Dict

from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.environment import EnvironmentConfigFetcher
from autotransform.config.fetcher import ConfigFetcher, ConfigFetcherName

fetcher_to_use = os.getenv("AUTO_TRANSFORM_CONFIG")

fetchers: Dict[str, ConfigFetcher] = {
    ConfigFetcherName.DEFAULT: DefaultConfigFetcher(),
    ConfigFetcherName.ENVIRONMENT: EnvironmentConfigFetcher(),
}

if fetcher_to_use is not None:
    if fetcher_to_use in fetchers:
        fetcher: ConfigFetcher = fetchers[fetcher_to_use]
    else:
        try:
            fetcher_info = json.loads(fetcher_to_use)
            module = importlib.import_module(fetcher_info["module"])
            fetcher = getattr(module, fetcher_info["class_name"]).from_data(
                fetcher_info.get("data", {})
            )
            assert isinstance(fetcher, ConfigFetcher)
        except Exception:  # pylint: disable=broad-except
            fetcher = DefaultConfigFetcher()
else:
    fetcher = DefaultConfigFetcher()

CONFIG = fetcher.get_config()
