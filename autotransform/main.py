#    _____          __       ___________                              _____                     
#   /  _  \  __ ___/  |_  ___\__    ___/___________    ____   _______/ ____\___________  _____  
#  /  /_\  \|  |  \   __\/  _ \|    |  \_  __ \__  \  /    \ /  ___/\   __\/  _ \_  __ \/     \ 
# /    |    \  |  /|  | (  <_> )    |   |  | \// __ \|   |  \\___ \  |  | (  <_> )  | \/  Y Y  \
# \____|__  /____/ |__|  \____/|____|   |__|  (____  /___|  /____  > |__|  \____/|__|  |__|_|  /
#         \/                                       \/     \/     \/                          \/ 

# Licensed under the MIT License <http://opensource.org/licenses/MIT
# SPDX-License-Identifier: MIT
# Copyright (c) 2022-present Nathan Rockenbach <http://github.com/nathro>

from batcher.single import SingleBatcher
from common.cachedfile import CachedFile
from common.package import AutoTransformPackage
from common.datastore import data_store
from filter.extension import Extensions, ExtensionFilter
from input.directory import DirectoryInput
from transformer.regex import RegexTransformer

if __name__ == "__main__":
    inp = DirectoryInput({"path": "C:/repos/autotransform/src"})
    filter = ExtensionFilter({"extensions": [Extensions.TEXT]})
    batcher = SingleBatcher({"metadata": {"title": "Just a test", "summary": "This is just a test", "tests": "This?"}})
    transformer = RegexTransformer({"pattern": r"test", "replacement": "foo"})
    package = AutoTransformPackage(inp, batcher, transformer, filters=[filter])
    json_package = package.to_json()
    package = AutoTransformPackage.from_json(json_package)
    input = package.input
    valid_files = []
    for file in input.get_files():
        f = CachedFile(file)
        is_valid = True
        for filter in package.filters:
            if not filter.is_valid(f):
                is_valid = False
                break
        if is_valid:
            valid_files.append(f)
    batches = package.batcher.batch(valid_files)
    batches = [{"files": [valid_files[file] for file in batch["files"]], "metadata": batch["metadata"]} for batch in batches]
    for batch in batches:
        for file in batch["files"]:
            package.transformer.transform(file)