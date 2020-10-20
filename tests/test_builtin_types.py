"""Tests for the yatiml module."""
import collections
from datetime import datetime
from typing import (
        Dict, List, Mapping, MutableMapping, MutableSequence, Optional,
        Sequence, Union)

import pytest
import yatiml


def test_load_str() -> None:
    load = yatiml.load_function(str)
    data = load('test')
    assert isinstance(data, str)
    assert data == 'test'


def test_load_str_type_error() -> None:
    load = yatiml.load_function(str)
    with pytest.raises(yatiml.RecognitionError):
        load('1')


def test_load_int() -> None:
    load = yatiml.load_function(int)
    data = load('42')
    assert isinstance(data, int)
    assert data == 42


def test_load_float() -> None:
    load = yatiml.load_function(float)
    data = load('3.1415')
    assert isinstance(data, float)
    assert data == 3.1415


def test_load_bool() -> None:
    load = yatiml.load_function(bool)
    data = load('True')
    assert isinstance(data, bool)
    assert data is True


def test_load_datetime() -> None:
    load = yatiml.load_function(datetime)
    data = load('2018-10-27T06:05:23Z')
    assert isinstance(data, datetime)
    assert data.year == 2018
    assert data.second == 23


def test_load_list() -> None:
    load = yatiml.load_function(List[str])
    data = load('- test1\n- test2\n')
    assert isinstance(data, list)
    assert data == ['test1', 'test2']


def test_load_list_item_type_mismatch() -> None:
    load = yatiml.load_function(List[str])
    with pytest.raises(yatiml.RecognitionError):
        load('[test1, 2]')


def test_load_nested_list() -> None:
    load = yatiml.load_function(List[List[int]])
    data = load('- [1, 2]\n- [3, 4]\n')
    assert data == [[1, 2], [3, 4]]


def test_load_list_mismatch() -> None:
    load = yatiml.load_function(List[int])
    with pytest.raises(yatiml.RecognitionError):
        load('12\n')


def test_load_sequence() -> None:
    load = yatiml.load_function(Sequence[int])
    data = load('- 1\n- 2')
    assert isinstance(data, collections.abc.Sequence)
    assert data == [1, 2]


def test_load_mutable_sequence() -> None:
    load = yatiml.load_function(MutableSequence[int])
    data = load('[3, 4]')
    assert data == [3, 4]


def test_load_dict() -> None:
    load = yatiml.load_function(Dict[str, str])
    data = load('key1: test1\nkey2: test2\n')
    assert isinstance(data, dict)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_dict_invalid_key() -> None:
    load = yatiml.load_function(Dict[int, str])
    with pytest.raises(RuntimeError):
        load(
                '1: one\n'
                '2: two\n'
                '3: three\n')


def test_load_dict_item_type_mismatch() -> None:
    load = yatiml.load_function(Dict[str, str])
    with pytest.raises(yatiml.RecognitionError):
        load('key1: test1\nkey2: 2\n')


def test_load_mapping() -> None:
    load = yatiml.load_function(Mapping[str, str])
    data = load('key1: test1\nkey2: test2\n')
    assert isinstance(data, collections.abc.MutableMapping)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_mutable_mapping() -> None:
    load = yatiml.load_function(MutableMapping[str, str])
    data = load('key1: test1\nkey2: test2\n')
    assert isinstance(data, collections.abc.MutableMapping)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_nested_dict() -> None:
    load = yatiml.load_function(Dict[str, Dict[str, bool]])
    data = load('key1: { key2: True, key3: False }\nkey4: {}')
    assert data == {'key1': {'key2': True, 'key3': False}, 'key4': {}}


def test_load_mixed_dict_list() -> None:
    load = yatiml.load_function(List[Dict[str, int]])
    data = load('[{key1: 10},{key2: 11, key3: 13}]')
    assert data == [{'key1': 10}, {'key2': 11, 'key3': 13}]

    with pytest.raises(yatiml.RecognitionError):
        load('[{key1: string}]')


def test_load_dict_error() -> None:
    load = yatiml.load_function(Dict[str, str])
    with pytest.raises(yatiml.RecognitionError):
        load('10')


def test_load_union() -> None:
    load = yatiml.load_function(Union[str, int])
    data = load('10')
    assert isinstance(data, int)
    assert data == 10
    data = load('test')
    assert isinstance(data, str)
    assert data == 'test'


def test_union_mismatch() -> None:
    load = yatiml.load_function(Union[str, int])
    with pytest.raises(yatiml.RecognitionError):
        load('2.71')


def test_optional() -> None:
    load = yatiml.load_function(Optional[str])
    data = load('test')
    assert data == 'test'

    data = load('!!null')
    assert data is None


def test_empty_document() -> None:
    load = yatiml.load_function(Optional[str])
    data = load('')
    assert data is None


def test_dump_str() -> None:
    dumps = yatiml.dumps_function()
    text = dumps('test')
    assert text == 'test\n...\n'


def test_dump_str_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps('test')
    assert text == '"test"'


def test_dump_datetime() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(datetime(2018, 10, 27))
    assert text == '"2018-10-27 00:00:00"'


def test_dump_datetime_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(datetime(2020, 10, 16))
    assert text == '"2020-10-16 00:00:00"'


def test_dump_int_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(42)
    assert text == '42'


def test_dump_float_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(13.5)
    assert text == '13.5'


def test_dump_bool_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(True)
    assert text == 'true'


def test_dump_null_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(None)
    assert text == 'null'
