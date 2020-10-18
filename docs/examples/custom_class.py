from typing import Union
import yatiml


# Create document class
class Submission:
    def __init__(self, name: str, age: Union[int, str]) -> None:
        self.name = name
        self.age = age

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
