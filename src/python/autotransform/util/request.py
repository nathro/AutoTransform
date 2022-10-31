# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""A utility for performing REST API requests."""

import json
import re
from functools import cached_property
from typing import Any, Callable, Dict, Mapping

import requests
from pydantic import BaseModel, Field  # pylint: disable=no-name-in-module

from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler


class RequestHandler(BaseModel):
    """Performs REST API requests, replacing values with things like environment variables

    Attributes:
        url(str): The URL to send a request to.
        constant_ replacers (optional, Mapping[str, Callable[[str], str]]): The replacers
            to apply to all usages of this handler. Defaults to {}.
        data(optional, Mapping[str, Any]): Data to include in the request. Defaults to {}.
        headers(optional, Mapping[str, Any]): Headers to include in the request. Defaults to {}.
        log_response(optional, bool): Indicates whether to log the response using DebugEvent.
            Defaults to False.
        params(optional, Mapping[str, Any]): Params to include in the request. Defaults to {}.
        post(optional, bool): Whether to send the request as a POST. Defaults to True.
    """

    url: str

    constant_replacers: Mapping[str, Callable[[str], str]] = Field(default_factory=dict)
    data: Mapping[str, Any] = Field(default_factory=dict)
    headers: Mapping[str, Any] = Field(default_factory=dict)
    log_response: bool = False
    params: Mapping[str, Any] = Field(default_factory=dict)
    post: bool = True

    @cached_property
    def _headers(self) -> Dict[str, Any]:
        """Gets the headers with any constant replacers filled in.

        Returns:
            Dict[str, Any]: The headers with constant replacers filled in.
        """

        headers = dict(self.headers)
        for name, replacer in self.constant_replacers.items():
            headers = self.replace_values(headers, name, replacer)

        return headers

    @cached_property
    def _params(self) -> Dict[str, Any]:
        """Gets the params with any constant replacers filled in.

        Returns:
            Dict[str, Any]: The params with constant replacers filled in.
        """

        params = dict(self.params)
        for name, replacer in self.constant_replacers.items():
            params = self.replace_values(params, name, replacer)

        return params

    @cached_property
    def _data(self) -> Dict[str, Any]:
        """Gets the data with any constant replacers filled in.

        Returns:
            Dict[str, Any]: The data with constant replacers filled in.
        """

        data = dict(self.data)
        for name, replacer in self.constant_replacers.items():
            data = self.replace_values(data, name, replacer)

        return data

    @staticmethod
    def replace_values(
        data: Mapping[str, Any], identifier: str, replacer: Callable[[str], str]
    ) -> Dict[str, Any]:
        """Replaces values in a dictionary with values from a replacing function.

        Args:
            data (Mapping[str, Any]): The data to replace values for.
            identifier (str): The identifier of the type of value.
            replacer (Callable[[str], Any]): The replacing function.

        Returns:
            Dict[str, Any]: The replaced data.
        """

        replaced_data: Dict[str, Any] = {}
        for name, val in data.items():
            if isinstance(val, str):
                match = re.match(f"<{identifier}:([^>]+)>", val)
                if match is not None:
                    tmp_val = val
                    for group in match.groups():
                        tmp_val = re.sub(f"<{identifier}:{group}>", replacer(group), tmp_val)
                    replaced_data[name] = tmp_val
                    continue
            elif isinstance(val, Mapping):
                replaced_data[name] = RequestHandler.replace_values(val, identifier, replacer)
                continue
            replaced_data[name] = val

        return replaced_data

    def get_response(self, replacers: Dict[str, Callable[[str], str]]) -> requests.Response:
        """Gets the value from a REST API request.

        Args:
            replacers (Dict[str, Callable[[str], str]]): The replacers to use for the request.

        Returns:
            requests.Response: The response to the request.
        """

        event_handler = EventHandler.get()

        headers = self._headers
        params = self._params
        data = self._data
        for name, replacer in replacers.items():
            headers = self.replace_values(headers, name, replacer)
            params = self.replace_values(params, name, replacer)
            data = self.replace_values(data, name, replacer)

        if self.post:
            response = requests.post(
                self.url, headers=headers, params=params, data=json.dumps(data), timeout=120
            )
        else:
            response = requests.get(
                self.url, headers=headers, params=params, data=json.dumps(data), timeout=120
            )

        if self.log_response:
            try:
                message = json.dumps(response.json(), indent=4)
            # pylint: disable=broad-except
            except Exception:
                message = str(response.content, encoding=response.apparent_encoding)

            event_handler.handle(DebugEvent({"message": f"Response:\n{message}"}))

        return response
