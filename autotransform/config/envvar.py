# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A config fetcher that utilizes environment variables for storing config settings."""

import os
from typing import List, Optional

from autotransform.config.default import DefaultConfigFetcher
from autotransform.config.fetcher import ConfigFetcher


class EnvironmentVariableConfigFetcher(ConfigFetcher):
    """A ConfigFetcher that utilizes environment variables as configuration storage.
    Environment variable names are of the form AUTO_TRANSFORM_<SECTION>_<SETTING>, using
    the sections and settings from autotransform/config/sample_config.ini. The
    DefaultConfigFetcher will be used for fallbacks where environment variables are not
    present. Set AUTO_TRANSFORM_CONFIG_USE_FALLBACK to "False" if you do not want to use
    a fallback.

    Attributes:
        _default_config (Optional[DefaultConfigFetcher]): A fallback config fetcher when
            values are not present as environment variables.
    """

    _default_config: Optional[DefaultConfigFetcher]

    def __init__(self):
        use_fallback = bool(os.getenv("AUTO_TRANSFORM_CONFIG_USE_FALLBACK", "True"))
        self._default_config = DefaultConfigFetcher() if use_fallback else None

    def get_credentials_github_token(self) -> Optional[str]:
        """Fetch the github token from AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN.

        Returns:
            Optional[str]: The github token,
        """

        github_token = os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_TOKEN")
        if github_token is None and self._default_config is not None:
            github_token = self._default_config.get_credentials_github_token()
        return github_token

    def get_credentials_github_base_url(self) -> Optional[str]:
        """Fetch the github base URL from AUTO_TRANSFORM_CREDENTIALS_GITHUB_BASE_URL.

        Returns:
            Optional[str]: The github base URL.
        """

        github_base_url = os.getenv("AUTO_TRANSFORM_CREDENTIALS_GITHUB_BASE_URL")
        if github_base_url is None and self._default_config is not None:
            return self._default_config.get_credentials_github_base_url()
        return github_base_url

    def get_imports_components(self) -> List[str]:
        """The modules containing the custom components to use: see
        autotransform.thirdparty.components from AUTO_TRANSFORM_CREDENTIALS_IMPORTS_COMPONENTS.

        Returns:
            List[str]: A list of the modules containing custom components that are not part base
                AutoTransform.
        """

        module_list = os.getenv("AUTO_TRANSFORM_IMPORTS_COMPONENTS")
        if module_list is None and self._default_config is not None:
            return self._default_config.get_imports_components()
        if module_list is None or module_list == "":
            return []
        return [module.strip() for module in module_list.split(",")]

    def get_runner_local(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for local runs.

        Returns:
            str: The JSON encoded Runner component to use for local runs.
        """

        local_runner = os.getenv("AUTO_TRANSFORM_RUNNER_LOCAL")
        if local_runner is None and self._default_config is not None:
            return self._default_config.get_runner_local()
        return local_runner

    def get_runner_remote(self) -> Optional[str]:
        """Gets the JSON encoded Runner component to use for remote runs.

        Returns:
            str: The JSON encoded Runner component to use for remote runs.
        """

        remote_runner = os.getenv("AUTO_TRANSFORM_RUNNER_REMOTE")
        if remote_runner is None and self._default_config is not None:
            return self._default_config.get_runner_remote()
        return remote_runner
