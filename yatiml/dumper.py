import inspect
from typing import Any, List, Type

from ruamel import yaml

from yatiml.helpers import ClassNode


class Representer:
    """A yaml Representer class for user-defined types.

    For ruamel.yaml to dump a class correctly, it needs a representer \
    function for that class. YAtiML provides this generic representer \
    which represents classes based on their public attributes by \
    default, with an optional user override using a member function.
    """
    def __init__(self, class_: Type) -> None:
        """Creates a new Representer for the given class.

        Args:
            class_: The class to represent.
        """
        self.class_ = class_

    def __call__(self, dumper: 'Dumper', data: Any) -> yaml.MappingNode:
        """Represents the class as a MappingNode.

        Args:
            dumper: The dumper to use.
            data: The user-defined object to dump.

        Returns:
            A yaml.Node representing the object.
        """
        # make a dict with attributes
        if hasattr(data, 'yatiml_attributes'):
            attributes = data.yatiml_attributes()
            if attributes is None:
                raise RuntimeError(('{}.yatiml_attributes() returned None,'
                    ' where a dict was expected.').format(self.class_.__name__))
        else:
            argspec = inspect.getfullargspec(data.__init__)
            attribute_names = list(argspec.args[1:])
            attributes = {name: getattr(data, name) for name in attribute_names}

        # convert to a yaml.MappingNode
        represented = dumper.represent_mapping('tag:yaml.org,2002:map', attributes)

        # sweeten
        cnode = ClassNode(represented)
        self.__sweeten(dumper, self.class_, cnode)

        return represented

    def __sweeten(
            self, dumper: 'Dumper',
            class_: Type, represented_object: Any) -> None:
        """Applies the user's yatiml_sweeten() function(s), if any.

        Sweetening is done for the base classes first, then for the \
        derived classes, down the hierarchy to the class we're \
        constructing.

        Args:
            dumper: The dumper that is dumping this object.
            class_: The type of the object to be dumped.
            represented_object: The object to be dumped.
        """
        for base_class in class_.__bases__:
            if base_class in dumper.yaml_representers:
                self.__sweeten(dumper, base_class, represented_object)
        if hasattr(class_, 'yatiml_sweeten'):
            class_.yatiml_sweeten(represented_object)


class Dumper(yaml.Dumper):
    """The YAtiML Dumper class.

    Derive your own Dumper class from this one, then add classes to it \
    using add_to_dumper().
    """
    pass


# Python errors if we define classes as Union[List[Type], Type]
# So List[Type] it is, and if the user ignores that and passes
# a single class, it'll work anyway, with a little mypy override.
def add_to_dumper(dumper: Type, classes: List[Type]) -> None:
    """Register user-defined classes with the Dumper.

    This enables the Dumper to write objects of your classes to a \
    YAML file. Note that all the arguments are types, not instances!

    Args:
        dumper: Your dumper class(!), derived from yatiml.Dumper
        classes: One or more classes to add.
    """
    if not isinstance(classes, list):
        classes = [classes]     # type: ignore
    for class_ in classes:
        dumper.add_representer(class_, Representer(class_))
