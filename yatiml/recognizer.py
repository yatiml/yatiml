import enum
from inspect import isclass
import logging
import os
import pathlib
from datetime import date
from textwrap import indent
from typing import Any, Dict, List
from typing_extensions import Type

import ruamel.yaml as yaml

from yatiml.exceptions import RecognitionError
from yatiml.helpers import Node, UnknownNode
from yatiml.introspection import class_subobjects
from yatiml.irecognizer import IRecognizer, RecResult
from yatiml.util import (
        bool_union_fix, generic_type_args, is_generic_mapping,
        is_generic_sequence, is_generic_union, is_string_like,
        scalar_type_to_tag, type_to_desc)


logger = logging.getLogger(__name__)


class Recognizer(IRecognizer):
    """Functions for recognizing objects as types."""

    def __init__(
            self, registered_classes: Dict[str, Type],
            additional_classes: Dict[Type, str]) -> None:
        """Create a Recognizer.

        Args:
            registered_classes: The registered tags and corresponding
                    classes.
        """
        self.__registered_classes = registered_classes
        self.__additional_classes = additional_classes

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
            return {expected_type}, ''
        message = 'Failed to recognize a {}\n{}\n'.format(
            type_to_desc(expected_type), node.start_mark)
        return set(), message

    def __recognize_additional(
            self, node: yaml.Node, expected_type: Type) -> RecResult:
        """Recognize a node that we expect to be an additional type.

        Args:
            node: The node to recognize.
            expected_type: The type it is expected to be.

        Returns:
            A list of recognized types and an error message
        """
        logger.debug('Recognizing as an additional type')

        if expected_type == pathlib.Path:
            if (isinstance(node, yaml.ScalarNode)
                    and node.tag == 'tag:yaml.org,2002:str'):
                return {expected_type}, ''

        message = 'Failed to recognize a {}\n{}\n'.format(
            type_to_desc(expected_type), node.start_mark)
        return set(), message

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
            return set(), message
        item_type = generic_type_args(expected_type)[0]
        for item in node.value:
            recognized_types, message = self.recognize(item, item_type)
            if len(recognized_types) == 0:
                return set(), message
            if len(recognized_types) > 1:
                recognized_types = {
                    List[t]  # type: ignore
                    for t in recognized_types
                }
                return recognized_types, message

        return {expected_type}, ''

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
        key_type = generic_type_args(expected_type)[0]
        if (
                not isclass(key_type)
                or not is_string_like(key_type)):
            raise RuntimeError(
                'YAtiML only supports dicts with strings as keys')
        if not isinstance(node, yaml.MappingNode):
            message = '{}{}Expected a dict/mapping here'.format(
                node.start_mark, os.linesep)
            return set(), message

        value_type = generic_type_args(expected_type)[1]
        for key, value in node.value:
            recognized_key_types, kmessage = self.recognize(key, key_type)
            if len(recognized_key_types) == 0:
                return set(), kmessage
            if len(recognized_key_types) > 1:
                return {
                    Dict[t, value_type]  # type: ignore
                    for t in recognized_key_types
                }, kmessage  # type: ignore

            recognized_value_types, vmessage = self.recognize(
                    value, value_type)
            if len(recognized_value_types) == 0:
                return set(), vmessage
            if len(recognized_value_types) > 1:
                return {
                    Dict[key_type, t]  # type: ignore
                    for t in recognized_value_types
                }, vmessage  # type: ignore

        return {expected_type}, ''

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
        recognized_types = set()
        message = ''
        union_types = generic_type_args(expected_type)
        logger.debug('Union types {}'.format(union_types))
        for possible_type in union_types:
            recognized_type, msg = self.recognize(node, possible_type)
            if len(recognized_type) == 0:
                message += msg
            recognized_types |= recognized_type
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

        This tries to recognize only exactly the specified class. It
        recurses down into the class's attributes, but not to its
        subclasses. See also __recognize_user_classes().

        Args:
            node: The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing the user-defined class, or an empty list.
        """
        logger.debug('Recognizing as a user-defined class')
        loc_str = '{}{}'.format(node.start_mark, os.linesep)
        if '_yatiml_recognize' in expected_type.__dict__:
            try:
                unode = UnknownNode(self, node)
                expected_type._yatiml_recognize(unode)
                return {expected_type}, ''
            except RecognitionError as e:
                if len(e.args) > 0:
                    message = ('Error recognizing a {}\n{}because of the'
                               ' following error(s): {}').format(
                                   expected_type.__name__, loc_str,
                                   indent(e.args[0], '    '))
                else:
                    message = 'Error recognizing a {}\n{}'.format(
                        expected_type.__name__, loc_str)
                return set(), message
        else:
            if issubclass(expected_type, enum.Enum):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    message = 'Expected an enum value from {}\n{}'.format(
                        expected_type.__name__, loc_str)
                    return set(), message
            elif is_string_like(expected_type):
                if (not isinstance(node, yaml.ScalarNode)
                        or node.tag != 'tag:yaml.org,2002:str'):
                    message = 'Expected a string matching {}\n{}'.format(
                        expected_type.__name__, loc_str)
                    return set(), message
            else:
                # auto-recognize based on constructor signature
                if not isinstance(node, yaml.MappingNode):
                    req_attrs = [
                            a for a, t, r in class_subobjects(expected_type)
                            if r]
                    message = (
                            'Expected a dict/mapping here with keys {}\n{}'
                            ).format(req_attrs, loc_str)
                    return set(), message

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
                                           ' "{}":\n{}').format(
                                               name, indent(message, '    '))
                                return set(), message
                            break
                    else:
                        if required:
                            message = (
                                'Error recognizing a {}\n{}because it'
                                ' is missing an attribute named "{}"').format(
                                    expected_type.__name__, loc_str, attr_name)
                            if '_' in attr_name:
                                message += ' or maybe "{}".\n'.format(
                                    attr_name.replace('_', '-'))
                            else:
                                message += '.\n'
                            return set(), message

            return {expected_type}, ''

    def __recognize_user_classes(self, node: yaml.Node,
                                 expected_type: Type) -> RecResult:
        """Recognize a user-defined class in the node.

        This returns a list of classes from the inheritance hierarchy
        headed by expected_type which match the given node and which
        do not have a registered derived class that matches the given
        node. So, the returned classes are the most derived matching
        classes that inherit from expected_type.

        This function recurses down the user's inheritance hierarchy.

        Args:
            node: The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing matched user-defined classes.
        """
        logger.debug('Recognizing user class {}'.format(
            expected_type.__name__))
        recognized_subclasses = set()
        message = ''
        for other_class in self.__registered_classes.values():
            if expected_type in other_class.__bases__:
                sub_subclasses, msg = self.__recognize_user_classes(
                    node, other_class)
                recognized_subclasses |= sub_subclasses
                if len(sub_subclasses) == 0:
                    message += msg

        logger.debug('Recognized subclasses of {}: {}'.format(
                expected_type.__name__, recognized_subclasses))

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
            logger.debug(message)
            return set(), message

        if len(recognized_subclasses) > 1:
            # Let the user disambiguate with an explicit tag
            if node.tag in self.__registered_classes:
                typ = self.__registered_classes[node.tag]
                if typ in recognized_subclasses:
                    return {typ}, ''

            message = ('{}{} Could not determine which of the following types'
                       ' this is: {}').format(node.start_mark, os.linesep,
                                              recognized_subclasses)
            logger.debug(message)
            return recognized_subclasses, message

        # Tags that don't match with what we recognized are an error,
        # because silently ignoring the conflict would get confusing.
        if not node.tag.startswith('tag:yaml.org,2002'):
            if node.tag in self.__registered_classes:
                tagged_class = self.__registered_classes[node.tag]
                if tagged_class not in recognized_subclasses:
                    message = ('{}{} Expected a {} and found it, but there\'s'
                               ' a tag here claiming this is a(n) {}. That'
                               ' makes no sense.').format(
                                       node.start_mark, os.linesep,
                                       expected_type.__name__,
                                       tagged_class.__name__)
                    logger.debug(message)
                    return set(), message
            else:
                message = ('{}{} Expected a {} and found it, but there\'s'
                           ' a tag here claiming this is a(n) {}, which type'
                           ' I don\'t know.').format(
                                   node.start_mark, os.linesep,
                                   expected_type.__name__, node.tag[1:])
                logger.debug(message)
                return set(), message

        return recognized_subclasses, ''

    def recognize(self, node: yaml.Node, expected_type: Type) -> RecResult:
        """Figure out how to interpret this node.

        This is not quite a type check. This function makes a list of
        all types that match the expected type and also the node, and
        returns that list. The goal here is not to test validity, but
        to determine how to process this node further.

        That said, it will recognize built-in types only in case of
        an exact match.

        Args:
            node: The YAML node to recognize.
            expected_type: The type we expect this node to be, based
                    on the context provided by our type definitions.

        Returns:
            A list of matching types.
        """
        logger.debug('Recognizing {} as a {}'.format(node, expected_type))
        recognized_types = None     # type: Any
        if expected_type in (
                str, int, float, bool, bool_union_fix, date, None,
                type(None)):
            recognized_types, message = self.__recognize_scalar(
                    node, expected_type)
        elif expected_type in self.__additional_classes:
            recognized_types, message = self.__recognize_additional(
                    node, expected_type)
        elif is_generic_union(expected_type):
            recognized_types, message = self.__recognize_union(
                     node, expected_type)
        elif is_generic_sequence(expected_type):
            recognized_types, message = self.__recognize_list(
                    node, expected_type)
        elif is_generic_mapping(expected_type):
            recognized_types, message = self.__recognize_dict(
                    node, expected_type)
        elif expected_type in self.__registered_classes.values():
            recognized_types, message = self.__recognize_user_classes(
                    node, expected_type)
        elif expected_type in (Any,):
            recognized_types, message = [Any], ''

        if recognized_types is None:
            raise RecognitionError(
                ('Could not recognize for type {},'
                 ' is it registered?').format(expected_type.__name__))
        logger.debug('Recognized types {} matching {}'.format(
            recognized_types, expected_type))
        return recognized_types, message
