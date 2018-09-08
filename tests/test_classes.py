#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
import pytest   # type: ignore
import ruamel.yaml as yaml

import yatiml

from .conftest import Document1, Document2, Extensible, Shape, SubA, Super


def test_load_class(document1_loader):
    text = 'attr1: test_value'
    data = yaml.load(text, Loader=document1_loader)
    assert isinstance(data, Document1)
    assert data.attr1 == 'test_value'


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


def test_kwargs(extensible_loader):
    text = ('a: 10\n'
            'b: test1\n'
            'c: 42\n')
    data = yaml.load(text, Loader=extensible_loader)
    assert isinstance(data, Extensible)
    assert data.a == 10
    assert data.kwargs['b'] == 'test1'
    assert data.kwargs['c'] == 42


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
