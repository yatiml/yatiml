"""Tests for the yatiml module."""
import collections
from datetime import date, datetime
from math import isnan
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


def test_load_float_format() -> None:
    # Issue #53
    signs = ['', '-', '+']
    numbers = ['0', '1', '12', '12345678901234']
    expsyms = 'eE'
    exponents = ['0', '1', '34']

    load = yatiml.load_function(float)

    def verify(yaml_string: str) -> None:
        data = load(yaml_string)
        assert isinstance(data, float)
        assert data == float(yaml_string)

    for sign in signs:
        for decimal in numbers:
            verify(f'{sign}.{decimal}')
            for expsym in expsyms:
                for exponent in exponents:
                    verify(f'{sign}.{decimal}{expsym}{exponent}')

        for cardinal in numbers:
            verify(f'{sign}{cardinal}.')
            for decimal in numbers:
                verify(f'{sign}{cardinal}.{decimal}')
            for expsym in expsyms:
                for exponent in exponents:
                    verify(f'{sign}{cardinal}{expsym}{exponent}')
                    verify(f'{sign}{cardinal}.{expsym}{exponent}')
                    for decimal in numbers:
                        verify(f'{sign}{cardinal}.{decimal}{expsym}{exponent}')

    assert load('.inf') == float('inf')
    assert load('.Inf') == float('inf')
    assert load('.INF') == float('inf')

    assert load('-.inf') == float('-inf')
    assert load('-.Inf') == float('-inf')
    assert load('-.INF') == float('-inf')

    assert load('+.inf') == float('+inf')
    assert load('+.Inf') == float('+inf')
    assert load('+.INF') == float('+inf')

    assert isnan(load('.nan'))
    assert isnan(load('.NaN'))
    assert isnan(load('.NAN'))


def test_load_bool() -> None:
    bools11 = (
            'y', 'Y', 'yes', 'Yes', 'YES', 'n', 'N', 'no', 'No', 'NO',
            'on', 'On', 'ON', 'off', 'Off', 'OFF')
    bools12 = ('true', 'True', 'TRUE', 'false', 'False', 'FALSE')

    load = yatiml.load_function(bool)

    for b in bools11:
        with pytest.raises(yatiml.RecognitionError):
            load(b)

    for b in bools12:
        data = load(b)
        assert isinstance(data, bool)
        assert data == (b.lower() == 'true')


def test_load_date() -> None:
    load = yatiml.load_function(date)
    data = load('2018-10-27T06:05:23Z')
    assert isinstance(data, datetime)
    assert data.year == 2018
    assert data.second == 23

    load = yatiml.load_function(date)
    data = load('2020-11-15')
    assert isinstance(data, date)
    assert data.year == 2020
    assert data.month == 11
    assert data.day == 15


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
    load = yatiml.load_function(Sequence[int])  # type: ignore
    data = load('- 1\n- 2')
    assert isinstance(data, collections.abc.Sequence)
    assert data == [1, 2]


def test_load_mutable_sequence() -> None:
    load = yatiml.load_function(MutableSequence[int])   # type: ignore
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
    load = yatiml.load_function(Mapping[str, str])  # type: ignore
    data = load('key1: test1\nkey2: test2\n')
    assert isinstance(data, collections.abc.MutableMapping)
    assert data == {'key1': 'test1', 'key2': 'test2'}


def test_load_mutable_mapping() -> None:
    load = yatiml.load_function(MutableMapping[str, str])   # type: ignore
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
    load = yatiml.load_function(Union[str, int])    # type: ignore
    data = load('10')
    assert isinstance(data, int)
    assert data == 10
    data = load('test')
    assert isinstance(data, str)
    assert data == 'test'


def test_union_mismatch() -> None:
    load = yatiml.load_function(Union[str, int])    # type: ignore
    with pytest.raises(yatiml.RecognitionError):
        load('2.71')


def test_optional() -> None:
    load = yatiml.load_function(Optional[str])      # type: ignore
    data = load('test')
    assert data == 'test'

    data = load('!!null')
    assert data is None


def test_empty_document() -> None:
    load = yatiml.load_function(Optional[str])      # type: ignore
    data = load('')
    assert data is None


def test_dump_str() -> None:
    dumps = yatiml.dumps_function()
    text = dumps('test')
    assert text == 'test\n...\n'


def test_dump_ordereddict() -> None:
    dumps = yatiml.dumps_function()
    data = collections.OrderedDict([('x', 1), ('y', 2)])
    text = dumps(data)
    assert text == 'x: 1\ny: 2\n'


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
