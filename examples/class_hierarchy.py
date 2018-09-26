from ruamel import yaml
from typing import List, Sequence, Union
import yatiml


# Create document classes
class Shape:
    def __init__(self, center: List[float]) -> None:
        self.center = center


class Circle(Shape):
    def __init__(self, center: List[float], radius: float) -> None:
        super().__init__(center)
        self.radius = radius


class Square(Shape):
    def __init__(self, center: List[float], width: float, height: float) -> None:
        super().__init__(center)
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

yatiml.add_to_loader(MyLoader, [Shape, Circle, Square, Submission])
yatiml.set_document_type(MyLoader, Submission)

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n'
             'drawing:\n'
             '  - center: [1.0, 1.0]\n'
             '    radius: 2.0\n'
             '  - center: [5.0, 5.0]\n'
             '    width: 1.0\n'
             '    height: 1.0\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(doc.name)
print(doc.age)
print(doc.drawing)
