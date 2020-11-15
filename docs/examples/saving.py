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


# Create dumper
dumps = yatiml.dumps_function(Submission)

# Dump YAML
doc = Submission('Youssou', 7, 'pencils')
yaml_text = dumps(doc)

print(yaml_text)
