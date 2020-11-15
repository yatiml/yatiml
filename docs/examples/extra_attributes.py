from collections import OrderedDict
from typing import Union
import yatiml


# Create document class
class Submission:
    def __init__(
            self,
            name: str,
            age: int,
            _yatiml_extra: OrderedDict
            ) -> None:
        self.name = name
        self.age = age
        self._yatiml_extra = _yatiml_extra


# Create loader
load = yatiml.load_function(Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'tool: crayons\n')
doc = load(yaml_text)

print(doc.name)
print(doc.age)
print(doc._yatiml_extra['tool'])
