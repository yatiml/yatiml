from ruamel import yaml
from typing import Optional, Union
import yatiml


# Create document class
class Submission:
    def __init__(
            self,
            name: str,
            age: Union[int, str],
            tool: Optional[str]=None
            ) -> None:
        self.name = name
        self.age = age
        self.tool = tool

    @classmethod
    def yatiml_savorize(cls, node: yatiml.ClassNode) -> None:
        str_to_int = {
                'five': 5,
                'six': 6,
                'seven': 7,
                }
        if node.has_attribute_type('age', str):
            str_val = node.get_attribute('age').value
            if str_val in str_to_int:
                node.set_attribute('age', str_to_int[str_val])
            else:
                raise yatiml.SeasoningError('Invalid age string')


# Create loader
class MyLoader(yatiml.Loader):
    pass

yatiml.add_to_loader(MyLoader, Submission)
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: six\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(doc.name)
print(doc.age)
print(doc.tool)
