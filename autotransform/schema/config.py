# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>


from __future__ import annotations

from typing import Any, Dict

from autotransform.validator.base import ValidationResultLevel


class Config:
    allowed_validation_level: ValidationResultLevel

    def __init__(
        self, allowed_validation_level: ValidationResultLevel = ValidationResultLevel.NONE
    ):
        self.allowed_validation_level = allowed_validation_level

    def bundle(self):
        return {
            "allowed_validation_level": self.allowed_validation_level,
        }

    @classmethod
    def from_data(cls, data: Dict[str, Any]) -> Config:
        if "allowed_validation_level" in data:
            validation_level = data["allowed_validation_level"]
            if not ValidationResultLevel.has_value(validation_level):
                validation_level = ValidationResultLevel.from_name(validation_level)
        else:
            validation_level = ValidationResultLevel.NONE
        return cls(validation_level)
