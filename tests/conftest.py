import enum
import math
from collections import OrderedDict, UserString
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Type, Union

from ruamel import yaml

import pytest  # type: ignore
import yatiml
from yatiml.recognizer import Recognizer


@pytest.fixture
def string_loader():
    class StringLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(StringLoader, str)
    return StringLoader


@pytest.fixture
def datetime_loader():
    class DatetimeLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(DatetimeLoader, datetime)
    return DatetimeLoader


@pytest.fixture
def string_list_loader():
    class StringListLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(StringListLoader, List[str])
    return StringListLoader


@pytest.fixture
def int_list_list_loader():
    class IntListListLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(IntListListLoader, List[List[int]])
    return IntListListLoader


@pytest.fixture
def int_list_loader():
    class IntListLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(IntListLoader, List[int])
    return IntListLoader


@pytest.fixture
def string_dict_loader():
    class StringDictLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(StringDictLoader, Dict[str, str])
    return StringDictLoader


@pytest.fixture
def int_key_dict_loader():
    class IntKeyDictLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(IntKeyDictLoader, Dict[int, str])
    return IntKeyDictLoader


@pytest.fixture
def nested_dict_loader():
    class NestedDictLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(NestedDictLoader, Dict[str, Dict[str, bool]])
    return NestedDictLoader


@pytest.fixture
def mixed_dict_list_loader():
    class MixedDictListLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(MixedDictListLoader, List[Dict[str, int]])
    return MixedDictListLoader


@pytest.fixture
def union_loader():
    class UnionLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(UnionLoader, Union[str, int])
    return UnionLoader


@pytest.fixture
def optional_loader():
    class OptionalLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(OptionalLoader, Optional[str])
    return OptionalLoader


@pytest.fixture
def plain_dumper():
    class PlainDumper(yatiml.Dumper):
        pass
    return PlainDumper


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
    def yatiml_subobjects(cls) -> List[Tuple[str, Type, bool]]:
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
    def yatiml_savorize(self, node: yatiml.Node) -> None:
        if node.is_scalar(str):
            node.set_value(node.get_value().upper())  # type: ignore

    @classmethod
    def yatiml_sweeten(self, node: yatiml.Node) -> None:
        node.set_value(node.get_value().lower())  # type: ignore


class Document2:
    def __init__(self, cursor_at: Vector2D, shapes: List[Shape]=None,
                 color: Color2=Color2.RED, extra_shape: Optional[Shape] = None
                 ) -> None:
        # Yes, having [] as a default value is a bad idea, but ok here
        self.cursor_at = cursor_at
        self.shapes = shapes if shapes is not None else list()
        self.color = color
        self.extra_shape = extra_shape


class Super:
    def __init__(self, subclass: str) -> None:
        pass


class SubA(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'A')


class SubB(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'B')


class Super2:
    def __init__(self) -> None:
        pass


class SubA2(Super2):
    def __init__(self) -> None:
        pass

    @classmethod
    def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'A2')

    @classmethod
    def yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.remove_attribute('subclass')

    @classmethod
    def yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.set_attribute('subclass', 'A2')


class SubB2(Super2):
    def __init__(self) -> None:
        pass

    @classmethod
    def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_attribute_value('subclass', 'B2')

    @classmethod
    def yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.remove_attribute('subclass')

    @classmethod
    def yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.set_attribute('subclass', 'B2')


class Universal:
    def __init__(self, a: int, b: List[int]) -> None:
        self.a = a
        self.b = b

    @classmethod
    def yatiml_recognize(cls, node: yatiml.Node) -> None:
        # recognizes anything as being of this type
        pass

    def yatiml_attributes(self) -> None:    # type: ignore
        # intentionally broken
        pass


class Extensible:
    def __init__(self, a: int, yatiml_extra: OrderedDict) -> None:
        self.a = a
        self.yatiml_extra = yatiml_extra


class UnionAttribute:
    def __init__(self, a: Union[int, str]) -> None:
        self.a = a


class PrivateAttributes:
    def __init__(self, a: int, b: float) -> None:
        self.__a = a
        self.__b = b

    def yatiml_attributes(self) -> OrderedDict:
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

    def yatiml_attributes(self) -> OrderedDict:
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
    def yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_scalar(str)

    @classmethod
    def yatiml_savorize(cls, node: yatiml.Node) -> None:
        text = str(node.get_value())
        node.make_mapping()
        node.set_attribute('digits', int(text[0:4]))
        node.set_attribute('letters', text[5:7])

    @classmethod
    def yatiml_sweeten(self, node: yatiml.Node) -> None:
        digits = node.get_attribute('digits').get_value()
        letters = node.get_attribute('letters').get_value()
        node.set_value('{} {}'.format(digits, letters))


class DashedAttribute:
    def __init__(self, dashed_attribute: int) -> None:
        self.dashed_attribute = dashed_attribute

    @classmethod
    def yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.dashes_to_unders_in_keys()

    @classmethod
    def yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.unders_to_dashes_in_keys()


@pytest.fixture
def document1_loader():
    class Document1Loader(yatiml.Loader):
        pass
    yatiml.add_to_loader(Document1Loader, Document1)
    yatiml.set_document_type(Document1Loader, Document1)
    return Document1Loader


@pytest.fixture
def document1_dumper():
    class Document1Dumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(Document1Dumper, Document1)
    return Document1Dumper


@pytest.fixture
def vector_loader():
    class VectorLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(VectorLoader, Vector2D)
    yatiml.set_document_type(VectorLoader, Vector2D)
    return VectorLoader


@pytest.fixture
def shape_loader():
    class ShapeLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(
            ShapeLoader, [Shape, Rectangle, Circle, Ellipse, Vector2D])
    yatiml.set_document_type(ShapeLoader, Shape)
    return ShapeLoader


@pytest.fixture
def missing_circle_loader():
    class MissingCircleLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(
            MissingCircleLoader, [Shape, Rectangle, Ellipse, Vector2D])
    yatiml.set_document_type(MissingCircleLoader, Shape)
    return MissingCircleLoader


@pytest.fixture
def document2_loader():
    class Document2Loader(yatiml.Loader):
        pass
    yatiml.add_to_loader(
            Document2Loader,
            [Color2, Document2, Shape, Rectangle, Circle, Vector2D])
    yatiml.set_document_type(Document2Loader, Document2)
    return Document2Loader


@pytest.fixture
def document2_dumper():
    class Document2Dumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(
            Document2Dumper,
            [Color2, Document2, Shape, Rectangle, Circle, Vector2D])
    return Document2Dumper


@pytest.fixture
def enum_loader():
    class EnumLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(EnumLoader, Color)
    yatiml.set_document_type(EnumLoader, Color)
    return EnumLoader


@pytest.fixture
def enum_dumper():
    class EnumDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(EnumDumper, Color)
    return EnumDumper


@pytest.fixture
def enum_loader2():
    class EnumLoader2(yatiml.Loader):
        pass
    yatiml.add_to_loader(EnumLoader2, Color2)
    yatiml.set_document_type(EnumLoader2, Color2)
    return EnumLoader2


@pytest.fixture
def enum_dumper2():
    class EnumDumper2(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(EnumDumper2, Color2)
    return EnumDumper2


@pytest.fixture
def user_string_loader():
    class UserStringLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(UserStringLoader, ConstrainedString)
    yatiml.set_document_type(UserStringLoader, ConstrainedString)
    return UserStringLoader


@pytest.fixture
def user_string_dumper():
    class UserStringDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(UserStringDumper, ConstrainedString)
    return UserStringDumper


@pytest.fixture
def super_loader():
    class SuperLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(SuperLoader, [Super, SubA, SubB])
    yatiml.set_document_type(SuperLoader, Super)
    return SuperLoader


@pytest.fixture
def super2_loader():
    class Super2Loader(yatiml.Loader):
        pass
    yatiml.add_to_loader(Super2Loader, [Super2, SubA2, SubB2])
    yatiml.set_document_type(Super2Loader, Super2)
    return Super2Loader


@pytest.fixture
def super2_dumper():
    class Super2Dumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(Super2Dumper, [Super2, SubA2, SubB2])
    return Super2Dumper


@pytest.fixture
def universal_loader():
    class UniversalLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(UniversalLoader, Universal)
    yatiml.set_document_type(UniversalLoader, Universal)
    return UniversalLoader


@pytest.fixture
def universal_dumper():
    class UniversalDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(UniversalDumper, Universal)
    return UniversalDumper


@pytest.fixture
def extensible_loader():
    class ExtensibleLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(ExtensibleLoader, Extensible)
    yatiml.set_document_type(ExtensibleLoader, Extensible)
    return ExtensibleLoader


@pytest.fixture
def extensible_dumper():
    class ExtensibleDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(ExtensibleDumper, Extensible)
    return ExtensibleDumper


@pytest.fixture
def private_attributes_dumper():
    class PrivateAttributesDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(PrivateAttributesDumper, PrivateAttributes)
    return PrivateAttributesDumper


@pytest.fixture
def broken_private_attributes_dumper():
    class BrokenPrivateAttributesDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(
            BrokenPrivateAttributesDumper,
            BrokenPrivateAttributes)
    return BrokenPrivateAttributesDumper


@pytest.fixture
def complex_private_attributes_dumper():
    class ComplexPrivateAttributesDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(ComplexPrivateAttributesDumper, Vector2D)
    yatiml.add_to_dumper(
            ComplexPrivateAttributesDumper, ComplexPrivateAttributes)
    return ComplexPrivateAttributesDumper


@pytest.fixture
def union_attribute_loader():
    class UnionAttributeLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(UnionAttributeLoader, UnionAttribute)
    yatiml.set_document_type(UnionAttributeLoader, UnionAttribute)
    return UnionAttributeLoader


@pytest.fixture
def parsed_class_loader():
    class ParsedClassLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(ParsedClassLoader, Postcode)
    yatiml.set_document_type(ParsedClassLoader, Postcode)
    return ParsedClassLoader


@pytest.fixture
def parsed_class_dumper():
    class ParsedClassDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(ParsedClassDumper, Postcode)
    return ParsedClassDumper


@pytest.fixture
def dashed_attribute_loader():
    class DashedAttributeLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(DashedAttributeLoader, DashedAttribute)
    yatiml.set_document_type(DashedAttributeLoader, DashedAttribute)
    return DashedAttributeLoader


@pytest.fixture
def dashed_attribute_dumper():
    class DashedAttributeDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(DashedAttributeDumper, DashedAttribute)
    return DashedAttributeDumper


@pytest.fixture
def yaml_seq_node():
    # A yaml.SequenceNode representing a sequence of mappings
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')
    item1_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item1_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', 100.0)
    value1 = [
            (item1_key1_node, item1_value1_node),
            (item1_key2_node, item1_value2_node)
            ]

    item1 = yaml.MappingNode(tag1, value1)

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item_id')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')
    item2_key2_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item2_value2_node = yaml.ScalarNode('tag:yaml.org,2002:float', 200.0)
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
def yaml_map_node():
    # A yaml.MappingNode representing a mapping of mappings
    tag1 = 'tag:yaml.org,2002:map'
    item1_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item1_value1_node = yaml.ScalarNode('tag:yaml.org,2002:float', 100.0)
    value1 = [(item1_key1_node, item1_value1_node)]

    item1 = yaml.MappingNode(tag1, value1)
    key1 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item1')

    tag2 = 'tag:yaml.org,2002:map'
    item2_key1_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'price')
    item2_value1_node = yaml.ScalarNode('tag:yaml.org,2002:float', 200.0)
    value2 = [(item2_key1_node, item2_value1_node)]

    item2 = yaml.MappingNode(tag2, value2)
    key2 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item2')

    item3 = yaml.ScalarNode('tag:yaml.org,2002:float', 150.0)
    key3 = yaml.ScalarNode('tag:yaml.org,2002:str', 'item3')

    outer_map_value = [(key1, item1), (key2, item2), (key3, item3)]
    outer_tag = 'tag:yaml.org,2002:map'
    outer_map = yaml.MappingNode(outer_tag, outer_map_value)

    return outer_map


@pytest.fixture
def yaml_node(yaml_seq_node, yaml_map_node):
    tag = 'tag:yaml.org,2002:map'

    attr1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'attr1')
    attr1_value_node = yaml.ScalarNode('tag:yaml.org,2002:int', 42)

    null_attr_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'null_attr')
    null_attr_value_node = yaml.ScalarNode('tag:yaml.org,2002:null', None)

    list1_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'list1')
    dict1_key_node = yaml.ScalarNode('tag:yaml.org,2002:map', 'dict1')

    dashed_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'dashed-attr')
    dashed_value_node = yaml.ScalarNode('tag:yaml.org,2002:int', 13)

    undered_key_node = yaml.ScalarNode('tag:yaml.org,2002:str', 'undered_attr')
    undered_value_node = yaml.ScalarNode('tag:yaml.org,2002:float', 13.0)

    value = [
            (attr1_key_node, attr1_value_node),
            (null_attr_key_node, null_attr_value_node),
            (list1_key_node, yaml_seq_node),
            (dict1_key_node, yaml_map_node),
            (dashed_key_node, dashed_value_node),
            (undered_key_node, undered_value_node)
            ]
    return yaml.MappingNode(tag, value)


@pytest.fixture
def class_node(yaml_node):
    return yatiml.Node(yaml_node)


@pytest.fixture
def scalar_node():
    ynode = yaml.ScalarNode('tag:yaml.org,2002:int', '42')
    return yatiml.Node(ynode)


@pytest.fixture
def unknown_node(yaml_node):
    return yatiml.UnknownNode(Recognizer({}), yaml_node)


@pytest.fixture
def unknown_scalar_node():
    ynode = yaml.ScalarNode('tag:yaml.org,2002:int', '23')
    return yatiml.UnknownNode(Recognizer({}), ynode)


@pytest.fixture
def unknown_sequence_node():
    ynode = yaml.SequenceNode('tag:yaml.org,2002:seq', [])
    return yatiml.UnknownNode(Recognizer({}), ynode)


@pytest.fixture
def class_node_dup_key():
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
