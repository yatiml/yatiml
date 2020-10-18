#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
from collections import OrderedDict

import ruamel.yaml as yaml

import pytest  # type: ignore
import yatiml

from .conftest import (BrokenPrivateAttributes, Circle, Color, Color2,
                       ComplexPrivateAttributes, ConstrainedString,
                       DashedAttribute, DictAttribute, Document1, Document2,
                       Document3, Document4, Extensible, Postcode,
                       PrivateAttributes, Rectangle, Shape, SubA, SubA2, Super,
                       UnionAttribute, Universal, Vector2D)


def test_load_class(document1_loader):
    text = 'attr1: test_value'
    data = yaml.load(text, Loader=document1_loader)
    assert isinstance(data, Document1)
    assert data.attr1 == 'test_value'


def test_init_raises(raises_loader):
    text = 'x: 20'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=raises_loader)


def test_recognize_subclass(shape_loader):
    text = ('center:\n'
            '  x: 10.0\n'
            '  y: 12.3\n')
    data = yaml.load(text, Loader=shape_loader)
    assert isinstance(data, Shape)
    assert data.center.x == 10.0
    assert data.center.y == 12.3


def test_missing_attribute(universal_loader):
    text = 'a: 2'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=universal_loader)


def test_extra_attribute(vector_loader):
    text = ('x: 12.3\n'
            'y: 45.6\n'
            'z: 78.9\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=vector_loader)


def test_incorrect_attribute_type(universal_loader):
    text = ('a: 2\n'
            'b: [test1, test2]\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=universal_loader)


def test_optional_attribute(document2_loader):
    text = ('cursor_at:\n'
            '  x: 42.0\n'
            '  y: 42.1\n')
    data = yaml.load(text, Loader=document2_loader)
    assert isinstance(data, Document2)
    assert data.cursor_at.x == 42.0
    assert data.cursor_at.y == 42.1
    assert data.shapes == []


def test_union_attribute(union_attribute_loader):
    text = 'a: 10'
    data = yaml.load(text, Loader=union_attribute_loader)
    assert isinstance(data, UnionAttribute)


def test_dict_attribute(dict_attribute_loader):
    text = ('a:\n'
            '  b: 10\n'
            '  c: 20\n')
    data = yaml.load(text, Loader=dict_attribute_loader)
    assert isinstance(data, DictAttribute)
    assert isinstance(data.a, OrderedDict)
    assert data.a['b'] == 10
    assert data.a['c'] == 20


def test_custom_recognize(super_loader):
    text = 'subclass: A'
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, SubA)


def test_built_in_instead_of_class(shape_loader):
    text = 'center: 10'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=shape_loader)


def test_parent_fallback(super_loader):
    text = 'subclass: x'
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, Super)


def test_missing_discriminator(super_loader):
    text = 'subclas: A'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=super_loader)


def test_yatiml_extra(extensible_loader):
    text = ('a: 10\n'
            'b: test1\n'
            'c: 42\n')
    data = yaml.load(text, Loader=extensible_loader)
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data._yatiml_extra['b'] == 'test1'
    assert data._yatiml_extra['c'] == 42


def test_yatiml_extra_empty(extensible_loader):
    text = 'a: 10\n'
    data = yaml.load(text, Loader=extensible_loader)
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert len(data._yatiml_extra) == 0


def test_yatiml_extra_strip(extensible_loader):
    text = ('a: 10\n'
            'b: test1\n'
            'c: !Extensible\n'
            '  a: 12\n'
            '  b: test2\n')
    data = yaml.load(text, Loader=extensible_loader)
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data._yatiml_extra['b'] == 'test1'
    assert not isinstance(data._yatiml_extra['c'], Extensible)
    assert isinstance(data._yatiml_extra['c'], OrderedDict)
    assert data._yatiml_extra['c']['a'] == 12
    assert data._yatiml_extra['c']['b'] == 'test2'


def test_missing_class(missing_circle_loader):
    text = ('center:\n'
            '  x: 1.0\n'
            '  y: 2.0\n'
            'radius: 10.0\n')
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=missing_circle_loader)


def test_user_class_override(super_loader):
    text = ('!SubA\n'
            'subclass: x\n')
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, SubA)


def test_user_class_override2(super_loader):
    text = ('!Super\n'
            'subclass: A\n')
    data = yaml.load(text, Loader=super_loader)
    assert isinstance(data, Super)


def test_savorize(super2_loader):
    text = 'subclass: A2\n'
    data = yaml.load(text, Loader=super2_loader)
    assert isinstance(data, SubA2)


def test_sweeten(super2_dumper):
    data = SubA2()
    text = yaml.dump(data, Dumper=super2_dumper)
    assert text == 'subclass: A2\n'


def test_sweeten_json(super2_json_dumper):
    data = SubA2()
    text = yaml.dump(data, Dumper=super2_json_dumper)
    assert text == '{"subclass":"A2"}'


def test_load_dashed_attribute(dashed_attribute_loader):
    text = 'dashed-attribute: 23\n'
    data = yaml.load(text, Loader=dashed_attribute_loader)
    assert isinstance(data, DashedAttribute)
    assert data.dashed_attribute == 23


def test_remove_defaulted_attribute(document3_dumper):
    data = Document3(Vector2D(1.2, 3.4))
    data.another_number = 13
    text = yaml.dump(data, Dumper=document3_dumper)
    assert text == 'cursor_at:\n  x: 1.2\n  y: 3.4\nanother_number: 13\n'

    data.color = 'blue'
    data.age = 8
    data.has_siblings = True
    data.score = 5.5
    data.extra_shape = Circle(Vector2D(1.0, 2.0), 3.0)
    data.another_number = 42
    text = yaml.dump(data, Dumper=document3_dumper)
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


def test_yatiml_defaults(document4_dumper):
    data = Document4()
    text = yaml.dump(data, Dumper=document4_dumper)
    assert text == '{}\n'


def test_dump_dashed_attribute(dashed_attribute_dumper):
    data = DashedAttribute(34)
    text = yaml.dump(data, Dumper=dashed_attribute_dumper)
    assert text == 'dashed-attribute: 34\n'


def test_dump_dashed_attribute_json(dashed_attribute_json_dumper):
    data = DashedAttribute(34)
    text = yaml.dump(data, Dumper=dashed_attribute_json_dumper)
    assert text == '{"dashed-attribute":34}'


def test_dump_document1(document1_dumper):
    data = Document1('test')
    text = yaml.dump(data, Dumper=document1_dumper)
    assert text == 'attr1: test\n'


def test_dump_document1_json(document1_json_dumper):
    data = Document1('test')
    text = yaml.dump(data, Dumper=document1_json_dumper)
    assert text == '{"attr1":"test"}'


def test_dump_custom_attributes(extensible_dumper):
    extra_attributes = OrderedDict([('b', 5), ('c', 3)])
    data = Extensible(10, _yatiml_extra=extra_attributes)
    text = yaml.dump(data, Dumper=extensible_dumper)
    assert text == 'a: 10\nb: 5\nc: 3\n'


def test_dump_custom_attributes_json(extensible_json_dumper):
    extra_attributes = OrderedDict([('b', 5), ('c', 3)])
    data = Extensible(10, _yatiml_extra=extra_attributes)
    text = yaml.dump(data, Dumper=extensible_json_dumper, indent=2)
    assert text == (
            '{\n'
            '  "a": 10,\n'
            '  "b": 5,\n'
            '  "c": 3\n'
            '}\n')


def test_load_complex_document(document2_loader, caplog):
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
    doc = yaml.load(text, Loader=document2_loader)
    assert isinstance(doc, Document2)
    assert isinstance(doc.shapes, list)
    assert doc.color == Color2.BLUE


def test_dump_complex_document(document2_dumper):
    shape1 = Circle(Vector2D(5.0, 6.0), 12.0)
    shape2 = Rectangle(Vector2D(-2.0, -5.0), 3.0, 7.0)
    data = Document2(Vector2D(3.0, 4.0), [shape1, shape2])
    text = yaml.dump(data, Dumper=document2_dumper)
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
            'extra_shape:\n'
            )


def test_dump_complex_document_json(document2_json_dumper):
    shape1 = Circle(Vector2D(5.0, 6.0), 12.0)
    shape2 = Rectangle(Vector2D(-2.0, -5.0), 3.0, 7.0)
    data = Document2(Vector2D(3.0, 4.0), [shape1, shape2])
    text = yaml.dump(data, Dumper=document2_json_dumper, indent=2)
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


def test_broken_custom_attributes(universal_dumper):
    data = Universal(3, [4])
    with pytest.raises(RuntimeError):
        yaml.dump(data, Dumper=universal_dumper)


def test_broken_custom_attributes_json(universal_json_dumper):
    data = Universal(3, [4])
    with pytest.raises(RuntimeError):
        yaml.dump(data, Dumper=universal_json_dumper)


def test_yatiml_attributes(private_attributes_dumper):
    data = PrivateAttributes(10, 42.0)
    text = yaml.dump(data, Dumper=private_attributes_dumper)
    assert text == 'a: 10\nb: 42.0\n'


def test_yatiml_attributes_json(private_attributes_json_dumper):
    data = PrivateAttributes(10, 42.0)
    text = yaml.dump(data, Dumper=private_attributes_json_dumper)
    assert text == '{"a":10,"b":42.0}'


def test_private_attributes(broken_private_attributes_dumper):
    data = BrokenPrivateAttributes(10, 42.0)
    with pytest.raises(AttributeError):
        yaml.dump(data, Dumper=broken_private_attributes_dumper)


def test_private_attributes_json(broken_private_attributes_json_dumper):
    data = BrokenPrivateAttributes(10, 42.0)
    with pytest.raises(AttributeError):
        yaml.dump(data, Dumper=broken_private_attributes_json_dumper)


def test_complex_private_attributes(complex_private_attributes_dumper):
    data = ComplexPrivateAttributes(Vector2D(1.0, 2.0))
    text = yaml.dump(data, Dumper=complex_private_attributes_dumper)
    assert text == ('a:\n'
                    '  x: 1.0\n'
                    '  y: 2.0\n')


def test_enum_class(enum_loader):
    text = 'blue\n'
    data = yaml.load(text, Loader=enum_loader)
    assert isinstance(data, Color)
    assert data == Color.blue

    text = 'yelow\n'
    with pytest.raises(yatiml.RecognitionError):
        data = yaml.load(text, Loader=enum_loader)

    text = '1\n'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=enum_loader)


def test_dump_enum(enum_dumper):
    text = yaml.dump(Color.green, Dumper=enum_dumper)
    assert text == 'green\n...\n'


def test_dump_enum_json(enum_json_dumper):
    text = yaml.dump(Color.green, Dumper=enum_json_dumper)
    assert text == '"green"'


def test_dump_enum2(enum_dumper):
    # check that we don't generate cross-references for enum values
    # regression test
    text = yaml.dump([Color.blue, Color.blue], Dumper=enum_dumper)
    assert text == '- blue\n- blue\n'


def test_enum_savorize(enum_loader2):
    text = 'blue\n'
    data = yaml.load(text, Loader=enum_loader2)
    assert isinstance(data, Color2)
    assert data == Color2.BLUE


def test_enum_sweeten(enum_dumper2):
    text = yaml.dump(Color2.YELLOW, Dumper=enum_dumper2)
    assert text == 'yellow\n...\n'


def test_enum_sweeten_json(enum_json_dumper2):
    text = yaml.dump(Color2.YELLOW, Dumper=enum_json_dumper2)
    assert text == '"yellow"'


def test_enum_list(enum_list_loader):
    text = ('- blue\n'
            '- yellow\n')
    data = yaml.load(text, Loader=enum_list_loader)
    assert isinstance(data[0], Color2)
    assert data[0] == Color2.BLUE
    assert data[1] == Color2.YELLOW


def test_enum_dict(enum_dict_loader):
    text = ('x: red\n'
            'y: orange\n')
    data = yaml.load(text, Loader=enum_dict_loader)
    assert 'x' in data
    assert isinstance(data['x'], Color2)
    assert data['x'] == Color2.RED
    assert 'y' in data
    assert isinstance(data['y'], Color2)
    assert data['y'] == Color2.ORANGE


def test_user_string(user_string_loader):
    text = 'abcd\n'
    data = yaml.load(text, Loader=user_string_loader)
    assert isinstance(data, ConstrainedString)
    assert data == 'abcd'

    text = 'efgh\n'
    with pytest.raises(ValueError):
        yaml.load(text, Loader=user_string_loader)


def test_dump_user_string(user_string_dumper):
    data = ConstrainedString('abc')
    text = yaml.dump(data, Dumper=user_string_dumper)
    assert text == 'abc\n...\n'


def test_dump_user_string_json(user_string_json_dumper):
    data = ConstrainedString('abc')
    text = yaml.dump(data, Dumper=user_string_json_dumper)
    assert text == '"abc"'


def test_parsed_class(parsed_class_loader):
    text = '1098 XG'
    data = yaml.load(text, Loader=parsed_class_loader)
    assert isinstance(data, Postcode)
    assert data.digits == 1098
    assert data.letters == 'XG'


def test_dump_parsed_class(parsed_class_dumper):
    data = Postcode(1098, 'XG')
    text = yaml.dump(data, Dumper=parsed_class_dumper)
    assert text == '1098 XG\n...\n'


def test_dump_parsed_class_json(parsed_class_json_dumper):
    data = Postcode(1098, 'XG')
    text = yaml.dump(data, Dumper=parsed_class_json_dumper)
    assert text == '"1098 XG"'
