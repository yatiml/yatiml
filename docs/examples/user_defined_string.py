from collections import UserString
from typing import Any, Union
import yatiml


# Create document class
class TitleCaseString(UserString):
    def __init__(self, seq: Any) -> None:
        super().__init__(seq)
        if not self.data.istitle():
            raise ValueError('Invalid TitleCaseString \'{}\': Each word must'
                             ' start with a capital letter'.format(self.data))


class Submission:
    def __init__(self, name: str, age: Union[int, str],
                 town: TitleCaseString) -> None:
        self.name = name
        self.age = age
        self.town = town


# Create loader
load_submission = yatiml.load_function(Submission, TitleCaseString)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'town: Piedmont')
doc = load_submission(yaml_text)

print(type(doc))
print(doc.name)
print(doc.town)
