from dataclasses import dataclass
from typing import Union
import yatiml


# Create document class
@dataclass
class Submission:
    name: str
    age: Union[int, str]

# Create loader
load = yatiml.load_function(Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = load(yaml_text)

print(type(doc))
print(doc.name)
print(doc.age)
print(type(doc.age))
