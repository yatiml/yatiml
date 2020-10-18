from typing import Dict
import yatiml


# Create loader
load = yatiml.load_function(Dict[str, str])

# Load YAML
yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = load(yaml_text)
print(doc)
