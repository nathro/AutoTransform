from common.package import AutoTransformPackage
from common.store import data_store
from filter.extension import Extensions
from filter.factory import FilterFactory
from filter.type import FilterType
from input.factory import InputFactory
from input.type import InputType

if __name__ == "__main__":
    inp = InputFactory.get(InputType.DIRECTORY, {"path": "C:/repos/autotransform/src"})
    filter = FilterFactory.get(FilterType.EXTENSION, {"extensions": [Extensions.PYTHON]})
    package = AutoTransformPackage(inp, [filter])
    json_package = package.to_json()
    print(json_package)
    package = AutoTransformPackage.from_json(json_package)
    input = package.input
    filter = package.filters[0]
    for file in input.get_files():
        if filter.is_valid(file):
            print(file)