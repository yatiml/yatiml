from typing import Dict, List

import pytest

import yatiml


def test_load_from_string():
    load_int_dict = yatiml.load_function(Dict[str, int])
    data = load_int_dict('x: 1')
    assert data['x'] == 1

    load_float_list = yatiml.load_function(List[float])
    data = load_float_list('[7.8, 9.1]')
    assert data[1] == 9.1

    with pytest.raises(yatiml.RecognitionError):
        load_float_list('x: 1')


def test_load_from_path(tmp_path):
    tmp_file = tmp_path / 'test_load_from_path.yaml'   # is a pathlib.Path
    with tmp_file.open('w') as f:
        f.write('y: z')

    load_string_dict = yatiml.load_function(Dict[str, str])
    data = load_string_dict(tmp_file)
    assert data['y'] == 'z'


def test_load_from_stream(tmp_path):
    tmp_file = tmp_path / 'test_load_from_stream.yaml'  # is a pathlib.Path
    with tmp_file.open('w') as f:
        f.write('testing')

    load_string = yatiml.load_function(str)
    with tmp_file.open('r') as f:
        data = load_string(f)
    assert data == 'testing'

    with tmp_file.open('rb') as f:
        data = load_string(f)
    assert data == 'testing'


def test_dump_to_string():
    dumps = yatiml.dumps_function()
    yaml_text = dumps({'x': 1})
    assert yaml_text == 'x: 1\n'


def test_dump_to_stream(tmp_path):
    tmp_file = tmp_path / 'test.yaml'
    dump = yatiml.dump_function()
    with tmp_file.open('w') as f:
        dump({'a': 1.5}, f)

    with tmp_file.open('r') as f:
        assert f.read() == 'a: 1.5\n'


def test_dump_to_filename(tmp_path):
    tmp_file = tmp_path / 'test.yaml'
    dump = yatiml.dump_function()
    dump({'a': 1.5}, str(tmp_file))

    with tmp_file.open('r') as f:
        assert f.read() == 'a: 1.5\n'


def test_dump_to_path(tmp_path):
    tmp_file = tmp_path / 'test.yaml'
    dump = yatiml.dump_function()
    dump({'a': 1.5}, tmp_file)

    with tmp_file.open('r') as f:
        assert f.read() == 'a: 1.5\n'


def test_dump_json_to_string():
    dumps_json = yatiml.dumps_json_function()
    json_text = dumps_json({'x': 1})
    assert json_text == '{"x":1}'

    json_text = dumps_json({'x': 2}, indent=4)
    assert json_text == (
            '{\n'
            '    "x": 2\n'
            '}\n')

    json_text = dumps_json('\u0410\u043d\u043d\u0430')
    assert json_text == '"\\u0410\\u043d\\u043d\\u0430"'

    json_text = dumps_json('\u0410\u043d\u043d\u0430', ensure_ascii=False)
    assert json_text == '"\u0410\u043d\u043d\u0430"'


def test_dump_json_to_stream(tmp_path):
    tmp_file = tmp_path / 'test.json'
    dump = yatiml.dump_json_function()
    with tmp_file.open('w') as f:
        dump({'a': 1.5}, f)

    with tmp_file.open('r') as f:
        assert f.read() == '{"a":1.5}'


def test_dump_json_to_filename(tmp_path):
    tmp_file = tmp_path / 'test.yaml'
    dump = yatiml.dump_json_function()
    dump({'a': 1.5}, str(tmp_file))

    with tmp_file.open('r') as f:
        assert f.read() == '{"a":1.5}'

    dump({'a': 3.5}, str(tmp_file), indent=2)
    with tmp_file.open('r') as f:
        assert f.read() == (
                '{\n'
                '  "a": 3.5\n'
                '}\n')

    dump('\u0410\u043d\u043d\u0430', str(tmp_file))
    with tmp_file.open('r') as f:
        assert f.read() == '"\\u0410\\u043d\\u043d\\u0430"'

    dump('\u0410\u043d\u043d\u0430', str(tmp_file), ensure_ascii=False)
    with tmp_file.open('r') as f:
        assert f.read() == '"\u0410\u043d\u043d\u0430"'


def test_dump_json_to_path(tmp_path):
    tmp_file = tmp_path / 'test.yaml'
    dump = yatiml.dump_json_function()
    dump({'a': 1.5}, tmp_file)

    with tmp_file.open('r') as f:
        assert f.read() == '{"a":1.5}'
