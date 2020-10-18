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


# Create loader
load = yatiml.load_function(Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = load(yaml_text)

print(doc.name)
print(doc.age)
print(doc.tool)
