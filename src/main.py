import json

from common.cachedfile import CachedFile
from common.package import AutoTransformPackage
from common.datastore import data_store
from batcher.single import SingleBatcher
from filter.extension import Extensions, ExtensionFilter
from input.directory import DirectoryInput

if __name__ == "__main__":
    inp = DirectoryInput({"path": "C:/repos/autotransform/src"})
    filter = ExtensionFilter({"extensions": [Extensions.PYTHON]})
    batcher = SingleBatcher({})
    package = AutoTransformPackage(inp, [filter], batcher)
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
    batches = [{"files": [valid_files[file].path for file in batch["files"]], "metadata": batch["metadata"]} for batch in batches]
    print(json.dumps(batches, indent=4))
    print(package.to_json(pretty = True))