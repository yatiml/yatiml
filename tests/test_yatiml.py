#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
import pytest
import ruamel.yaml as yaml

from typing import Dict, List, Union

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


def test_load_dict():
    loader = yatiml.make_loader(Dict[str, str])
    text = 'key1: test1\nkey2: test2\n'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, dict)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_dict_item_type_mismatch():
    loader = yatiml.make_loader(Dict[str, int])
    text = 'key1: test1\nkey2: 2\n'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=loader)


def test_load_nested_dict():
    loader = yatiml.make_loader(Dict[str, Dict[str, bool]])
    text = 'key1: { key2: True, key3: False }\nkey4: {}'
    data = yaml.load(text, Loader=loader)
    assert data == {'key1': {'key2': True, 'key3': False}, 'key4': {}}


def test_load_mixed_dict_list():
    loader = yatiml.make_loader(List[Dict[str, int]])
    text = '[{key1: 10},{key2: 11, key3: 13}]'
    data = yaml.load(text, Loader=loader)
    assert data == [{'key1': 10}, {'key2': 11, 'key3': 13}]


def test_load_dict_error():
    loader = yatiml.make_loader(Dict[str, int])
    text = '10'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=loader)


def test_load_union():
    loader = yatiml.make_loader(Union[str, int])
    text = '10'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, int)
    assert data == 10
    text = 'test'
    data = yaml.load(text, Loader=loader)
    assert isinstance(data, str)
    assert data == 'test'


def test_union_mismatch():
    loader = yatiml.make_loader(Union[str, int])
    text = '2.71'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=loader)
