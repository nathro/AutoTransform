# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation of RequestAction."""

import os
from functools import cached_property
from typing import Any, ClassVar, Mapping

from pydantic import Field

from autotransform.change.base import Change
from autotransform.step.action.base import Action, ActionName
from autotransform.util.request import RequestHandler


class RequestAction(Action):
    """Performs a URL request for a Change. Used for interacting with REST APIs.

    Attributes:
        url(str): The URL to send a request to.
        data(optional, Mapping[str, Any]): Data to include in the request. Defaults to {}.
        headers(optional, Mapping[str, Any]): Headers to include in the request. Defaults to {}.
        log_response(optional, bool): Indicates whether to log the response using DebugEvent.
            Defaults to False.
        params(optional, Mapping[str, Any]): Params to include in the request. Defaults to {}.
        post(optional, bool): Whether to send the request as a POST. Defaults to True.
        name (ClassVar[ActionName]): The name of the component.
    """

    url: str

    data: Mapping[str, Any] = Field(default_factory=dict)
    headers: Mapping[str, Any] = Field(default_factory=dict)
    log_response: bool = False
    params: Mapping[str, Any] = Field(default_factory=dict)
    post: bool = True

    name: ClassVar[ActionName] = ActionName.REQUEST

    @cached_property
    def _handler(self) -> RequestHandler:
        """Gets the handler for requests.

        Returns:
            RequestHandler: The handler for requests.
        """

        return RequestHandler(
            url=self.url,
            data=self.data,
            headers=self.headers,
            params=self.params,
            log_response=self.log_response,
            post=self.post,
            constant_replacers={"env": lambda var: str(os.getenv(var) or "")},
        )

    def run(self, change: Change) -> bool:
        """Performs a REST API request for a Change.

        Args:
            change (Change): The Change to perform the request on.

        Returns:
            bool: Whether the request returned a non-error response.
        """

        response = self._handler.get_response(
            {"change": lambda name: str(getattr(change, name) or "")}
        )

        return response.ok
