from ruamel import yaml
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

    def yatiml_attributes(self) -> OrderedDict:
        return OrderedDict([
            ('name', self.__name),
            ('age', self.__age)])


# Create loader
class MyLoader(yatiml.Loader):
    pass

yatiml.add_to_loader(MyLoader, Submission)
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = yaml.load(yaml_text, Loader=MyLoader)
print(doc)
