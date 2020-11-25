"""Tests for supported additional types."""
from pathlib import Path

import yatiml


class WithPath:
    def __init__(self, path: Path) -> None:
        self.path = path


def test_load_abs_path() -> None:
    load = yatiml.load_function(Path)
    data = load('/tmp/testing.txt')
    assert isinstance(data, Path)
    assert data == Path('/tmp/testing.txt')


def test_load_rel_path() -> None:
    load = yatiml.load_function(Path)
    data = load('dir/testing.txt')
    assert isinstance(data, Path)
    assert data == Path('dir/testing.txt')


def test_load_with_path() -> None:
    load = yatiml.load_function(WithPath)
    data = load('path: /etc')
    assert isinstance(data, WithPath)
    assert isinstance(data.path, Path)
    assert data.path == Path('/etc')


def test_dump_abs_path() -> None:
    dumps = yatiml.dumps_function()
    text = dumps(Path('/tmp/testing.txt'))
    assert text == '/tmp/testing.txt\n...\n'


def test_dump_rel_path() -> None:
    dumps = yatiml.dumps_function()
    text = dumps(Path('dir/testing.txt'))
    assert text == 'dir/testing.txt\n...\n'


def test_dump_with_path() -> None:
    dumps = yatiml.dumps_function(WithPath)
    data = WithPath(Path('dir/subdir/test.txt'))
    text = dumps(data)
    assert text == 'path: dir/subdir/test.txt\n'


def test_dump_path_json() -> None:
    dumps = yatiml.dumps_json_function()
    text = dumps(Path('/tmp/testing.txt'))
    assert text == '"/tmp/testing.txt"'
