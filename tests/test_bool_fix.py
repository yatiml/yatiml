import sys
from typing import Union

import pytest
from ruamel import yaml

import yatiml


@pytest.fixture
def bool_loader():
    class BoolLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolLoader, bool)
    return BoolLoader


@pytest.fixture
def bool_fix_loader():
    class BoolFixLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolFixLoader, yatiml.bool_union_fix)
    return BoolFixLoader


@pytest.fixture
def bool_union_loader():
    class BoolUnionLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolUnionLoader, Union[int, bool])
    return BoolUnionLoader


@pytest.fixture
def bool_fix_union_loader():
    class BoolUnionFixLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolUnionFixLoader, Union[
            int, bool, yatiml.bool_union_fix])
    return BoolUnionFixLoader


class BoolTester:
    def __init__(self, x: Union[int, bool]) -> None:
        self.x = x


@pytest.fixture
def bool_tester_loader():
    class BoolTesterLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolTesterLoader, BoolTester)
    yatiml.add_to_loader(BoolTesterLoader, BoolTester)
    return BoolTesterLoader


class BoolFixTester:
    def __init__(self, x: Union[int, bool, yatiml.bool_union_fix]) -> None:
        self.x = x


@pytest.fixture
def bool_fix_tester_loader():
    class BoolFixTesterLoader(yatiml.Loader):
        pass
    yatiml.set_document_type(BoolFixTesterLoader, BoolFixTester)
    yatiml.add_to_loader(BoolFixTesterLoader, BoolFixTester)
    return BoolFixTesterLoader


def test_load_bool(bool_loader):
    text = 'true'
    data = yaml.load(text, Loader=bool_loader)
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_int(bool_loader):
    text = '12'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=bool_loader)


def test_load_bool_fix(bool_fix_loader):
    text = 'true'
    data = yaml.load(text, Loader=bool_fix_loader)
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_fix_int(bool_fix_loader):
    text = '12'
    with pytest.raises(yatiml.RecognitionError):
        yaml.load(text, Loader=bool_fix_loader)


def test_load_bool_union_bool(bool_union_loader):
    # On Python 3.7 and up, Union[bool, int] does not collapse to int.
    # So there, this is supposed to work without the work-around.
    if sys.version_info.major > 3 or sys.version_info.minor > 7:
        text = 'true'
        data = yaml.load(text, Loader=bool_union_loader)
        assert isinstance(data, bool)
        assert data is True


def test_load_bool_union_int(bool_union_loader):
    text = '42'
    data = yaml.load(text, Loader=bool_union_loader)
    assert isinstance(data, int)
    assert data == 42


def test_load_bool_fix_union_bool(bool_fix_union_loader):
    text = 'true'
    data = yaml.load(text, Loader=bool_fix_union_loader)
    assert isinstance(data, bool)
    assert data is True


def test_load_bool_fix_union_int(bool_fix_union_loader):
    text = '42'
    data = yaml.load(text, Loader=bool_fix_union_loader)
    assert isinstance(data, int)
    assert data == 42


def test_load_bool_object_bool(bool_tester_loader):
    # On Python 3.7 and up, Union[bool, int] does not collapse to int.
    # So there, this is supposed to work without the work-around.
    if sys.version_info.major > 3 or sys.version_info.minor > 7:
        text = 'x: true'
        data = yaml.load(text, Loader=bool_tester_loader)
        assert isinstance(data.x, bool)
        assert data.x is True


def test_load_bool_object_int(bool_tester_loader):
    text = 'x: 42'
    data = yaml.load(text, Loader=bool_tester_loader)
    assert isinstance(data.x, int)
    assert data.x == 42


def test_load_bool_fix_object_bool(bool_fix_tester_loader):
    text = 'x: true'
    data = yaml.load(text, Loader=bool_fix_tester_loader)
    assert isinstance(data.x, bool)
    assert data.x is True


def test_load_bool_fix_object_int(bool_fix_tester_loader):
    text = 'x: 42'
    data = yaml.load(text, Loader=bool_fix_tester_loader)
    assert isinstance(data.x, int)
    assert data.x == 42


@pytest.fixture
def bool_tester_dumper():
    class BoolTesterDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(BoolTesterDumper, BoolTester)
    return BoolTesterDumper


@pytest.fixture
def bool_fix_tester_dumper():
    class BoolFixTesterDumper(yatiml.Dumper):
        pass
    yatiml.add_to_dumper(BoolFixTesterDumper, BoolFixTester)
    return BoolFixTesterDumper


def test_dump_object_bool(bool_tester_dumper):
    data = BoolTester(True)
    text = yaml.dump(data, Dumper=bool_tester_dumper)
    assert text == 'x: true\n'


def test_dump_object_int(bool_tester_dumper):
    data = BoolTester(21)
    text = yaml.dump(data, Dumper=bool_tester_dumper)
    assert text == 'x: 21\n'


def test_dump_object_bool_fix(bool_fix_tester_dumper):
    data = BoolFixTester(True)
    text = yaml.dump(data, Dumper=bool_fix_tester_dumper)
    assert text == 'x: true\n'


def test_dump_object_int_fix(bool_fix_tester_dumper):
    data = BoolFixTester(21)
    text = yaml.dump(data, Dumper=bool_fix_tester_dumper)
    assert text == 'x: 21\n'
