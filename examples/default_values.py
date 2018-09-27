from ruamel import yaml
from typing import Union
import yatiml


# Create document class
class Submission:
    def __init__(
            self,
            name: str,
            age: Union[int, str],
            tool: str='crayons'
            ) -> None:
        self.name = name
        self.age = age
        self.tool = tool


# Create loader
class MyLoader(yatiml.Loader):
  pass

yatiml.add_to_loader(MyLoader, Submission)
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(doc.name)
print(doc.age)
print(doc.tool)
