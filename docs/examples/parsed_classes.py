from typing import List

from ruamel import yaml

import yatiml


class Identifier:
    def __init__(self, namespaces: List[str], name: str) -> None:
        self.namespaces = namespaces
        self.name = name

    @classmethod
    def _yatiml_recognize(cls, node: yatiml.UnknownNode) -> None:
        node.require_scalar(str)

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        text = str(node.get_value())
        parts = text.split('.')
        node.make_mapping()

        # We need to make a yaml.SequenceNode by hand here, since
        # set_attribute doesn't take lists as an argument.
        start_mark = yaml.error.StreamMark('generated node', 0, 0, 0)
        end_mark = yaml.error.StreamMark('generated node', 0, 0, 0)
        item_nodes = list()
        for part in parts[:-1]:
            item_nodes.append(yaml.ScalarNode('tag:yaml.org,2002:str', part,
                                              start_mark, end_mark))
        ynode = yaml.SequenceNode('tag:yaml.org,2002:seq', item_nodes,
                                  start_mark, end_mark)
        node.set_attribute('namespaces', ynode)
        node.set_attribute('name', parts[-1])

    @classmethod
    def _yatiml_sweeten(self, node: yatiml.Node) -> None:
        namespace_nodes = node.get_attribute('namespaces').seq_items()
        namespaces = list(map(yatiml.Node.get_value, namespace_nodes))
        namespace_str = '.'.join(namespaces)

        name = node.get_attribute('name').get_value()
        node.set_value('{}.{}'.format(namespace_str, name))


class MyLoader(yatiml.Loader):
    pass


yatiml.add_to_loader(MyLoader, Identifier)
yatiml.set_document_type(MyLoader, Identifier)


class MyDumper(yatiml.Dumper):
    pass


yatiml.add_to_dumper(MyDumper, Identifier)


yaml_text = ('yatiml.logger.setLevel\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(type(doc))
print(doc.namespaces)
print(doc.name)

doc = Identifier(['yatiml'], 'add_to_loader')
yaml_text = yaml.dump(doc, Dumper=MyDumper)

print(yaml_text)
