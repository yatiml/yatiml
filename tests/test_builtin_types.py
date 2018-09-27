#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the yatiml module."""
import pytest
import ruamel.yaml as yaml

from collections import MutableMapping
from typing import Dict, List

import yatiml


def test_load_str(string_loader):
    text = 'test'
    data = yaml.load(text, Loader=string_loader)
    assert isinstance(data, str)
    assert data == 'test'


def test_load_multiple_docs(string_loader):
    text = (
        '---\n'
        'test1\n'
        '...\n'
        '---\n'
        'test2\n'
        '...\n')
    data = yaml.load_all(text, Loader=string_loader)
    assert list(data) == ['test1', 'test2']


def test_load_str_type_error(string_loader):
    text = '1'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=string_loader)


def test_load_int():
    class IntLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(IntLoader, int)

    text = '42'
    data = yaml.load(text, Loader=IntLoader)
    assert isinstance(data, int)
    assert data == 42


def test_load_float():
    class FloatLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(FloatLoader, float)

    text = '3.1415'
    data = yaml.load(text, Loader=FloatLoader)
    assert isinstance(data, float)
    assert data == 3.1415


def test_load_bool():
    class BoolLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolLoader, bool)

    text = 'True'
    data = yaml.load(text, Loader=BoolLoader)
    assert isinstance(data, bool)
    assert data is True


def test_load_list(string_list_loader):
    text = '- test1\n- test2\n'
    data = yaml.load(text, Loader=string_list_loader)
    assert data == ['test1', 'test2']


def test_load_list_item_type_mismatch(string_list_loader):
    text = '[test1, 2]'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=string_list_loader)


def test_load_nested_list(int_list_list_loader):
    text = '- [1, 2]\n- [3, 4]\n'
    data = yaml.load(text, Loader=int_list_list_loader)
    assert data == [[1, 2], [3, 4]]


def test_load_list_mismatch(int_list_loader):
    text = '12\n'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=int_list_loader)


def test_load_dict(string_dict_loader):
    text = 'key1: test1\nkey2: test2\n'
    data = yaml.load(text, Loader=string_dict_loader)
    assert isinstance(data, MutableMapping)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_dict_invalid_key():
    class IntKeyDictLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(IntKeyDictLoader, Dict[int, str])

    text = ('1: one\n'
            '2: two\n'
            '3: three\n')
    with pytest.raises(RuntimeError):
        yaml.load(text, Loader=IntKeyDictLoader)


def test_load_dict_item_type_mismatch(string_dict_loader):
    text = 'key1: test1\nkey2: 2\n'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=string_dict_loader)


def test_load_nested_dict(nested_dict_loader):
    text = 'key1: { key2: True, key3: False }\nkey4: {}'
    data = yaml.load(text, Loader=nested_dict_loader)
    assert data == {'key1': {'key2': True, 'key3': False}, 'key4': {}}


def test_load_mixed_dict_list():
    class ListDictLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(ListDictLoader, List[Dict[str, int]])
    text = '[{key1: 10},{key2: 11, key3: 13}]'
    data = yaml.load(text, Loader=ListDictLoader)
    assert data == [{'key1': 10}, {'key2': 11, 'key3': 13}]


def test_load_dict_error(string_dict_loader):
    text = '10'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=string_dict_loader)


def test_load_union(union_loader):
    text = '10'
    data = yaml.load(text, Loader=union_loader)
    assert isinstance(data, int)
    assert data == 10
    text = 'test'
    data = yaml.load(text, Loader=union_loader)
    assert isinstance(data, str)
    assert data == 'test'


def test_union_mismatch(union_loader):
    text = '2.71'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=union_loader)


def test_optional(optional_loader):
    text = 'test'
    data = yaml.load(text, Loader=optional_loader)
    assert data == 'test'

    text = '!!null'
    data = yaml.load(text, Loader=optional_loader)
    assert data is None


def test_empty_document(optional_loader):
    text = ''
    data = yaml.load(text, Loader=optional_loader)
    assert data is None


def test_dump_str(plain_dumper):
    data = 'test'
    text = yaml.dump(data, Dumper=plain_dumper)
    assert text == 'test\n...\n'
