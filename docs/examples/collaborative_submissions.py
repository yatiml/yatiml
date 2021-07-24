from typing import Dict, List
import yatiml


class Submission:
    def __init__(self, name: List[str], age: Dict[str, int]) -> None:
        self.name = name
        self.age = age

load = yatiml.load_function(Submission)

yaml_text = (
        'name:\n'
        '- Janice\n'
        '- Eve\n'
        'age:\n'
        '  Janice: 6\n'
        '  Eve: 5\n')

doc = load(yaml_text)

print(type(doc))
print(doc.name)
print(doc.age)
