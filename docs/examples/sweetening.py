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
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        int_to_str = {
                5: 'five',
                6: 'six',
                7: 'seven'
                }
        int_val = int(node.get_attribute('age').get_value())
        if int_val in int_to_str:
            node.set_attribute('age', int_to_str[int_val])


# Create dumper
dumps = yatiml.dumps_function(Submission)

# Dump YAML
doc = Submission('Youssou', 7, 'pencils')
yaml_text = dumps(doc)

print(yaml_text)
