from enum import Enum
from typing import Union
import yatiml


class Color(Enum):
    red = 1
    green = 2
    blue = 3


class Thing:
    def __init__(self, color: Union[str, Color]) -> None:
        if isinstance(color, str):
            color = Color[color]
        self.color = color


# Creating things with colors in two ways
thing1 = Thing('red')
thing2 = Thing(Color.green)


# Create loader
load = yatiml.load_function(Thing, Color)

# Load YAML
yaml_text = 'color: red\n'
doc = load(yaml_text)

print(type(doc.attr))
print(doc.attr)
