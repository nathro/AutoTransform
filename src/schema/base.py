from abc import ABC, abstractmethod
from typing import List, Optional

from batcher.base import Batcher
from batcher.single import SingleBatcher
from command.base import Command
from common.package import AutoTransformPackage, PackageConfiguration
from filter.base import Filter
from input.base import Input
from repo.base import Repo
from transformer.base import Transformer
from validator.base import Validator

class AutoTransformSchema(ABC):
    
    @abstractmethod
    def get_input(self) -> Input:
        pass
    
    def get_filters(self) -> List[Filter]:
        return []
    
    def get_batcher(self) -> Batcher:
        return SingleBatcher({"message": ""})
    
    @abstractmethod
    def get_transformer(self) -> Transformer:
        pass
    
    def get_validators(self) -> List[Validator]:
        return []
    
    def get_commands(self) -> List[Command]:
        return []
    
    def get_repo(self) -> Optional[Repo]:
        return None
    
    def get_config(self) -> PackageConfiguration:
        return PackageConfiguration()
    
    def get_package(self):
        return AutoTransformPackage(
            self.get_input(),
            self.get_batcher(),
            self.get_batcher(),
            filters = self.get_filters(),
            validators = self.get_validators(),
            commands = self.get_commands(),
            repo = self.get_repo(),
            config = self.get_config(),
        )
        
    def dump_to_file(self, file: str):
        f = open(file, "w")
        f.write(self.get_package().to_json(pretty = True))
        f.close()