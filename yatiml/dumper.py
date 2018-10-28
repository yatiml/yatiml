import enum
import logging
from collections import UserString
from typing import List, Type

from ruamel import yaml

from yatiml.representers import (EnumRepresenter, Representer,
                                 UserStringRepresenter)

logger = logging.getLogger(__name__)


class Dumper(yaml.RoundTripDumper):
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
        classes = [classes]  # type: ignore
    for class_ in classes:
        if issubclass(class_, enum.Enum):
            dumper.add_representer(class_, EnumRepresenter(class_))
        elif issubclass(class_, str) or issubclass(class_, UserString):
            dumper.add_representer(class_, UserStringRepresenter(class_))
        else:
            dumper.add_representer(class_, Representer(class_))
