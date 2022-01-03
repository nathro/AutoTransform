from common.FileDataStore import data_store
from input.InputFactory import InputFactory
from input.InputType import InputType

def __main__():
    global data_store
    inp = InputFactory.get(InputType.DIRECTORY, {"path": "C:/repos/autotransform/src"})
    for file in inp.getFiles():
        print(file)
        
__main__()