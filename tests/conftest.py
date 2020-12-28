import enum
import math
from collections import OrderedDict, UserString
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from typing_extensions import Type

from ruamel import yaml

import pytest  # type: ignore
import yatiml
from yatiml.recognizer import Recognizer


@pytest.fixture
def tmpdir_path(tmp_path: Any) -> Path:
    # Older versions of PyTest on older versions of Python give us a
    # pathlib2.Path, which YAtiML does not support. This smooths over
    # the difference and makes sure our tests work everywhere.
    return Path(str(tmp_path))


class Document1:
    def __init__(self, attr1: str) -> None:
        self.attr1 = attr1


class Vector2D:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y


class Shape:
    def __init__(self, center: Vector2D) -> None:
        self.center = center


class Rectangle(Shape):
    def __init__(self, center: Vector2D, width: float, height: float) -> None:
        super().__init__(center)
        self.width = width
        self.height = height


class Circle(Shape):
    def __init__(self, center: Vector2D, radius: float) -> None:
        super().__init__(center)
        self.radius = radius


class Ellipse(Shape):
    def __init__(
            self, center: Vector2D,
            semi_major: float, semi_minor: float
            ) -> None:
        super().__init__(center)
        self.semi_major = semi_major
        self.semi_minor = semi_minor
        self.eccentricity = math.sqrt(1.0 - semi_minor**2 / semi_major**2)

    @classmethod
    def _yatiml_subobjects(cls) -> List[Tuple[str, Type, bool]]:
        return [('semi_major', float, True),
                ('semi_minor', float, True)
                ]


class Color(enum.Enum):
    red = 'red'
    orange = 'orange'
    yellow = 'yellow'
    green = 'green'
    blue = 'blue'


class Color2(enum.Enum):
    RED = 1
    ORANGE = 2
    YELLOW = 3
    GREEN = 4
    BLUE = 5

    @classmethod
    def _yatiml_savorize(self, node: yatiml.Node) -> None:
        if node.is_scalar(str):
            node.set_value(node.get_value().upper())  # type: ignore

    @classmethod
    def _yatiml_sweeten(self, node: yatiml.Node) -> None:
        node.set_value(node.get_value().lower())  # type: ignore


class Document2:
    def __init__(self, cursor_at: Vector2D, shapes: List[Shape] = None,
                 color: Color2 = Color2.RED,
                 extra_shape: Optional[Shape] = None
                 ) -> None:
        self.cursor_at = cursor_at
        self.shapes = shapes if shapes is not None else list()
        self.color = color
        self.extra_shape = extra_shape


class Document3:
    def __init__(self, cursor_at: Vector2D,
                 color: str = 'red',
                 age: int = 7,
                 has_siblings: bool = False,
                 score: float = 7.5,
                 extra_shape: Optional[Shape] = None,
                 another_number: int = 42
                 ) -> None:
        self.cursor_at = cursor_at
        self.color = color
        self.age = age
        self.has_siblings = has_siblings
        self.score = score
        self.extra_shape = extra_shape
        self.another_number = another_number

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.remove_attributes_with_default_values(cls)


class Document4:
    def __init__(self, shapes: List[Shape] = None) -> None:
        self.shapes = shapes if shapes is not None else list()

    _yatiml_defaults = {'shapes': []}   # type: Dict[str, Any]

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.remove_attributes_with_default_values(cls)


class Super:
    def __init__(self, subclass: str) -> None:
        pass


class SubA(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'A')


class SubB(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'B')


class Super2:
    def __init__(self) -> None:
        pass


class SubA2(Super2):
    def __init__(self) -> None:
        pass

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'A2')

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.remove_attribute('subclass')

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.set_attribute('subclass', 'A2')


class SubB2(Super2):
    def __init__(self) -> None:
        pass

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'B2')

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.remove_attribute('subclass')

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.set_attribute('subclass', 'B2')


class Universal:
    def __init__(self, a: int, b: List[int]) -> None:
        self.a = a
        self.b = b

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.Node) -> None:
        # recognizes anything as being of this type
        pass

    def _yatiml_attributes(self) -> None:    # type: ignore
        # intentionally broken
        pass


class Extensible:
    def __init__(self, a: int, _yatiml_extra: OrderedDict) -> None:
        self.a = a
        self._yatiml_extra = _yatiml_extra


class UnionAttribute:
    def __init__(self, a: Union[int, str]) -> None:
        self.a = a


class DictAttribute:
    def __init__(self, a: Dict[str, int]) -> None:
        self.a = a


class PrivateAttributes:
    def __init__(self, a: int, b: float) -> None:
        self.__a = a
        self.__b = b

    def _yatiml_attributes(self) -> OrderedDict:
        attrs = OrderedDict()   # type: OrderedDict
        attrs['a'] = self.__a
        attrs['b'] = self.__b
        return attrs


class BrokenPrivateAttributes:
    def __init__(self, a: int, b: float) -> None:
        self.__a = a
        self.__b = b


class ComplexPrivateAttributes:
    def __init__(self, a: Vector2D) -> None:
        self.__a = a

    def _yatiml_attributes(self) -> OrderedDict:
        attrs = OrderedDict()  # type: OrderedDict[str, Vector2D]
        attrs['a'] = self.__a
        return attrs


class ConstrainedString(UserString):
    def __init__(self, seq: Any) -> None:
        super().__init__(seq)
        if not self.data.startswith('a'):   # type: ignore
            raise ValueError('ConstrainedString must start with an a')


class Postcode:
    def __init__(self, digits: int, letters: str) -> None:
        self.digits = digits
        self.letters = letters

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_scalar(str)

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        text = str(node.get_value())
        node.make_mapping()
        node.set_attribute('digits', int(text[0:4]))
        node.set_attribute('letters', text[5:7])

    @classmethod
    def _yatiml_sweeten(self, node: yatiml.Node) -> None:
        digits = node.get_attribute('digits').get_value()
        letters = node.get_attribute('letters').get_value()
        node.set_value('{} {}'.format(digits, letters))


class DashedAttribute:
    def __init__(self, dashed_attribute: int) -> None:
        self.dashed_attribute = dashed_attribute

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.dashes_to_unders_in_keys()

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.unders_to_dashes_in_keys()


class Raises:
    def __init__(self, x: int) -> None:
        if x >= 10:
            raise RuntimeError('x must be less than 10')


@pytest.fixture
def yaml_seq_node() -> yaml.Node:
    # A yaml.SequenceNode representing a sequence of mappings
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')
    item1_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item1_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', '100.0')
    value1 = [
            (item1_key1_node, item1_value1_node),
            (item1_key2_node, item1_value2_node)
            ]

    item1 = yaml.MappingNode(tag1, value1)

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')
    item2_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item2_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', '200.0')
    item2_key3_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'on_sale')
    item2_value3_node = yaml.ScalarNode('tag:yaml.org,2002:bool', 'True')
    value2 = [
            (item2_key1_node, item2_value1_node),
            (item2_key2_node, item2_value2_node),
            (item2_key3_node, item2_value3_node)
            ]
    item2 = yaml.MappingNode(tag2, value2)

    return yaml.SequenceNode('tag:yaml.org,2002:seq', [item1, item2])


@pytest.fixture
def yaml_map_node() -> yaml.Node:
    # A yaml.MappingNode representing a mapping of mappings
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:float', '100.0')
    value1 = [(item1_key1_node, item1_value1_node)]

    item1 = yaml.MappingNode(tag1, value1)
    key1 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:float', '200.0')
    value2 = [(item2_key1_node, item2_value1_node)]

    item2 = yaml.MappingNode(tag2, value2)
    key2 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')

    item3 = yaml.ScalarNode('tag:yaml.org,2002:float', '150.0')
    key3 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item3')

    outer_map_value = [(key1, item1), (key2, item2), (key3, item3)]
    outer_tag = 'tag:yaml.org,2002:map'
    outer_map = yaml.MappingNode(outer_tag, outer_map_value)

    return outer_map


@pytest.fixture
def yaml_index_node() -> yaml.Node:
    # A yaml.MappingNode representing a mapping of mappings indexed
    # by item id
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')
    item1_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item1_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', '100.0')
    value1 = [
            (item1_key1_node, item1_value1_node),
            (item1_key2_node, item1_value2_node)]

    item1 = yaml.MappingNode(tag1, value1)
    key1 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')
    item2_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item2_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', '200.0')
    value2 = [
            (item2_key1_node, item2_value1_node),
            (item2_key2_node, item2_value2_node)]

    item2 = yaml.MappingNode(tag2, value2)
    key2 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')

    tag3 = 'tag:yaml.org,2002:map'
    item3_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item3_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item3')
    item3_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item3_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', '150.0')
    item3_key3_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'on_sale')
    item3_value3_node = yaml.ScalarNode('tag:yaml.org,2002:bool', 'true')
    value3 = [
            (item3_key1_node, item3_value1_node),
            (item3_key2_node, item3_value2_node),
            (item3_key3_node, item3_value3_node)]

    item3 = yaml.MappingNode(tag3, value3)
    key3 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item3')

    outer_map_value = [(key1, item1), (key2, item2), (key3, item3)]
    outer_tag = 'tag:yaml.org,2002:map'
    outer_map = yaml.MappingNode(outer_tag, outer_map_value)

    return outer_map


@pytest.fixture
def yaml_node(
        yaml_seq_node: yaml.Node, yaml_map_node: yaml.Node,
        yaml_index_node: yaml.Node) -> yaml.Node:
    tag = 'tag:yaml.org,2002:map'

    attr1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'attr1')
    attr1_value_node = yaml.ScalarNode('tag:yaml.org,2002:int', '42')

    null_attr_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'null_attr')
    null_attr_value_node = yaml.ScalarNode('tag:yaml.org,2002:null', '')

    list1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'list1')
    dict1_key_node = yaml.ScalarNode('tag:yaml.org,2002:map', 'dict1')

    index1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'index1')

    dashed_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'dashed-attr')
    dashed_value_node = yaml.ScalarNode('tag:yaml.org,2002:int', '13')

    undered_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'undered_attr')
    undered_value_node = yaml.ScalarNode('tag:yaml.org,2002:float', '13.0')

    value = [
            (attr1_key_node, attr1_value_node),
            (null_attr_key_node, null_attr_value_node),
            (list1_key_node, yaml_seq_node),
            (dict1_key_node, yaml_map_node),
            (index1_key_node, yaml_index_node),
            (dashed_key_node, dashed_value_node),
            (undered_key_node, undered_value_node)
            ]
    return yaml.MappingNode(tag, value)


@pytest.fixture
def class_node(yaml_node: yaml.Node) -> yatiml.Node:
    return yatiml.Node(yaml_node)


@pytest.fixture
def scalar_node() -> yatiml.Node:
    ynode = yaml.ScalarNode('tag:yaml.org,2002:int', '42')
    return yatiml.Node(ynode)


@pytest.fixture
def unknown_node(yaml_node: yaml.Node) -> yatiml.UnknownNode:
    return yatiml.UnknownNode(Recognizer({}), yaml_node)


@pytest.fixture
def unknown_scalar_node() -> yatiml.UnknownNode:
    ynode = yaml.ScalarNode('tag:yaml.org,2002:int', '23')
    return yatiml.UnknownNode(Recognizer({}), ynode)


@pytest.fixture
def unknown_sequence_node() -> yatiml.UnknownNode:
    ynode = yaml.SequenceNode('tag:yaml.org,2002:seq', [])
    return yatiml.UnknownNode(Recognizer({}), ynode)


@pytest.fixture
def class_node_dup_key() -> yatiml.Node:
    # A Node wrapping a yaml.SequenceNode representing a sequence of
    # mappings with a duplicate key.
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item')
    value1 = [(item1_key1_node, item1_value1_node)]

    item1 = yaml.MappingNode(tag1, value1)

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item')
    value2 = [(item2_key1_node, item2_value1_node)]
    item2 = yaml.MappingNode(tag2, value2)

    seq_node = yaml.SequenceNode('tag:yaml.org,2002:seq', [item1, item2])

    list1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'dup_list')
    value = [(list1_key_node, seq_node)]
    map_node = yaml.MappingNode('tag:yaml.org,2002:map', value)
    return yatiml.Node(map_node)
