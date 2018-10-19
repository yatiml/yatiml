import yatiml

from ruamel import yaml
import pytest


def test_require_attribute(unknown_node):
    unknown_node.require_attribute('attr1')
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('non_existent_attribute')

    unknown_node.require_attribute('attr1', int)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('attr1', str)

    unknown_node.require_attribute('null_attr', None)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('attr1', None)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute('null_attr', int)


def test_require_attribute_value(unknown_node):
    unknown_node.require_attribute_value('attr1', 42)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('attr1', 43)
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('attr1', 'test')
    with pytest.raises(yatiml.RecognitionError):
        unknown_node.require_attribute_value('non_existent_attribute', 'test')


def test_has_attribute(class_node):
    assert class_node.has_attribute('attr1')
    assert not class_node.has_attribute('non_existent_attribute')


def test_has_attribute_type(class_node):
    assert class_node.has_attribute_type('attr1', int)
    assert not class_node.has_attribute_type('attr1', float)
    assert not class_node.has_attribute_type('non_existent_attribute', int)
    assert class_node.has_attribute_type('list1', list)
    with pytest.raises(ValueError):
        class_node.has_attribute_type('list1', yaml)


def test_get_attribute(class_node):
    assert class_node.get_attribute('attr1').value == 42
    with pytest.raises(yatiml.SeasoningError):
        class_node.get_attribute('non_existent_attribute')


def test_set_attribute(class_node):
    assert class_node.get_attribute('attr1').value == 42

    class_node.set_attribute('attr1', 43)
    assert class_node.get_attribute('attr1').tag == 'tag:yaml.org,2002:int'
    assert class_node.get_attribute('attr1').value == '43'
    assert class_node.get_attribute('attr1').start_mark is not None
    assert class_node.get_attribute('attr1').end_mark is not None

    class_node.set_attribute('attr1', 'test')
    assert class_node.get_attribute('attr1').tag == 'tag:yaml.org,2002:str'
    assert class_node.get_attribute('attr1').value == 'test'
    assert class_node.get_attribute('attr1').start_mark is not None
    assert class_node.get_attribute('attr1').end_mark is not None

    class_node.set_attribute('attr1', 3.14)
    assert class_node.get_attribute('attr1').tag == 'tag:yaml.org,2002:float'
    assert class_node.get_attribute('attr1').value == '3.14'
    assert class_node.get_attribute('attr1').start_mark is not None
    assert class_node.get_attribute('attr1').end_mark is not None

    class_node.set_attribute('attr1', True)
    assert class_node.get_attribute('attr1').tag == 'tag:yaml.org,2002:bool'
    assert class_node.get_attribute('attr1').value == 'true'
    assert class_node.get_attribute('attr1').start_mark is not None
    assert class_node.get_attribute('attr1').end_mark is not None

    class_node.set_attribute('attr1', None)
    assert class_node.get_attribute('attr1').tag == 'tag:yaml.org,2002:null'
    assert class_node.get_attribute('attr1').value == ''
    assert class_node.get_attribute('attr1').start_mark is not None
    assert class_node.get_attribute('attr1').end_mark is not None

    assert not class_node.has_attribute('attr2')
    class_node.set_attribute('attr2', 'testing')
    assert class_node.get_attribute('attr2').value == 'testing'
    assert class_node.get_attribute('attr2').start_mark is not None
    assert class_node.get_attribute('attr2').end_mark is not None

    node = yaml.ScalarNode('tag:yaml.org,2002:str', 'testnode')
    class_node.set_attribute('attr3', node)
    assert class_node.get_attribute('attr3') == node

    with pytest.raises(TypeError):
        class_node.set_attribute('attr4', class_node)


def test_remove_attribute(class_node):
    assert class_node.has_attribute('attr1')
    class_node.remove_attribute('attr1')
    assert not class_node.has_attribute('attr1')

    class_node.set_attribute('attr1', 10)
    class_node.set_attribute('attr2', 11)
    assert class_node.has_attribute('attr2')
    class_node.remove_attribute('attr2')
    assert not class_node.has_attribute('attr2')

    class_node.remove_attribute('attr2')
    assert not class_node.has_attribute('attr2')


def test_rename_attribute(class_node):
    assert class_node.has_attribute('attr1')
    assert not class_node.has_attribute('attr2')
    attr1_value = class_node.get_attribute('attr1')
    class_node.rename_attribute('attr1', 'attr2')
    assert not class_node.has_attribute('attr1')
    assert class_node.has_attribute('attr2')
    assert class_node.get_attribute('attr2') == attr1_value

    # make sure that this does not raise
    class_node.rename_attribute('non_existent_attribute', 'attr3')


def test_seq_attribute_to_map(class_node, class_node_dup_key):
    assert class_node.has_attribute_type('list1', list)

    class_node.seq_attribute_to_map('list1', 'item_id')

    assert class_node.has_attribute_type('list1', dict)
    attr_node = class_node.get_attribute('list1')
    assert isinstance(attr_node, yaml.MappingNode)
    attr_cnode = yatiml.ClassNode(attr_node)

    assert attr_cnode.has_attribute_type('item1', dict)
    item1_cnode = yatiml.ClassNode(attr_cnode.get_attribute('item1'))
    assert not item1_cnode.has_attribute('item_id')
    assert item1_cnode.has_attribute('price')

    assert attr_cnode.has_attribute_type('item2', dict)
    item2_cnode = yatiml.ClassNode(attr_cnode.get_attribute('item2'))
    assert not item2_cnode.has_attribute('item_id')
    assert item2_cnode.has_attribute('price')

    # check that it fails silently if the attribute is missing or not a list
    class_node.seq_attribute_to_map('non_existent_attribute', 'item_id')
    class_node.seq_attribute_to_map('attr1', 'item_id')

    # check that it raises with strict=True and duplicate keys
    with pytest.raises(yatiml.SeasoningError):
        class_node_dup_key.seq_attribute_to_map('dup_list', 'item_id', True)


def test_map_attribute_to_seq(class_node):
    assert class_node.has_attribute_type('dict1', dict)

    class_node.map_attribute_to_seq('dict1', 'item_id')

    assert class_node.has_attribute_type('dict1', list)
    attr_node = class_node.get_attribute('dict1')

    assert len(attr_node.value) == 2
    first_item_cnode = yatiml.ClassNode(attr_node.value[0])
    assert first_item_cnode.has_attribute('item_id')
    assert first_item_cnode.has_attribute('price')
    first_item_id = first_item_cnode.get_attribute('item_id').value

    second_item_cnode = yatiml.ClassNode(attr_node.value[1])
    assert second_item_cnode.has_attribute('item_id')
    assert second_item_cnode.has_attribute('price')
    second_item_id = second_item_cnode.get_attribute('item_id').value

    assert ((first_item_id == 'item1' and second_item_id == 'item2') or
            (first_item_id == 'item2' and second_item_id == 'item1'))
