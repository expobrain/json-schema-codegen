from typing import Dict, List, NewType


DefinitionType = NewType("DefinitionType", Dict)
PropertyType = NewType("PropertyType", Dict)
PropertiesType = NewType("PropertiesType", List[PropertyType])
RequiredType = NewType("RequiredType", List[str])
