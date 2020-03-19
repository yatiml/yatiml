from ruamel import yaml
from typing import Union
import yatiml


# Create document class
class Dashed:
    def __init__(self, an_attribute: int, another_attribute: str) -> None:
        self.an_attribute = an_attribute
        self.another_attribute = another_attribute

    @classmethod
    def _yatiml_savorize(cls, node: yatiml.Node) -> None:
        node.dashes_to_unders_in_keys()

    @classmethod
    def _yatiml_sweeten(cls, node: yatiml.Node) -> None:
        node.unders_to_dashes_in_keys()


# Create loader
class MyLoader(yatiml.Loader):
    pass

yatiml.add_to_loader(MyLoader, Dashed)
yatiml.set_document_type(MyLoader, Dashed)


# Create dumper
class MyDumper(yatiml.Dumper):
    pass

yatiml.add_to_dumper(MyDumper, Dashed)


# Load YAML
yaml_text = ('an-attribute: 42\n'
             'another-attribute: with-dashes\n')
doc = yaml.load(yaml_text, Loader=MyLoader)

print(type(doc))
print(doc.an_attribute)
print(doc.another_attribute)


# Dump YAML

dumped_text = yaml.dump(doc, Dumper=MyDumper)
print(dumped_text)
