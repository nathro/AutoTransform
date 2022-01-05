from typing import Dict

from schema.base import AutoTransformSchema
from schema.name import SchemaName

class SchemaFactory:
    _schemas: Dict[SchemaName, AutoTransformSchema] = {
    }
    
    @staticmethod
    def get(schema: SchemaName) -> AutoTransformSchema:
        return SchemaFactory._schemas[schema]