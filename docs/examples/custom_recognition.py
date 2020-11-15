from typing import Optional, Union
import yatiml


# Create document class
class Submission:
    def __init__(
            self,
            name: str,
            age: int,
            tool: Optional[str]=None
            ) -> None:
        self.name = name
        self.age = age
        self.tool = tool

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute('name', str)
        node.require_attribute('age', Union[int, str])

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        str_to_int = {
                'five': 5,
                'six': 6,
                'seven': 7,
                }
        if node.has_attribute_type('age', str):
            str_val = node.get_attribute('age').get_value()
            if str_val in str_to_int:
                node.set_attribute('age', str_to_int[str_val])
            else:
                raise yatiml.SeasoningError('Invalid age string')


# Create loader
load = yatiml.load_function(Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: six\n')
doc = load(yaml_text)

print(doc.name)
print(doc.age)
print(doc.tool)
