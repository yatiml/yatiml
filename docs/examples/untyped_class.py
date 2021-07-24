import yatiml


class Submission:
    def __init__(self, name, age):
        self.name = name
        self.age = age

load = yatiml.load_function(Submission)

yaml_text = ('name: Janice\n'
             'age: 6\n')
doc = load(yaml_text)

print(type(doc))
print(doc.name)
print(doc.age)
