# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation of RequestAction."""

import json
import os
import re
from functools import cached_property
from typing import Any, Callable, ClassVar, Dict, Mapping

import requests
from pydantic import Field

from autotransform.change.base import Change
from autotransform.event.debug import DebugEvent
from autotransform.event.handler import EventHandler
from autotransform.step.action.base import Action, ActionName


class RequestAction(Action):
    """Performs a URL request for a Change. Used for interacting with REST APIs.

    Attributes:
        url(str): The URL to send a request to.
        data(optional, Mapping[str, Any]): Data to include in the request. Defaults to {}.
        headers(optional, Mapping[str, Any]): Headers to include in the request. Defaults to {}.
        log_request(optional, bool): Indicates whether to log the request using DebugEvent.
            Defaults to False.
        log_response(optional, bool): Indicates whether to log the response using DebugEvent.
            Defaults to False.
        params(optional, Mapping[str, Any]): Params to include in the request. Defaults to {}.
        post(optional, bool): Whether to send the request as a POST. Defaults to True.
        name (ClassVar[ActionName]): The name of the component.
    """

    url: str

    data: Mapping[str, Any] = Field(default_factory=dict)
    headers: Mapping[str, Any] = Field(default_factory=dict)
    log_request: bool = False
    log_response: bool = False
    params: Mapping[str, Any] = Field(default_factory=dict)
    post: bool = True

    name: ClassVar[ActionName] = ActionName.REQUEST

    @cached_property
    def _headers(self) -> Dict[str, Any]:
        """Gets the headers with any environment variables filled in.

        Returns:
            Dict[str, Any]: The headers with environment variables filled in.
        """

        return self.replace_values(self.headers, "env", os.getenv)

    @cached_property
    def _params(self) -> Dict[str, Any]:
        """Gets the params with any environment variables filled in.

        Returns:
            Dict[str, Any]: The params with environment variables filled in.
        """

        return self.replace_values(self.params, "env", os.getenv)

    @cached_property
    def _data(self) -> Dict[str, Any]:
        """Gets the data with any environment variables filled in.

        Returns:
            Dict[str, Any]: The data with environment variables filled in.
        """

        return self.replace_values(self.data, "env", os.getenv)

    @staticmethod
    def replace_values(
        data: Mapping[str, Any], identifier: str, replacer: Callable[[str], Any]
    ) -> Dict[str, Any]:
        """Replaces values in a dictionary with values from a replacing function.

        Args:
            data (Mapping[str, Any]): The data to replace values for.
            identifier (str): The identifier of the type of value.
            replacer (Callable[[str], Any]): The replacing function.

        Returns:
            Dict[str, Any]: The replaced data.
        """

        replaced_data = {}
        for name, val in data.items():
            if isinstance(val, str):
                match = re.match(f"<{identifier}:([^>]+)>", val)
                if match is not None:
                    tmp_val = val
                    for group in match.groups():
                        tmp_val = re.sub(f"<{identifier}:{group}>", replacer(group), tmp_val)
                    replaced_data[name] = tmp_val
                    continue
            replaced_data[name] = val

        return replaced_data

    def run(self, change: Change) -> bool:
        """Adds a comment to the specified Change.

        Args:
            change (Change): The Change to comment on.

        Returns:
            bool: Whether the comment was successful.
        """

        event_handler = EventHandler.get()

        headers = self.replace_values(self._headers, "change", lambda name: getattr(change, name))
        params = self.replace_values(self._params, "change", lambda name: getattr(change, name))
        data = self.replace_values(self._data, "change", lambda name: getattr(change, name))

        if self.log_request:
            event_handler.handle(
                DebugEvent(
                    {
                        "message": f"Requesting URL {self.url}"
                        + f"\nParams:\n{json.dumps(params, indent=4)}"
                        + f"\nHeaders:\n{json.dumps(headers, indent=4)}"
                        + f"\nData:\n{json.dumps(data, indent=4)}"
                    }
                )
            )

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

        return response.ok
