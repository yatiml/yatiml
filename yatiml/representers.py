import inspect
import logging
from typing import TYPE_CHECKING, Any, Type

from ruamel import yaml

from yatiml.helpers import Node

if TYPE_CHECKING:
    from yatiml.dumper import Dumper  # noqa: F401

logger = logging.getLogger(__name__)


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
        logger.info('Representing {} of class {}'.format(
            data, self.class_.__name__))
        if hasattr(data, 'yatiml_attributes'):
            logger.debug('Found yatiml_attributes()')
            attributes = data.yatiml_attributes()
            if attributes is None:
                raise RuntimeError(('{}.yatiml_attributes() returned None,'
                                    ' where a dict was expected.').format(
                                        self.class_.__name__))
        else:
            logger.debug(
                'No yatiml_attributes() found, using public attributes')
            argspec = inspect.getfullargspec(data.__init__)
            attribute_names = list(argspec.args[1:])
            attrs = [(name, getattr(data, name)) for name in attribute_names
                     if name != 'yatiml_extra']
            if 'yatiml_extra' in attribute_names:
                if not hasattr(data, 'yatiml_extra'):
                    raise RuntimeError(
                        ('Class {} takes yatiml_extra but has '
                         ' no yatiml_extra attribute, and no '
                         ' yatiml_attributes().').format(self.class_.__name__))
                attrs.extend(data.yatiml_extra.items())
            attributes = yaml.comments.CommentedMap(attrs)

        # convert to a yaml.MappingNode
        represented = dumper.represent_mapping('tag:yaml.org,2002:map',
                                               attributes)

        # sweeten
        cnode = Node(represented)
        self.__sweeten(dumper, self.class_, cnode)
        represented = cnode.yaml_node

        logger.debug('End representing {}'.format(data))
        return represented

    def __sweeten(self, dumper: 'Dumper', class_: Type, node: Node) -> None:
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
                logger.debug('Sweetening for class {}'.format(
                    self.class_.__name__))
                self.__sweeten(dumper, base_class, node)
        if hasattr(class_, 'yatiml_sweeten'):
            class_.yatiml_sweeten(node)


class EnumRepresenter:
    """A yaml Representer class for user-defined enum types.

    For ruamel.yaml to dump a class correctly, it needs a representer \
    function for that class. YAtiML provides this generic representer \
    which represents enum classes based on the names of their values by \
    default, with an optional user override using a member function.
    """

    def __init__(self, class_: Type) -> None:
        """Creates a new Representer for the given class.

        Args:
            class_: The class to represent.
        """
        self.class_ = class_

    def __call__(self, dumper: 'Dumper', data: Any) -> yaml.ScalarNode:
        """Represents the class as a ScalarNode.

        Args:
            dumper: The dumper to use.
            data: The user-defined object to dump.

        Returns:
            A yaml.Node representing the object.
        """
        # make a ScalarNode of type str with name of value
        logger.info('Representing {} of class {}'.format(
            data, self.class_.__name__))

        # convert to a yaml.ScalarNode
        start_mark = yaml.error.StreamMark('Generated node', 0, 0, 0)
        end_mark = start_mark
        represented = yaml.nodes.ScalarNode(
                'tag:yaml.org,2002:str', data.name, start_mark, end_mark)

        # sweeten
        snode = Node(represented)
        if hasattr(self.class_, 'yatiml_sweeten'):
            self.class_.yatiml_sweeten(snode)
            represented = snode.yaml_node

        logger.debug('End representing {}'.format(data))
        return represented


class UserStringRepresenter:
    """A yaml Representer class for user-defined string types.

    For ruamel.yaml to dump a class correctly, it needs a representer \
    function for that class. YAtiML provides this generic representer \
    which represents user-defined string classes as strings.
    """

    def __init__(self, class_: Type) -> None:
        """Creates a new Representer for the given class.

        Args:
            class_: The class to represent.
        """
        self.class_ = class_

    def __call__(self, dumper: 'Dumper', data: Any) -> yaml.MappingNode:
        """Represents the class as a ScalarNode.

        Args:
            dumper: The dumper to use.
            data: The user-defined object to dump.

        Returns:
            A yaml.ScalarNode representing the object.
        """
        # make a ScalarNode of type str with name of value
        logger.info('Representing {} of class {}'.format(
            data, self.class_.__name__))

        # convert to a yaml.ScalarNode
        represented = dumper.represent_str(str(data))

        # sweeten
        snode = Node(represented)
        if hasattr(self.class_, 'yatiml_sweeten'):
            self.class_.yatiml_sweeten(snode)
            represented = snode.yaml_node

        logger.debug('End representing {}'.format(data))
        return represented
