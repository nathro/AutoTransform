from common.FileDataStore import data_store
from input.DirectoryInput import DirectoryInput, DirectoryInputParams

def __main__():
    global data_store
    inp = DirectoryInput(DirectoryInputParams("C:/repos/autotransform/src"))
    for file in inp.getInput():
        print(file)
        
__main__()