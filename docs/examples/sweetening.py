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
    def yatiml_sweeten(cls, node: yatiml.Node) -> None:
        int_to_str = {
                5: 'five',
                6: 'six',
                7: 'seven'
                }
        int_val = int(node.get_attribute('age').get_value())
        if int_val in int_to_str:
            node.set_attribute('age', int_to_str[int_val])


# Create dumper
class MyDumper(yatiml.Dumper):
    pass

yatiml.add_to_dumper(MyDumper, Submission)


# Dump YAML
doc = Submission('Youssou', 7, 'pencils')
yaml_text = yaml.dump(doc, Dumper=MyDumper)

print(yaml_text)
