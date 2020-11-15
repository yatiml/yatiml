from collections import OrderedDict
from typing import Union
import yatiml


# Create document class
class Submission:
    def __init__(self, name: str, age: Union[int, str]) -> None:
        self.__name = name
        self.__age = age

    def __str__(self) -> str:
        return '{}\n{}'.format(self.__name, self.__age)

    def _yatiml_attributes(self) -> OrderedDict:
        return OrderedDict([
            ('name', self.__name),
            ('age', self.__age)])


# Create loader
load = yatiml.load_function(Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = load(yaml_text)
print(doc)
