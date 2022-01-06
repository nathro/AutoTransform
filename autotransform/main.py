# AutoTransform
# Large scale, component based code modification library
#
# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from autotransform.batcher.single import SingleBatcher
from autotransform.common.package import AutoTransformPackage
from autotransform.filter.extension import ExtensionFilter, Extensions
from autotransform.input.directory import DirectoryInput
from autotransform.transformer.regex import RegexTransformer

if __name__ == "__main__":
    inp = DirectoryInput({"path": "C:/repos/autotransform/src"})
    f = ExtensionFilter({"extensions": [Extensions.TEXT]})
    batcher = SingleBatcher(
        {"metadata": {"title": "Just a test", "summary": "This is just a test", "tests": "This?"}}
    )
    transformer = RegexTransformer({"pattern": r"test", "replacement": "foo"})
    package = AutoTransformPackage(inp, batcher, transformer, filters=[f])
    json_package = package.to_json()
    package = AutoTransformPackage.from_json(json_package)
    package.run()
