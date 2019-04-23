import enum
import logging
import os
from collections import UserString
from datetime import datetime
from textwrap import indent
from typing import Dict, List, Type

from ruamel import yaml

from yatiml.exceptions import RecognitionError
from yatiml.helpers import Node, UnknownNode
from yatiml.introspection import class_subobjects
from yatiml.irecognizer import IRecognizer, RecResult
from yatiml.util import (generic_type_args, is_generic_dict, is_generic_list,
                         is_generic_union, scalar_type_to_tag, type_to_desc,
                         bool_union_fix)

logger = logging.getLogger(__name__)


class Recognizer(IRecognizer):
    """Functions for recognizing objects as types."""

    def __init__(self, registered_classes: Dict[str, Type]) -> None:
        """Create a Recognizer.

        Args:
            registered_classes: The registered tags and corresponding \
                    classes.
        """
        self.__registered_classes = registered_classes

    def __recognize_scalar(self, node: yaml.Node,
                           expected_type: Type) -> RecResult:
        """Recognize a node that we expect to be a scalar.

        Args:
            node: The node to recognize.
            expected_type: The type it is expected to be.

        Returns:
            A list of recognized types and an error message
        """
        logger.debug('Recognizing as a scalar')
        if (isinstance(node, yaml.ScalarNode)
                and node.tag == scalar_type_to_tag[expected_type]):
            return [expected_type], ''
        message = 'Failed to recognize a {}\n{}\n'.format(
            type_to_desc(expected_type), node.start_mark)
        return [], message

    def __recognize_list(self, node: yaml.Node,
                         expected_type: Type) -> RecResult:
        """Recognize a node that we expect to be a list of some kind.

        Args:
            node: The node to recognize.
            expected_type: List[...something...]

        Returns
            expected_type and the empty string if it was recognized,
                    [] and an error message otherwise.
        """
        logger.debug('Recognizing as a list')
        if not isinstance(node, yaml.SequenceNode):
            message = '{}{}Expected a list here.'.format(
                node.start_mark, os.linesep)
            return [], message
        item_type = generic_type_args(expected_type)[0]
        for item in node.value:
            recognized_types, message = self.recognize(item, item_type)
            if len(recognized_types) == 0:
                return [], message
            if len(recognized_types) > 1:
                recognized_types = [
                    List[t]  # type: ignore
                    for t in recognized_types
                ]
                return recognized_types, message

        return [expected_type], ''

    def __recognize_dict(self, node: yaml.Node,
                         expected_type: Type) -> RecResult:
        """Recognize a node that we expect to be a dict of some kind.

        Args:
            node: The node to recognize.
            expected_type: Dict[str, ...something...]

        Returns:
            expected_type if it was recognized, [] otherwise.
        """
        logger.debug('Recognizing as a dict')
        if not issubclass(generic_type_args(expected_type)[0], str):
            raise RuntimeError(
                'YAtiML only supports dicts with strings as keys')
        if not isinstance(node, yaml.MappingNode):
            message = '{}{}Expected a dict/mapping here'.format(
                node.start_mark, os.linesep)
            return [], message
        value_type = generic_type_args(expected_type)[1]
        for _, value in node.value:
            recognized_value_types, message = self.recognize(value, value_type)
            if len(recognized_value_types) == 0:
                return [], message
            if len(recognized_value_types) > 1:
                return [
                    Dict[str, t]  # type: ignore
                    for t in recognized_value_types
                ], message  # type: ignore

        return [expected_type], ''

    def __recognize_union(self, node: yaml.Node,
                          expected_type: Type) -> RecResult:
        """Recognize a node that we expect to be one of a union of types.

        Args:
            node: The node to recognize.
            expected_type: Union[...something...]

        Returns:
            The specific type that was recognized, multiple, or none.
        """
        logger.debug('Recognizing as a union')
        recognized_types = []
        message = ''
        union_types = generic_type_args(expected_type)
        logger.debug('Union types {}'.format(union_types))
        for possible_type in union_types:
            recognized_type, msg = self.recognize(node, possible_type)
            if len(recognized_type) == 0:
                message += msg
            recognized_types.extend(recognized_type)
        recognized_types = list(set(recognized_types))
        if bool in recognized_types and bool_union_fix in recognized_types:
            recognized_types.remove(bool_union_fix)

        if len(recognized_types) == 0:
            return recognized_types, message
        elif len(recognized_types) > 1:
            message = ('{}{}Could not determine which of the following types'
                       ' this is: {}').format(node.start_mark, os.linesep,
                                              recognized_types)
            return recognized_types, message

        return recognized_types, ''

    def __recognize_user_class(self, node: yaml.Node,
                               expected_type: Type) -> RecResult:
        """Recognize a user-defined class in the node.

        This tries to recognize only exactly the specified class. It \
        recurses down into the class's attributes, but not to its \
        subclasses. See also __recognize_user_classes().

        Args:
            node: The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing the user-defined class, or an empty list.
        """
        logger.debug('Recognizing as a user-defined class')
        loc_str = '{}{}'.format(node.start_mark, os.linesep)
        if hasattr(expected_type, 'yatiml_recognize'):
            try:
                unode = UnknownNode(self, node)
                expected_type.yatiml_recognize(unode)
                return [expected_type], ''
            except RecognitionError as e:
                if len(e.args) > 0:
                    message = ('Error recognizing a {}\n{}because of the'
                               ' following error(s): {}').format(
                                   expected_type.__class__, loc_str,
                                   indent(e.args[0], '    '))
                else:
                    message = 'Error recognizing a {}\n{}'.format(
                        expected_type.__class__, loc_str)
                return [], message
        else:
            if issubclass(expected_type, enum.Enum):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    message = 'Expected an enum value from {}\n{}'.format(
                        expected_type.__class__, loc_str)
                    return [], message
            elif (issubclass(expected_type, UserString)
                  or issubclass(expected_type, str)):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    message = 'Expected a string matching {}\n{}'.format(
                        expected_type.__class__, loc_str)
                    return [], message
            else:
                # auto-recognize based on constructor signature
                if not isinstance(node, yaml.MappingNode):
                    message = 'Expected a dict/mapping here\n{}'.format(
                        loc_str)
                    return [], message

                for attr_name, type_, required in class_subobjects(
                        expected_type):
                    cnode = Node(node)
                    # try exact match first, dashes if that doesn't match
                    for name in [attr_name, attr_name.replace('_', '-')]:
                        if cnode.has_attribute(name):
                            subnode = cnode.get_attribute(name)
                            recognized_types, message = self.recognize(
                                subnode.yaml_node, type_)
                            if len(recognized_types) == 0:
                                message = ('Failed when checking attribute'
                                           ' {}:\n{}').format(
                                               name, indent(message, '    '))
                                return [], message
                            break
                    else:
                        if required:
                            message = (
                                'Error recognizing a {}\n{}because it'
                                ' is missing an attribute named {}').format(
                                    expected_type.__name__, loc_str, attr_name)
                            if '_' in attr_name:
                                message += ' or maybe {}.\n'.format(
                                    attr_name.replace('_', '-'))
                            else:
                                message += '.\n'
                            return [], message

            return [expected_type], ''

    def __recognize_user_classes(self, node: yaml.Node,
                                 expected_type: Type) -> RecResult:
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
            return [self.__registered_classes[node.tag]], ''

        recognized_subclasses = []
        message = ''
        for other_class in self.__registered_classes.values():
            if expected_type in other_class.__bases__:
                sub_subclasses, msg = self.__recognize_user_classes(
                    node, other_class)
                recognized_subclasses.extend(sub_subclasses)
                if len(sub_subclasses) == 0:
                    message += msg

        if len(recognized_subclasses) == 0:
            recognized_subclasses, msg = self.__recognize_user_class(
                node, expected_type)
            if len(recognized_subclasses) == 0:
                message += msg

        if len(recognized_subclasses) == 0:
            message = ('Failed to recognize a {}\n{}\nbecause of the following'
                       ' error(s):\n{}').format(expected_type.__name__,
                                                node.start_mark,
                                                indent(msg, '    '))
            return [], message

        if len(recognized_subclasses) > 1:
            message = ('{}{} Could not determine which of the following types'
                       ' this is: {}').format(node.start_mark, os.linesep,
                                              recognized_subclasses)
            return recognized_subclasses, message

        return recognized_subclasses, ''

    def recognize(self, node: yaml.Node, expected_type: Type) -> RecResult:
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
        if expected_type in [
                str, int, float, bool, bool_union_fix, datetime, None,
                type(None)
        ]:
            recognized_types, message = self.__recognize_scalar(
                node, expected_type)
        elif is_generic_union(expected_type):
            recognized_types, message = self.__recognize_union(
                node, expected_type)
        elif is_generic_list(expected_type):
            recognized_types, message = self.__recognize_list(
                node, expected_type)
        elif is_generic_dict(expected_type):
            recognized_types, message = self.__recognize_dict(
                node, expected_type)
        elif expected_type in self.__registered_classes.values():
            recognized_types, message = self.__recognize_user_classes(
                node, expected_type)

        if recognized_types is None:
            raise RecognitionError(
                ('Could not recognize for type {},'
                 ' is it registered?').format(expected_type))
        logger.debug('Recognized types {} matching {}'.format(
            recognized_types, expected_type))
        return recognized_types, message
