from ruamel import yaml
from typing import Dict
import yatiml


# Create loader
class MyLoader(yatiml.Loader):
  pass

yatiml.set_document_type(MyLoader, Dict[str, str])

# Load YAML
yaml_text = ('name: Janice\n'
             'age: Six\n')
doc = yaml.load(yaml_text, Loader=MyLoader)
print(doc)
