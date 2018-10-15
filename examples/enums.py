import enum
from ruamel import yaml
from typing import List, Union
import yatiml


# Create document classes
class Color(enum.Enum):
    red = 0xff0000
    orange = 0xff8000
    yellow = 0xffff00
    green = 0x008000
    blue = 0x00aeef


class Shape:
    def __init__(self, center: List[float], color: Color) -> None:
        self.center = center
        self.color = color


class Circle(Shape):
    def __init__(self, center: List[float], color: Color, radius: float) -> None:
        super().__init__(center, color)
        self.radius = radius


class Square(Shape):
    def __init__(self, center: List[float], color: Color, width: float, height: float) -> None:
        super().__init__(center, color)
        self.width = width
        self.height = height


class Submission(Shape):
    def __init__(
            self,
            name: str,
            age: Union[int, str],
            drawing: List[Shape]
            ) -> None:
        self.name = name
        self.age = age
        self.drawing = drawing


# Create loader
class MyLoader(yatiml.Loader):
  pass

yatiml.add_to_loader(MyLoader, [Color, Shape, Circle, Square, Submission])
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'drawing:\n'
             '  - center: [1.0, 1.0]\n'
             '    color: red\n'
             '    radius: 2.0\n'
             '  - center: [5.0, 5.0]\n'
             '    color: blue\n'
             '    width: 1.0\n'
             '    height: 1.0\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(doc.name)
print(doc.age)
print(doc.drawing[0].color)
