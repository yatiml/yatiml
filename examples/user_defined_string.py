from collections import UserString
from ruamel import yaml
from typing import Any, Union
import yatiml


# Create document class
class TitleCaseString(UserString):
    def __init__(self, seq: Any) -> None:
        super().__init__(seq)
        if self.data != self.data.title():
            raise ValueError('Invalid TitleCaseString \'{}\': Each word must'
                             ' start with a capital letter'.format(self.data))


class Submission:
    def __init__(self, name: str, age: Union[int, str],
                 town: TitleCaseString) -> None:
        self.name = name
        self.age = age
        self.town = town


# Create loader
class MyLoader(yatiml.Loader):
    pass

yatiml.add_to_loader(MyLoader, [TitleCaseString, Submission])
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'town: Piedmont')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(type(doc))
print(doc.name)
print(doc.town)
