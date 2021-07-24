import yatiml


yaml_text = (
        'name: Janice\n'
        'age: 6\n')

load = yatiml.load_function()
doc = load(yaml_text)

print(doc)
