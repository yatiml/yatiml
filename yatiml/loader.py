from collections import UserString
import enum
import logging
import os
from typing import Any, Dict, GenericMeta, List, Type

import ruamel.yaml as yaml

from yatiml.constructors import (Constructor, EnumConstructor,
                                 UserStringConstructor)
from yatiml.exceptions import RecognitionError
from yatiml.helpers import ClassNode, ScalarNode
from yatiml.introspection import class_subobjects
from yatiml.recognizer import Recognizer
from yatiml.util import scalar_type_to_tag

logger = logging.getLogger(__name__)


class Loader(yaml.RoundTripLoader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__recognizer = Recognizer(self._registered_classes)

    def get_single_node(self) -> yaml.Node:
        """Hook used when loading a single document.

        This is the hook we use to hook yatiml into ruamel.yaml. It is \
        called by the yaml libray when the user uses load() to load a \
        YAML document.

        Returns:
            A processed node representing the document.
        """
        node = super().get_single_node()
        if node is not None:
            node = self.__process_node(node, type(self).document_type)
        return node

    def get_node(self) -> yaml.Node:
        """Hook used when reading a multi-document stream.

        This is the hook we use to hook yatiml into ruamel.yaml. It is \
        called by the yaml library when the user uses load_all() to \
        load multiple documents from a stream.

        Returns:
            A processed node representing the document.
        """
        node = super().get_node()
        if node is not None:
            node = self.__process_node(node, type(self).document_type)
        return node

    def __type_to_desc(self, type_: Type) -> str:
        """Convert a type to a human-readable description.

        This is used for generating nice error messages. We want users \
        to see a nice readable text, rather than something like \
        "typing.List<~T>[str]".

        Args:
            type_: The type to represent.

        Returns:
            A human-readable description.
        """
        scalar_type_to_str = {
            str: 'string',
            int: 'int',
            float: 'float',
            bool: 'boolean',
            None: 'null value',
            type(None): 'null value'
        }

        if type_ in scalar_type_to_str:
            return scalar_type_to_str[type_]

        if type(type_).__name__ in ['UnionMeta', '_Union']:
            if hasattr(type_, '__union_params__'):
                types = type_.__union_params__
            else:
                types = type_.__args__
            return 'union of {}'.format(
                [self.__type_to_desc(t) for t in types])

        if isinstance(type_, GenericMeta):
            if type_.__origin__ == List:
                return 'list of ({})'.format(
                    self.__type_to_desc(type_.__args__[0]))
            if type_.__origin__ == Dict:
                return 'dict of string to ({})'.format(
                    self.__type_to_desc(type_.__args__[1]))

        if type_ in self._registered_classes.values():
            return type_.__name__

        raise RuntimeError((
            'Unknown type {} in type_to_desc,'  # pragma: no cover
            ' please report a YAtiML bug.').format(type_))

    def __type_to_tag(self, type_: Type) -> str:
        """Convert a type to the corresponding YAML tag.

        Args:
            type_: The type to convert

        Returns:
            A string containing the YAML tag.
        """
        if type_ in scalar_type_to_tag:
            return scalar_type_to_tag[type_]

        if isinstance(type_, GenericMeta):
            if type_.__origin__ == List:
                return 'tag:yaml.org,2002:seq'
            elif type_.__origin__ == Dict:
                return 'tag:yaml.org,2002:map'

        if type_ in self._registered_classes.values():
            return '!{}'.format(type_.__name__)

        raise RuntimeError((
            'Unknown type {} in type_to_tag,'  # pragma: no cover
            ' please report a YAtiML bug.').format(type_))

    def __savorize(self, node: yaml.MappingNode, expected_type: Type) -> None:
        """Removes syntactic sugar from the node.

        This calls yatiml_savorize(), first on the class's base \
        classes, then on the class itself.

        Args:
            node: The node to modify.
            expected_type: The type to assume this type is.
        """
        logger.debug('Savorizing node assuming type {}'.format(
            expected_type.__name__))
        if issubclass(expected_type, enum.Enum):
            if hasattr(expected_type, 'yatiml_savorize'):
                logger.debug('Calling {}.yatiml_savorize()'.format(
                    expected_type.__name__))
                snode = ScalarNode(node)
                expected_type.yatiml_savorize(snode)  # type: ignore
        else:
            for base_class in expected_type.__bases__:
                if base_class in self._registered_classes.values():
                    self.__savorize(node, base_class)

            if hasattr(expected_type, 'yatiml_savorize'):
                logger.debug('Calling {}.yatiml_savorize()'.format(
                    expected_type.__name__))
                cnode = ClassNode(node)
                expected_type.yatiml_savorize(cnode)

    def __process_node(self, node: yaml.Node,
                       expected_type: Type) -> yaml.Node:
        """Processes a node.

        This is the main function that implements yatiml's \
        functionality. It figures out how to interpret this node \
        (recognition), then applies syntactic sugar, and finally \
        recurses to the subnodes, if any.

        Args:
            node: The node to process.
            expected_type: The type we expect this node to be.

        Returns:
            The transformed node, or a transformed copy.
        """
        logger.info('Processing node {} expecting type {}'.format(
            node, expected_type))

        # figure out how to interpret this node
        recognized_types = self.__recognizer.recognize(node, expected_type)

        if len(recognized_types) == 0:
            raise RecognitionError('{}{}Type mismatch, expected a {}'.format(
                node.start_mark, os.linesep,
                self.__type_to_desc(expected_type)))
        if len(recognized_types) > 1:
            raise RecognitionError(
                '{}{}Ambiguous value, could be any of {}'.format(
                    node.start_mark, os.linesep,
                    [self.__type_to_desc(t) for t in recognized_types]))

        recognized_type = recognized_types[0]
        node.tag = self.__type_to_tag(recognized_type)

        # remove syntactic sugar
        logger.debug('Savorizing node')
        if recognized_type in self._registered_classes.values():
            self.__savorize(node, recognized_type)

        # process subnodes
        logger.debug('Recursing into subnodes')
        if isinstance(recognized_type, GenericMeta):
            if recognized_type.__origin__ == List:
                if node.tag != 'tag:yaml.org,2002:seq':
                    raise RecognitionError('{}{}Expected a {} here'.format(
                        node.start_mark, os.linesep,
                        self.__type_to_desc(expected_type)))
                for item in node.value:
                    self.__process_node(item, recognized_type.__args__[0])
            elif recognized_type.__origin__ == Dict:
                if node.tag != 'tag:yaml.org,2002:map':
                    raise RecognitionError('{}{}Expected a {} here'.format(
                        node.start_mark, os.linesep,
                        self.__type_to_desc(expected_type)))
                for _, value_node in node.value:
                    self.__process_node(value_node,
                                        recognized_type.__args__[1])

        elif recognized_type in self._registered_classes.values():
            if (not issubclass(recognized_type, enum.Enum)
                    and not issubclass(recognized_type, str)
                    and not issubclass(recognized_type, UserString)):
                for attr_name, type_, _ in class_subobjects(expected_type):
                    cnode = ClassNode(node)
                    if cnode.has_attribute(attr_name):
                        subnode = cnode.get_attribute(attr_name)
                        self.__process_node(subnode, type_)

        logger.debug('Finished processing node {}'.format(node))
        return node


def set_document_type(loader_cls: Type, type_: Type) -> None:
    """Set the type corresponding to the whole document.

    Args:
        loader_cls: The loader class to set the document type for.
        type_: The type to loader should process the document into.
    """
    loader_cls.document_type = type_

    if not hasattr(loader_cls, '_registered_classes'):
        loader_cls._registered_classes = dict()


# Python errors if we define classes as Union[List[Type], Type]
# So List[Type] it is, and if the user ignores that and passes
# a single class, it'll work anyway, with a little mypy override.
def add_to_loader(loader_cls: Type, classes: List[Type]) -> None:
    """Registers one or more classes with a YAtiML loader.

    Once a class has been registered, it can be recognized and \
    constructed when reading a YAML text.

    Args:
        loader_cls: The loader to register the classes with.
        classes: The class(es) to register, a plain Python class or a \
                list of them.
    """
    if not isinstance(classes, list):
        classes = [classes]  # type: ignore

    for class_ in classes:
        tag = '!{}'.format(class_.__name__)
        if issubclass(class_, enum.Enum):
            loader_cls.add_constructor(tag, EnumConstructor(class_))
        elif issubclass(class_, str) or issubclass(class_, UserString):
            loader_cls.add_constructor(tag, UserStringConstructor(class_))
        else:
            loader_cls.add_constructor(tag, Constructor(class_))

        if not hasattr(loader_cls, '_registered_classes'):
            loader_cls._registered_classes = dict()
        loader_cls._registered_classes[tag] = class_
