import yatiml

import pytest   # type: ignore

import math
from typing import Any, Dict, List, Optional, Tuple, Type, Union


@pytest.fixture
def string_loader():
    class StringLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(StringLoader, str)
    return StringLoader


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


class Document2:
    def __init__(self, cursor_at: Vector2D, shapes: List[Shape]=[]) -> None:
        # Yes, having [] as a default value is a bad idea, but ok here
        self.cursor_at = cursor_at
        self.shapes = shapes


class Super:
    def __init__(self, subclass: str) -> None:
        pass


class SubA(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def yatiml_recognize(cls, node: yatiml.ClassNode) -> None:
        node.require_attribute_value('subclass', 'A')


class SubB(Super):
    def __init__(self, subclass: str) -> None:
        super().__init__(subclass)

    @classmethod
    def yatiml_recognize(cls, node: yatiml.ClassNode) -> None:
        node.require_attribute_value('subclass', 'B')


class Universal:
    def __init__(self, a: int, b: List[int]) -> None:
        self.a = a
        self.b = b

    @classmethod
    def yatiml_recognize(cls, node: yatiml.ClassNode) -> None:
        # recognizes anything as being of this type
        pass

    def yatiml_attributes(self) -> None:    # type: ignore
        # intentionally broken
        pass


class Extensible:
    def __init__(self, a: int, **kwargs: Any) -> None:
        self.a = a
        self.kwargs = kwargs

    def yatiml_attributes(self) -> Dict[str, Any]:
        attrs = self.kwargs.copy()
        attrs['a'] = self.a
        return attrs


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
            [Document2, Shape, Rectangle, Circle, Vector2D])
    yatiml.set_document_type(Document2Loader, Document2)
    return Document2Loader


@pytest.fixture
def document2_dumper():
    class Document2Dumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(
            Document2Dumper,
            [Document2, Shape, Rectangle, Circle, Vector2D])
    return Document2Dumper


@pytest.fixture
def super_loader():
    class SuperLoader(yatiml.Loader):
        pass
    yatiml.add_to_loader(SuperLoader, [Super, SubA, SubB])
    yatiml.set_document_type(SuperLoader, Super)
    return SuperLoader


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
