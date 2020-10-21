import sys
from typing import Union

import pytest

import yatiml


class BoolTester:
    def __init__(self, x: Union[int, bool]) -> None:
        self.x = x


class BoolFixTester:
    # Note the order of the Union arguments: we had a bug that only
    # showed up if a non-bool type was listed after the bool_union_fix,
    # and only for attributes.
    # So don't rearrange this unless you add another regression test for
    # that.
    def __init__(self, x: Union[bool, yatiml.bool_union_fix, int]) -> None:
        self.x = x


def test_load_bool() -> None:
    load = yatiml.load_function(bool)
    data = load('true')
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_int() -> None:
    load = yatiml.load_function(bool)
    with pytest.raises(yatiml.RecognitionError):
        load('12')


def test_load_bool_fix() -> None:
    load = yatiml.load_function(yatiml.bool_union_fix)
    data = load('true')
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_fix_int() -> None:
    load = yatiml.load_function(yatiml.bool_union_fix)
    with pytest.raises(yatiml.RecognitionError):
        load('12')


def test_load_bool_union_bool() -> None:
    # On Python 3.7 and up, Union[bool, int] does not collapse to int.
    # So there, this is supposed to work without the work-around.
    if sys.version_info.major > 3 or sys.version_info.minor >= 7:
        load = yatiml.load_function(Union[int, bool])   # type: ignore
        data = load('true')
        assert isinstance(data, bool)
        assert data is True


def test_load_bool_union_int() -> None:
    load = yatiml.load_function(Union[int, bool])   # type: ignore
    data = load('42')
    assert isinstance(data, int)
    assert data == 42


def test_load_bool_fix_union_bool() -> None:
    load = yatiml.load_function(    # type: ignore
            Union[int, yatiml.bool_union_fix, bool])    # type: ignore
    data = load('true')
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_fix_union_int() -> None:
    load = yatiml.load_function(    # type: ignore
            Union[int, yatiml.bool_union_fix, bool])    # type: ignore
    data = load('42')
    assert isinstance(data, int)
    assert data == 42


def test_load_bool_object_bool() -> None:
    # On Python 3.7 and up, Union[bool, int] does not collapse to int.
    # So there, this is supposed to work without the work-around.
    if sys.version_info.major > 3 or sys.version_info.minor > 7:
        load = yatiml.load_function(BoolTester)
        data = load('x: true')
        assert isinstance(data.x, bool)
        assert data.x is True


def test_load_bool_object_int() -> None:
    load = yatiml.load_function(BoolTester)
    data = load('x: 42')
    assert isinstance(data.x, int)
    assert data.x == 42


def test_load_bool_fix_object_bool() -> None:
    load = yatiml.load_function(BoolFixTester)
    data = load('x: true')
    assert isinstance(data.x, bool)
    assert data.x is True


def test_load_bool_fix_object_int() -> None:
    load = yatiml.load_function(BoolFixTester)
    data = load('x: 42')
    assert isinstance(data.x, int)
    assert data.x == 42


def test_dump_object_bool() -> None:
    dumps = yatiml.dumps_function(BoolTester)
    text = dumps(BoolTester(True))
    assert text == 'x: true\n'


def test_dump_object_int() -> None:
    dumps = yatiml.dumps_function(BoolTester)
    text = dumps(BoolTester(21))
    assert text == 'x: 21\n'


def test_dump_object_bool_fix() -> None:
    dumps = yatiml.dumps_function(BoolFixTester)
    text = dumps(BoolFixTester(True))
    assert text == 'x: true\n'


def test_dump_object_int_fix() -> None:
    dumps = yatiml.dumps_function(BoolFixTester)
    text = dumps(BoolFixTester(21))
    assert text == 'x: 21\n'
