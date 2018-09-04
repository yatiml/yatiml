#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
import pytest
import ruamel.yaml as yaml

from typing import List

import yatiml


def test_load_str():
    loader = yatiml.make_loader(str)
    text = 'test'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, str)
    assert data == 'test'


def test_load_multiple_docs():
    loader = yatiml.make_loader(str)
    text = (
        '---\n'
        'test1\n'
        '...\n'
        '---\n'
        'test2\n'
        '...\n')
    data = yaml.load_all(text, Loader=loader)
    assert list(data) == ['test1', 'test2']


def test_load_str_type_error():
    loader = yatiml.make_loader(str)
    text = '1'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=loader)


def test_load_int():
    loader = yatiml.make_loader(int)
    text = '42'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, int)
    assert data == 42


def test_load_float():
    loader = yatiml.make_loader(float)
    text = '3.1415'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, float)
    assert data == 3.1415


def test_load_bool():
    loader = yatiml.make_loader(bool)
    text = 'True'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, bool)
    assert data is True


def test_load_null():
    loader = yatiml.make_loader(None)
    text = '!!null'
    data = yaml.load(text, Loader=loader)
    assert data is None


def test_load_list():
    loader = yatiml.make_loader(List[str])
    text = '- test1\n- test2\n'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, list)
    assert data == ['test1', 'test2']


def test_load_list_item_type_mismatch():
    loader = yatiml.make_loader(List[str])
    text = '[test1, 2]'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=loader)


def test_load_nested_list():
    loader = yatiml.make_loader(List[List[int]])
    text = '- [1, 2]\n- [3, 4]\n'
    data = yaml.load(text, Loader=loader)
    assert data == [[1, 2], [3, 4]]
