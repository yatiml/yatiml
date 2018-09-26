from ruamel import yaml
from typing import Dict, Union
import yatiml


# Create loader
class MyLoader(yatiml.Loader):
  pass

yatiml.set_document_type(MyLoader, Dict[str, Union[str, int]])

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = yaml.load(yaml_text, Loader=MyLoader)
print(doc)
