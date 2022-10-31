# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT>
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

# @black_format

"""The implementation of Request based conditions."""

import os
from functools import cached_property
from typing import Any, ClassVar, List, Mapping, Optional, TypeVar

from pydantic import Field

from autotransform.change.base import Change
from autotransform.step.condition.base import ComparisonCondition, ConditionName
from autotransform.step.condition.comparison import ComparisonType
from autotransform.util.request import RequestHandler

T = TypeVar("T")


class RequestStrCondition(ComparisonCondition[str]):
    """Performs a URL request to get a check a condition on a Change. Used for interacting with
    REST APIs. Handles the basics of the condition.

    Attributes:
        comparison (ComparisonType): The type of comparison to perform.
        url(str): The URL to send a request to.
        value (str | List[str]): The value to compare against.
        data(optional, Mapping[str, Any]): Data to include in the request. Defaults to {}.
        headers(optional, Mapping[str, Any]): Headers to include in the request. Defaults to {}.
        log_response(optional, bool): Indicates whether to log the response using DebugEvent.
            Defaults to False.
        params(optional, Mapping[str, Any]): Params to include in the request. Defaults to {}.
        post(optional, bool): Whether to send the request as a POST. Defaults to True.
        response_field(optional, Optional[str]): The field containing the desired response value
            when using the response as JSON. If multiple levels are needed, they should be separated
            by //. 'foo//bar' as an example would get the field at response['foo']['bar']. If no
            response_field is provided the whole response as text is used. Defaults to None.
        name (ClassVar[ConditionName]): The name of the Component.
    """

    comparison: ComparisonType
    url: str
    value: str | List[str]

    data: Mapping[str, Any] = Field(default_factory=dict)
    headers: Mapping[str, Any] = Field(default_factory=dict)
    log_response: bool = False
    params: Mapping[str, Any] = Field(default_factory=dict)
    post: bool = True
    response_field: Optional[str] = None

    name: ClassVar[ConditionName] = ConditionName.REQUEST_STR

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

    def get_val_from_change(self, change: Change) -> str:
        """Gets the existing value to compare against from the Change.

        Args:
            change (Change): The Change the Condition is checking.

        Returns:
            str: The value from the Change to compare against.
        """

        response = self._handler.get_response(
            ({"change": lambda name: str(getattr(change, name) or "")})
        )

        if not self.response_field:
            return response.text

        result = response.json()
        for field_name in self.response_field.split("//"):
            result = result[field_name]

        return str(result)
