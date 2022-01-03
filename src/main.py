from store.store import data_store
from input.factory import InputFactory
from input.type import InputType

def __main__():
    global data_store
    inp = InputFactory.get(InputType.DIRECTORY, {"path": "C:/repos/autotransform/src"})
    for file in inp.getFiles():
        print(file)
        
__main__()