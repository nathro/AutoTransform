from common.store import data_store
from filter.extension import Extensions
from filter.factory import FilterFactory
from filter.type import FilterType
from input.factory import InputFactory
from input.type import InputType

if __name__ == "__main__":
    inp = InputFactory.get(InputType.DIRECTORY, {"path": "C:/repos/autotransform/src"})
    filter = FilterFactory.get(FilterType.EXTENSION, {"extensions": [Extensions.PYTHON]})
    for file in inp.get_files():
        if filter.is_valid(file):
            print(file)