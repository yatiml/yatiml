"""Tests for the yatiml module."""
from collections import OrderedDict
import sys
from typing import Any, Dict, List, Union

import pytest  # type: ignore
import yatiml

from .conftest import (
        Abstract, BrokenPrivateAttributes, Circle, Color, Color2, Color3,
        ComplexPrivateAttributes, Concrete, ConstrainedString, DashedAttribute,
        DictAttribute, Document1, Document2, Document3, Document4, Document5,
        Document6, Ellipse, Extensible, ManyAttrs, Postcode, PrivateAttributes,
        Raises, Rectangle, Shape, StringLike, SubA, SubA2, SubA3, SubB, SubB2,
        SubB3, Super, Super2, Super3, Super3Clone, Super4, Super5, Sub45,
        raises, UnionAttribute, Universal, Vector2D)


def test_load_class() -> None:
    load = yatiml.load_function(Document1)
    data = load('attr1: test_value')
    assert isinstance(data, Document1)
    assert data.attr1 == 'test_value'


def test_load_class_return_type() -> None:
    def test_fn(text: str) -> Document1:
        load = yatiml.load_function(Document1)
        return load(text)

    assert isinstance(test_fn('attr1: test_value'), Document1)
    assert test_fn('attr1: test_value').attr1 == 'test_value'


def test_init_raises() -> None:
    load = yatiml.load_function(Raises)
    with raises(yatiml.RecognitionError):
        load('x: 20')


def test_recognize_subclass() -> None:
    load = yatiml.load_function(Shape, Rectangle, Circle, Ellipse, Vector2D)
    data = load(
            'center:\n'
            '  x: 10.0\n'
            '  y: 12.3\n')
    assert isinstance(data, Shape)
    assert data.center.x == 10.0
    assert data.center.y == 12.3


def test_missing_attribute_class() -> None:
    # omitting Vector2D from the list here
    load = yatiml.load_function(
            Document2, Color2, Shape, Rectangle, Circle)
    with raises(yatiml.RecognitionError):
        load(
                'cursor_at:\n'
                '  x: 42.0\n'
                '  y: 42.1\n')


def test_missing_attribute() -> None:
    load = yatiml.load_function(Universal)
    with raises(yatiml.RecognitionError):
        load('a: 2')


def test_ambiguous_missing_attribute() -> None:
    load = yatiml.load_function(Document5)
    with raises(yatiml.RecognitionError):
        data = load(
                'attr1: 10\n'
                'attrx: x\n'
                'attry: y\n')


def test_many_attributes() -> None:
    load = yatiml.load_function(ManyAttrs)
    with raises(yatiml.RecognitionError):
        data = load(
                'attr1: 1\n'
                'attr2: 2\n'
                'attr3: 3\n'
                'attr4: 4\n'
                'attr5: 5\n'
                'attr6: 6\n'
                'attr7: 7\n'
                'test: test\n'
                'testing: testing\n'
                'python: tested\n')


def test_extra_attribute() -> None:
    load = yatiml.load_function(Vector2D)
    with raises(yatiml.RecognitionError):
        load(
                'x: 12.3\n'
                'y: 45.6\n'
                'z: 78.9\n')


def test_incorrect_attribute_type() -> None:
    load = yatiml.load_function(Universal)
    with raises(yatiml.RecognitionError):
        load(
                'a: 2\n'
                'b: [test1, test2]\n')


def test_optional_attribute() -> None:
    load = yatiml.load_function(
            Document2, Color2, Shape, Rectangle, Circle, Vector2D)
    data = load(
            'cursor_at:\n'
            '  x: 42.0\n'
            '  y: 42.1\n')
    assert isinstance(data, Document2)
    assert data.cursor_at.x == 42.0
    assert data.cursor_at.y == 42.1
    assert data.shapes == []


def test_union_attribute() -> None:
    load = yatiml.load_function(UnionAttribute)
    data = load('a: 10')
    assert isinstance(data, UnionAttribute)


def test_dict_attribute() -> None:
    load = yatiml.load_function(DictAttribute)
    data = load(
            'a:\n'
            '  b: 10\n'
            '  c: 20\n')
    assert isinstance(data, DictAttribute)
    assert isinstance(data.a, dict)
    assert data.a['b'] == 10
    assert data.a['c'] == 20


def test_custom_recognize() -> None:
    load = yatiml.load_function(Super, SubA, SubB)
    data = load('subclass: A')
    assert isinstance(data, SubA)


def test_built_in_instead_of_class() -> None:
    load = yatiml.load_function(Shape, Rectangle, Circle, Ellipse, Vector2D)
    with raises(yatiml.RecognitionError):
        load('center: 10')


def test_parent_fallback() -> None:
    load = yatiml.load_function(Super, SubA, SubB)
    data = load('subclass: x')
    assert isinstance(data, Super)


def test_enum() -> None:
    load = yatiml.load_function(Color3)
    assert load('no') == Color3.NO
    assert load('on') == Color3.ON
    assert load('false') == Color3.FALSE
    assert load('black_and_white') == Color3.BLACK_AND_WHITE


def test_abstract_base_class() -> None:
    # mypy does not accept ABCs for Type[T], see
    # https://github.com/python/mypy/issues/4717
    load = yatiml.load_function(Abstract, Concrete)     # type: ignore
    with raises(yatiml.RecognitionError):
        load('attr: 13')

    load(
            'attr: 13\n'
            'attr2: a\n')


def test_missing_discriminator() -> None:
    load = yatiml.load_function(Super, SubA, SubB)
    with raises(yatiml.RecognitionError):
        load('subclas: A')


def test_any_typed_attributes() -> None:
    load = yatiml.load_function(Document5)
    text = (
            'attr1: 10\n'
            'attr2: test\n')
    data = load(text)
    assert data.attr1 == 10
    assert data.attr2 == 'test'

    text = (
            'attr1: [10, 13]\n'
            'attr2:\n'
            '    x: 12.4\n'
            '    y: 78.9\n')
    data = load(text)
    assert data.attr1 == [10, 13]
    assert isinstance(data.attr2, dict)
    assert data.attr2['x'] == 12.4
    assert data.attr2['y'] == 78.9


def test_any_object_tag_strip() -> None:
    load = yatiml.load_function(Document5)
    text = (
            'attr1: test\n'
            'attr2: !Document5\n'
            '    attr1: 3\n'
            '    attr2: test')
    data = load(text)
    assert isinstance(data, Document5)
    assert isinstance(data.attr2, dict)

    assert 'attr1' in data.attr2
    assert isinstance(data.attr2['attr1'], int)
    assert data.attr2['attr1'] == 3

    assert 'attr2' in data.attr2
    assert isinstance(data.attr2['attr2'], str)
    assert data.attr2['attr2'] == 'test'


def test_any_document() -> None:
    # mypy flags this because Any doesn't match Type[T]. The solution
    # is in https://github.com/python/mypy/issues/9773, but that's
    # waiting for a sufficiently round tuit. Meanwhile, we'll have to
    # ignore the type check.
    load = yatiml.load_function(Any)    # type: ignore
    text = '42'
    data = load(text)
    assert data == 42


def test_dump_any() -> None:
    dumps = yatiml.dumps_function(Document5)
    data = Document5(42, 'YAtiML')
    text = dumps(data)
    assert text == (
            'attr1: 42\n'
            'attr2: YAtiML\n')


def test_untyped_attributes() -> None:
    load = yatiml.load_function(Document6)
    text = (
            'attr1: test\n'
            'attr2: [12, 76]')
    data = load(text)
    assert isinstance(data, Document6)
    assert isinstance(data.attr1, str)
    assert data.attr1 == 'test'
    assert isinstance(data.attr2, list)
    assert data.attr2 == [12, 76]


def test_missing_untyped_attributes() -> None:
    load = yatiml.load_function(Document6)
    text = 'attr2: x'
    with raises(yatiml.RecognitionError):
        load(text)


def test_untyped_attributes_tag_strip() -> None:
    load = yatiml.load_function(Document6)
    text = (
            'attr1: test\n'
            'attr2: !Document6\n'
            '    attr1: 3\n'
            '    attr2: test')
    data = load(text)
    assert isinstance(data, Document6)
    assert isinstance(data.attr2, dict)

    assert 'attr1' in data.attr2
    assert isinstance(data.attr2['attr1'], int)
    assert data.attr2['attr1'] == 3

    assert 'attr2' in data.attr2
    assert isinstance(data.attr2['attr2'], str)
    assert data.attr2['attr2'] == 'test'


def test_untyped_document() -> None:
    load = yatiml.load_function()
    text = 'Testing!'
    data = load(text)
    assert data == 'Testing!'


def test_dump_untyped() -> None:
    dumps = yatiml.dumps_function(Document6)
    data = Document6(24, 'LMitAY')
    text = dumps(data)
    assert text == (
            'attr1: 24\n'
            'attr2: LMitAY\n')


def test_yatiml_extra() -> None:
    load = yatiml.load_function(Extensible)
    data = load(
            'a: 10\n'
            'b: test1\n'
            'c: 42\n')
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data._yatiml_extra['b'] == 'test1'
    assert data._yatiml_extra['c'] == 42


def test_yatiml_extra_empty() -> None:
    load = yatiml.load_function(Extensible)
    data = load('a: 10\n')
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert len(data._yatiml_extra) == 0


def test_yatiml_extra_strip() -> None:
    load = yatiml.load_function(Extensible)
    data = load(
            'a: 10\n'
            'b: test1\n'
            'c: !Extensible\n'
            '  a: 12\n'
            '  b: test2\n')
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data._yatiml_extra['b'] == 'test1'
    assert not isinstance(data._yatiml_extra['c'], Extensible)
    assert isinstance(data._yatiml_extra['c'], dict)
    assert data._yatiml_extra['c']['a'] == 12
    assert data._yatiml_extra['c']['b'] == 'test2'


def test_missing_class() -> None:
    load = yatiml.load_function(Shape, Rectangle, Ellipse, Vector2D)
    with raises(yatiml.RecognitionError):
        load(
                'center:\n'
                '  x: 1.0\n'
                '  y: 2.0\n'
                'radius: 10.0\n')


def test_user_class_override() -> None:
    load = yatiml.load_function(Super3, SubA3, SubB3)
    data = load(
            '!SubA3\n'
            'attr: x\n')
    assert isinstance(data, SubA3)


def test_user_class_override2() -> None:
    load = yatiml.load_function(Super, SubA, SubB)
    data = load(
            '!Super\n'
            'subclass: A\n')
    assert isinstance(data, Super)


def test_user_class_conflicting_override() -> None:
    load = yatiml.load_function(Super2, SubA2, SubB2, Ellipse)
    with raises(yatiml.RecognitionError):
        load(
                '!Ellipse\n'
                'subclass: A2\n')


def test_user_class_unknown_override() -> None:
    load = yatiml.load_function(Super2, SubA2, SubB2)
    with raises(yatiml.RecognitionError):
        load(
                '!Ellipse\n'
                'subclass: A2\n')


def test_disambiguated_union() -> None:
    # mypy flags this because Union doesn't match Type[T]. The solution
    # is in https://github.com/python/mypy/issues/9773, but that's
    # waiting for a sufficiently round tuit. Meanwhile, we'll have to
    # ignore the type check.
    load = yatiml.load_function(    # type: ignore
            Union[Super3, Super3Clone], Super3, Super3Clone)
    with raises(yatiml.RecognitionError):
        load('attr: X\n')

    data = load(
            '!Super3\n'
            'attr: X\n')
    assert isinstance(data, Super3)
    assert not isinstance(data, Super3Clone)


def test_different_recognitions_of_the_same_type() -> None:
    # mypy flags this because Union doesn't match Type[T]. The solution
    # is in https://github.com/python/mypy/issues/9773, but that's
    # waiting for a sufficiently round tuit. Meanwhile, we'll have to
    # ignore the type check.
    load = yatiml.load_function(    # type: ignore
            Union[Super4, Super5], Super4, Super5, Sub45)
    data = load('attr: 42')
    assert isinstance(data, Sub45)


def test_savorize() -> None:
    load = yatiml.load_function(Super2, SubA2, SubB2)
    data = load('subclass: A2\n')
    assert isinstance(data, SubA2)


def test_sweeten() -> None:
    dumps = yatiml.dumps_function(Super2, SubA2, SubB2)
    text = dumps(SubA2())
    assert text == 'subclass: A2\n'


def test_sweeten_json() -> None:
    dumps = yatiml.dumps_json_function(Super2, SubA2, SubB2)
    text = dumps(SubA2())
    assert text == '{"subclass":"A2"}'


def test_load_dashed_attribute() -> None:
    load = yatiml.load_function(DashedAttribute)
    data = load('dashed-attribute: 23\n')
    assert isinstance(data, DashedAttribute)
    assert data.dashed_attribute == 23


def test_remove_defaulted_attribute() -> None:
    dumps = yatiml.dumps_function(
            Document3, Color2, Shape, Rectangle, Circle, Vector2D)
    data = Document3(Vector2D(1.2, 3.4))
    data.another_number = 13
    text = dumps(data)
    assert text == 'cursor_at:\n  x: 1.2\n  y: 3.4\nanother_number: 13\n'

    data.color = 'blue'
    data.age = 8
    data.has_siblings = True
    data.score = 5.5
    data.extra_shape = Circle(Vector2D(1.0, 2.0), 3.0)
    data.another_number = 42
    text = dumps(data)
    assert text == (
            'cursor_at:\n'
            '  x: 1.2\n'
            '  y: 3.4\n'
            'color: blue\n'
            'age: 8\n'
            'has_siblings: true\n'
            'score: 5.5\n'
            'extra_shape:\n'
            '  center:\n'
            '    x: 1.0\n'
            '    y: 2.0\n'
            '  radius: 3.0\n')


def test_yatiml_defaults() -> None:
    dumps = yatiml.dumps_function(
            Document4, Shape, Rectangle, Circle, Vector2D)
    text = dumps(Document4())
    assert text == '{}\n'


def test_dump_dashed_attribute() -> None:
    dumps = yatiml.dumps_function(DashedAttribute)
    text = dumps(DashedAttribute(34))
    assert text == 'dashed-attribute: 34\n'


def test_dump_dashed_attribute_json() -> None:
    dumps = yatiml.dumps_json_function(DashedAttribute)
    text = dumps(DashedAttribute(34))
    assert text == '{"dashed-attribute":34}'


def test_dump_document1() -> None:
    dumps = yatiml.dumps_function(Document1)
    text = dumps(Document1('test'))
    assert text == 'attr1: test\n'


def test_dump_document1_json() -> None:
    dumps = yatiml.dumps_json_function(Document1)
    text = dumps(Document1('test'))
    assert text == '{"attr1":"test"}'


def test_dump_custom_attributes() -> None:
    dumps = yatiml.dumps_function(Extensible)
    extra_attributes = OrderedDict([('b', 5), ('c', 3)])
    data = Extensible(10, _yatiml_extra=extra_attributes)
    text = dumps(data)
    assert text == (
            'a: 10\n'
            'b: 5\n'
            'c: 3\n')


def test_dump_custom_attributes_json() -> None:
    dumps = yatiml.dumps_json_function(Extensible)
    extra_attributes = OrderedDict([('b', 5), ('c', 3)])
    data = Extensible(10, _yatiml_extra=extra_attributes)
    text = dumps(data, indent=2)
    assert text == (
            '{\n'
            '  "a": 10,\n'
            '  "b": 5,\n'
            '  "c": 3\n'
            '}\n')


def test_load_complex_document() -> None:
    load = yatiml.load_function(
            Document2, Color2, Shape, Rectangle, Circle, Vector2D)
    text = ('cursor_at:\n'
            '  x: 3.0\n'
            '  y: 4.0\n'
            'shapes:\n'
            '- center:\n'
            '    x: 5.0\n'
            '    y: 6.0\n'
            '  radius: 12.0\n'
            '- center:\n'
            '    x: -2.0\n'
            '    y: -5.0\n'
            '  width: 3.0\n'
            '  height: 7.0\n'
            'color: blue\n'
            'extra_shape:\n'
            '  center:\n'
            '    x: 7.0\n'
            '    y: 8.0\n'
            '  radius: 2.0\n'
            )
    doc = load(text)
    assert isinstance(doc, Document2)
    assert isinstance(doc.shapes, list)
    assert doc.color == Color2.BLUE


def test_dump_complex_document() -> None:
    dumps = yatiml.dumps_function(
            Document2, Color2, Shape, Rectangle, Circle, Vector2D)
    shape1 = Circle(Vector2D(5.0, 6.0), 12.0)
    shape2 = Rectangle(Vector2D(-2.0, -5.0), 3.0, 7.0)
    data = Document2(Vector2D(3.0, 4.0), [shape1, shape2])
    text = dumps(data)
    assert text == (
            'cursor_at:\n'
            '  x: 3.0\n'
            '  y: 4.0\n'
            'shapes:\n'
            '- center:\n'
            '    x: 5.0\n'
            '    y: 6.0\n'
            '  radius: 12.0\n'
            '- center:\n'
            '    x: -2.0\n'
            '    y: -5.0\n'
            '  width: 3.0\n'
            '  height: 7.0\n'
            'color: red\n'
            'extra_shape: null\n'
            )


def test_dump_complex_document_json() -> None:
    dumps = yatiml.dumps_json_function(
            Document2, Color2, Shape, Rectangle, Circle, Vector2D)
    shape1 = Circle(Vector2D(5.0, 6.0), 12.0)
    shape2 = Rectangle(Vector2D(-2.0, -5.0), 3.0, 7.0)
    data = Document2(Vector2D(3.0, 4.0), [shape1, shape2])
    text = dumps(data, indent=2)
    assert text == (
            '{\n'
            '  "cursor_at": {\n'
            '    "x": 3.0,\n'
            '    "y": 4.0\n'
            '  },\n'
            '  "shapes": [\n'
            '    {\n'
            '      "center": {\n'
            '        "x": 5.0,\n'
            '        "y": 6.0\n'
            '      },\n'
            '      "radius": 12.0\n'
            '    },\n'
            '    {\n'
            '      "center": {\n'
            '        "x": -2.0,\n'
            '        "y": -5.0\n'
            '      },\n'
            '      "width": 3.0,\n'
            '      "height": 7.0\n'
            '    }\n'
            '  ],\n'
            '  "color": "red",\n'
            '  "extra_shape": null\n'
            '}\n'
            )


def test_broken_custom_attributes() -> None:
    dumps = yatiml.dumps_function(Universal)
    data = Universal(3, [4])
    with raises(RuntimeError):
        dumps(data)


def test_broken_custom_attributes_json() -> None:
    dumps = yatiml.dumps_json_function(Universal)
    data = Universal(3, [4])
    with raises(RuntimeError):
        dumps(data)


def test_yatiml_attributes() -> None:
    dumps = yatiml.dumps_function(PrivateAttributes)
    text = dumps(PrivateAttributes(10, 42.0))
    assert text == 'a: 10\nb: 42.0\n'


def test_yatiml_attributes_json() -> None:
    dumps = yatiml.dumps_json_function(PrivateAttributes)
    text = dumps(PrivateAttributes(10, 42.0))
    assert text == '{"a":10,"b":42.0}'


def test_private_attributes() -> None:
    dumps = yatiml.dumps_function(BrokenPrivateAttributes)
    with raises(AttributeError):
        dumps(BrokenPrivateAttributes(10, 42.0))


def test_private_attributes_json() -> None:
    dumps = yatiml.dumps_json_function(BrokenPrivateAttributes)
    with raises(AttributeError):
        dumps(BrokenPrivateAttributes(10, 42.0))


def test_complex_private_attributes() -> None:
    dumps = yatiml.dumps_function(ComplexPrivateAttributes, Vector2D)
    text = dumps(ComplexPrivateAttributes(Vector2D(1.0, 2.0)))
    assert text == ('a:\n'
                    '  x: 1.0\n'
                    '  y: 2.0\n')


def test_enum_class() -> None:
    load = yatiml.load_function(Color)
    data = load('blue\n')
    assert isinstance(data, Color)
    assert data == Color.blue

    with raises(yatiml.RecognitionError):
        load('yelow\n')


def test_enum_class2() -> None:
    load = yatiml.load_function(Color)
    with raises(yatiml.RecognitionError):
        load('1\n')


def test_dump_enum() -> None:
    dumps = yatiml.dumps_function(Color)
    text = dumps(Color.green)
    assert text == 'green\n...\n'


def test_dump_enum_json() -> None:
    dumps = yatiml.dumps_json_function(Color)
    text = dumps(Color.green)
    assert text == '"green"'


def test_dump_enum2() -> None:
    # check that we don't generate cross-references for enum values
    # regression test
    dumps = yatiml.dumps_function(Color)
    text = dumps([Color.blue, Color.blue])
    assert text == '- blue\n- blue\n'


def test_enum_savorize() -> None:
    load = yatiml.load_function(Color2)
    data = load('blue\n')
    assert isinstance(data, Color2)
    assert data == Color2.BLUE


def test_enum_sweeten() -> None:
    dumps = yatiml.dumps_function(Color2)
    text = dumps(Color2.YELLOW)
    assert text == 'yellow\n...\n'


def test_enum_sweeten_json() -> None:
    dumps = yatiml.dumps_json_function(Color2)
    text = dumps(Color2.YELLOW)
    assert text == '"yellow"'


def test_enum_list() -> None:
    load = yatiml.load_function(List[Color2], Color2)
    data = load(
            '- blue\n'
            '- yellow\n')
    assert isinstance(data[0], Color2)
    assert data[0] == Color2.BLUE
    assert data[1] == Color2.YELLOW


def test_enum_dict() -> None:
    load = yatiml.load_function(Dict[str, Color2], Color2)
    data = load(
            'x: red\n'
            'y: orange\n')
    assert 'x' in data
    assert isinstance(data['x'], Color2)
    assert data['x'] == Color2.RED
    assert 'y' in data
    assert isinstance(data['y'], Color2)
    assert data['y'] == Color2.ORANGE


def test_load_user_string() -> None:
    load = yatiml.load_function(ConstrainedString)
    data = load('abcd\n')
    assert isinstance(data, ConstrainedString)
    assert data == 'abcd'

    with raises(yatiml.RecognitionError):
        load('efgh\n')


def test_load_user_string_from_incorrect_type() -> None:
    load = yatiml.load_function(ConstrainedString)
    with raises(yatiml.RecognitionError):
        load('10\n')


def test_dump_user_string() -> None:
    dumps = yatiml.dumps_function(ConstrainedString)
    text = dumps(ConstrainedString('abc'))
    assert text == 'abc\n...\n'


def test_dump_user_string_json() -> None:
    dumps = yatiml.dumps_json_function(ConstrainedString)
    text = dumps(ConstrainedString('abc'))
    assert text == '"abc"'


def test_load_user_string_like() -> None:
    load = yatiml.load_function(StringLike)
    data = load('abcd\n')
    assert isinstance(data, StringLike)
    assert data._value == 'abcd'


def test_dump_user_string_like() -> None:
    dumps = yatiml.dumps_function(StringLike)
    text = dumps(StringLike('abcd'))
    assert text == 'abcd\n...\n'


def test_dump_user_string_like_json() -> None:
    dumps = yatiml.dumps_json_function(StringLike)
    text = dumps(StringLike('abcd'))
    assert text == '"abcd"'


def test_load_user_string_key() -> None:
    load = yatiml.load_function(
            Dict[ConstrainedString, int], ConstrainedString)
    data = load('abcd: 10\n')
    assert isinstance(data, dict)
    assert len(data) == 1
    assert isinstance(list(data.keys())[0], ConstrainedString)
    assert ConstrainedString('abcd') in data
    assert data[ConstrainedString('abcd')] == 10

    with raises(yatiml.RecognitionError):
        load('efgh: 4\n')


def test_dump_user_string_key() -> None:
    dumps = yatiml.dumps_function(ConstrainedString)
    data = {ConstrainedString('abcd'): 10}
    text = dumps(data)
    assert text == 'abcd: 10\n'


def test_load_string_like_key() -> None:
    load = yatiml.load_function(Dict[StringLike, int], StringLike)
    data = load('abcd: 10\nefgh: 20\n')
    assert isinstance(data, dict)
    assert len(data) == 2
    assert isinstance(list(data.keys())[0], StringLike)
    assert isinstance(list(data.keys())[1], StringLike)
    assert StringLike('abcd') in data
    assert data[StringLike('abcd')] == 10
    assert data[StringLike('efgh')] == 20


def test_dump_string_like_key() -> None:
    dumps = yatiml.dumps_function(StringLike)
    data = {StringLike('abcd'): 13}
    text = dumps(data)
    assert text == 'abcd: 13\n'


def test_parsed_class() -> None:
    load = yatiml.load_function(Postcode)
    data = load('1098 XG')
    assert isinstance(data, Postcode)
    assert data.digits == 1098
    assert data.letters == 'XG'


def test_dump_parsed_class() -> None:
    dumps = yatiml.dumps_function(Postcode)
    text = dumps(Postcode(1098, 'XG'))
    assert text == '1098 XG\n...\n'


def test_dump_parsed_class_json() -> None:
    dumps = yatiml.dumps_json_function(Postcode)
    text = dumps(Postcode(1098, 'XG'))
    assert text == '"1098 XG"'


if sys.version_info >= (3, 7):

    from .conftest import DataClass

    def test_load_data_class() -> None:
        load = yatiml.load_function(DataClass)
        data = load('attr1: test_value')
        assert isinstance(data, DataClass)
        assert data.attr1 == 'test_value'
        assert data.attr2 == 42

    def test_dump_data_class() -> None:
        dumps = yatiml.dumps_function(DataClass)
        text = dumps(DataClass('test'))
        assert text == (
                'attr1: test\n'
                'attr2: 42\n')
