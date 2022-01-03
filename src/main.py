from store.store import data_store
from input.factory import InputFactory
from input.type import InputType

if __name__ == "__main__":
    inp = InputFactory.get(InputType.DIRECTORY, {"path": "C:/repos/autotransform/src"})
    for file in inp.get_files():
        print(file)