from collections import UserString
import enum
import logging
from typing import Dict, GenericMeta, List, Type

from ruamel import yaml

from yatiml.exceptions import RecognitionError
from yatiml.helpers import ClassNode, UnknownNode
from yatiml.introspection import class_subobjects
from yatiml.irecognizer import IRecognizer
from yatiml.util import scalar_type_to_tag

logger = logging.getLogger(__name__)


class Recognizer(IRecognizer):
    """Functions for recognizing objects as types."""

    def __init__(self, registered_classes: Dict[str, Type]) -> None:
        """Create a RecognizerImpl.

        Args:
            registered_classes: The registered tags and corresponding \
                    classes.
        """
        self.__registered_classes = registered_classes

    def __recognize_scalar(self, node: yaml.Node,
                           expected_type: Type) -> List[Type]:
        """Recognize a node that we expect to be a scalar.

        Args:
            node: The node to recognize.
            expected_type: The type it is expected to be.

        Returns:
            A list of recognized types
        """
        logger.debug('Recognizing as a scalar')
        if (isinstance(node, yaml.ScalarNode)
                and node.tag == scalar_type_to_tag[expected_type]):
            return [expected_type]
        return []

    def __recognize_list(self, node: yaml.Node,
                         expected_type: Type) -> List[Type]:
        """Recognize a node that we expect to be a list of some kind.

        Args:
            node: The node to recognize.
            expected_type: List[...something...]

        Returns
            expected_type if it was recognized, [] otherwise.
        """
        logger.debug('Recognizing as a list')
        if not isinstance(node, yaml.SequenceNode):
            return []
        item_type = expected_type.__args__[0]
        for item in node.value:
            recognized_types = self.recognize(item, item_type)
            if len(recognized_types) == 0:
                return []
            if len(recognized_types) > 1:
                return [List[t] for t in recognized_types]  # type: ignore

        return [expected_type]

    def __recognize_dict(self, node: yaml.Node,
                         expected_type: Type) -> List[Type]:
        """Recognize a node that we expect to be a dict of some kind.

        Args:
            node: The node to recognize.
            expected_type: Dict[str, ...something...]

        Returns:
            expected_type if it was recognized, [] otherwise.
        """
        logger.debug('Recognizing as a dict')
        if not issubclass(expected_type.__args__[0], str):
            raise RuntimeError(
                'YAtiML only supports dicts with strings as keys')
        if not isinstance(node, yaml.MappingNode):
            return []
        value_type = expected_type.__args__[1]
        for key, value in node.value:
            recognized_value_types = self.recognize(value, value_type)
            if len(recognized_value_types) == 0:
                return []
            if len(recognized_value_types) > 1:
                return [
                    Dict[str, t]  # type: ignore
                    for t in recognized_value_types
                ]  # type: ignore

        return [expected_type]

    def __recognize_union(self, node: yaml.Node,
                          expected_type: Type) -> List[Type]:
        """Recognize a node that we expect to be one of a union of types.

        Args:
            node: The node to recognize.
            expected_type: Union[...something...]

        Returns:
            The specific type that was recognized, multiple, or none.
        """
        logger.debug('Recognizing as a union')
        recognized_types = []
        if hasattr(expected_type, '__union_set_params__'):
            union_types = expected_type.__union_set_params__
        else:
            union_types = expected_type.__args__
        logger.debug('Union types {}'.format(union_types))
        for possible_type in union_types:
            recognized_types.extend(self.recognize(node, possible_type))
        recognized_types = list(set(recognized_types))
        return recognized_types

    def __recognize_user_class(self, node: yaml.Node,
                               expected_type: Type) -> List[Type]:
        """Recognize a user-defined class in the node.

        This tries to recognize only exactly the specified class. It \
        recurses down into the class's attributes, but not to its \
        subclasses. See also __recognize_user_classes().

        Args:
            node The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing the user-defined class, or an empty list.
        """
        logger.debug('Recognizing as a user-defined class')
        if hasattr(expected_type, 'yatiml_recognize'):
            try:
                unode = UnknownNode(self, node)
                expected_type.yatiml_recognize(unode)
                return [expected_type]
            except RecognitionError:
                return []
        else:
            if issubclass(expected_type, enum.Enum):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    return []
            elif (issubclass(expected_type, UserString)
                  or issubclass(expected_type, str)):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    return []
            else:
                # auto-recognize based on constructor signature
                if not isinstance(node, yaml.MappingNode):
                    return []

                for attr_name, type_, required in class_subobjects(
                        expected_type):
                    cnode = ClassNode(node)
                    if cnode.has_attribute(attr_name):
                        subnode = cnode.get_attribute(attr_name)
                        recognized_types = self.recognize(subnode, type_)
                        if len(recognized_types) == 0:
                            return []
                    elif required:
                        return []

            return [expected_type]

    def __recognize_user_classes(self, node: yaml.Node,
                                 expected_type: Type) -> List[Type]:
        """Recognize a user-defined class in the node.

        This returns a list of classes from the inheritance hierarchy \
        headed by expected_type which match the given node and which \
        do not have a registered derived class that matches the given \
        node. So, the returned classes are the most derived matching \
        classes that inherit from expected_type.

        This function recurses down the user's inheritance hierarchy.

        Args:
            node: The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing matched user-defined classes.
        """
        # Let the user override with an explicit tag
        if node.tag in self.__registered_classes:
            return [self.__registered_classes[node.tag]]

        recognized_subclasses = []
        for other_class in self.__registered_classes.values():
            if expected_type in other_class.__bases__:
                sub_subclasses = self.__recognize_user_classes(
                    node, other_class)
                recognized_subclasses.extend(sub_subclasses)

        if len(recognized_subclasses) == 0:
            recognized_subclasses = self.__recognize_user_class(
                node, expected_type)

        return recognized_subclasses

    def recognize(self, node: yaml.Node, expected_type: Type) -> List[Type]:
        """Figure out how to interpret this node.

        This is not quite a type check. This function makes a list of \
        all types that match the expected type and also the node, and \
        returns that list. The goal here is not to test validity, but \
        to determine how to process this node further.

        That said, it will recognize built-in types only in case of \
        an exact match.

        Args:
            node: The YAML node to recognize.
            expected_type: The type we expect this node to be, based \
                    on the context provided by our type definitions.

        Returns:
            A list of matching types.
        """
        logger.debug('Recognizing {} as a {}'.format(node, expected_type))
        recognized_types = None
        if expected_type in [str, int, float, bool, None, type(None)]:
            recognized_types = self.__recognize_scalar(node, expected_type)
        elif type(expected_type).__name__ in ['UnionMeta', '_Union']:
            recognized_types = self.__recognize_union(node, expected_type)
        elif isinstance(expected_type, GenericMeta):
            if expected_type.__origin__ == List:
                recognized_types = self.__recognize_list(node, expected_type)
            elif expected_type.__origin__ == Dict:
                recognized_types = self.__recognize_dict(node, expected_type)
        elif expected_type in self.__registered_classes.values():
            recognized_types = self.__recognize_user_classes(
                node, expected_type)

        if recognized_types is None:
            raise RecognitionError(
                ('Could not recognize for type {},'
                 ' is it registered?').format(expected_type))
        logger.debug('Recognized types {} matching {}'.format(
            recognized_types, expected_type))
        return recognized_types
