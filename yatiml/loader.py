import enum
import logging
import os
from collections import UserString
from typing import Any, List, Type

import ruamel.yaml as yaml

from yatiml.constructors import (Constructor, EnumConstructor,
                                 UserStringConstructor)
from yatiml.exceptions import RecognitionError
from yatiml.helpers import Node
from yatiml.introspection import class_subobjects
from yatiml.recognizer import Recognizer
from yatiml.util import (generic_type_args, is_generic_list, is_generic_dict,
                         scalar_type_to_tag, type_to_desc)

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

    def __type_to_tag(self, type_: Type) -> str:
        """Convert a type to the corresponding YAML tag.

        Args:
            type_: The type to convert

        Returns:
            A string containing the YAML tag.
        """
        if type_ in scalar_type_to_tag:
            return scalar_type_to_tag[type_]

        if is_generic_list(type_):
            return 'tag:yaml.org,2002:seq'

        if is_generic_dict(type_):
            return 'tag:yaml.org,2002:map'

        if type_ in self._registered_classes.values():
            return '!{}'.format(type_.__name__)

        raise RuntimeError((
            'Unknown type {} in type_to_tag,'  # pragma: no cover
            ' please report a YAtiML bug.').format(type_))

    def __savorize(self, node: yaml.Node, expected_type: Type) -> yaml.Node:
        """Removes syntactic sugar from the node.

        This calls yatiml_savorize(), first on the class's base \
        classes, then on the class itself.

        Args:
            node: The node to modify.
            expected_type: The type to assume this type is.
        """
        logger.debug('Savorizing node assuming type {}'.format(
            expected_type.__name__))

        for base_class in expected_type.__bases__:
            if base_class in self._registered_classes.values():
                node = self.__savorize(node, base_class)

        if hasattr(expected_type, 'yatiml_savorize'):
            logger.debug('Calling {}.yatiml_savorize()'.format(
                expected_type.__name__))
            cnode = Node(node)
            expected_type.yatiml_savorize(cnode)
            node = cnode.yaml_node
        return node

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
        recognized_types, message = self.__recognizer.recognize(
            node, expected_type)

        if len(recognized_types) != 1:
            raise RecognitionError(message)

        recognized_type = recognized_types[0]

        # remove syntactic sugar
        logger.debug('Savorizing node {}'.format(node))
        if recognized_type in self._registered_classes.values():
            node = self.__savorize(node, recognized_type)
        logger.debug('Savorized, now {}'.format(node))

        # process subnodes
        logger.debug('Recursing into subnodes')
        if is_generic_list(recognized_type):
            if node.tag != 'tag:yaml.org,2002:seq':
                raise RecognitionError('{}{}Expected a {} here'.format(
                    node.start_mark, os.linesep,
                    type_to_desc(expected_type)))
            for item in node.value:
                self.__process_node(item,
                                    generic_type_args(recognized_type)[0])
        elif is_generic_dict(recognized_type):
            if node.tag != 'tag:yaml.org,2002:map':
                raise RecognitionError('{}{}Expected a {} here'.format(
                    node.start_mark, os.linesep,
                    type_to_desc(expected_type)))
            for _, value_node in node.value:
                self.__process_node(value_node,
                                    generic_type_args(recognized_type)[1])

        elif recognized_type in self._registered_classes.values():
            if (not issubclass(recognized_type, enum.Enum)
                    and not issubclass(recognized_type, str)
                    and not issubclass(recognized_type, UserString)):
                for attr_name, type_, _ in class_subobjects(recognized_type):
                    cnode = Node(node)
                    if cnode.has_attribute(attr_name):
                        subnode = cnode.get_attribute(attr_name)
                        new_subnode = self.__process_node(
                            subnode.yaml_node, type_)
                        cnode.set_attribute(attr_name, new_subnode)
        else:
            logger.debug('Not a generic class or a user-defined class, not'
                         ' recursing')

        node.tag = self.__type_to_tag(recognized_type)
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
