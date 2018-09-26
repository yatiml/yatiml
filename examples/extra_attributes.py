from ruamel import yaml
from collections import OrderedDict
from typing import Optional, Union
import yatiml
import logging


# Create document class
class Submission:
    def __init__(
            self,
            name: str,
            age: int,
            yatiml_extra: OrderedDict
            ) -> None:
        self.name = name
        self.age = age
        self.yatiml_extra = yatiml_extra


# Create loader
class MyLoader(yatiml.Loader):
    pass

yatiml.add_to_loader(MyLoader, Submission)
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'tool: crayons\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(doc.name)
print(doc.age)
print(doc.yatiml_extra['tool'])
