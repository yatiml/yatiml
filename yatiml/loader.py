import copy
import os
from typing import List, Type

import ruamel.yaml as yaml

from yatiml.exceptions import RecognitionError


class Loader(yaml.Loader):
    def get_single_node(self) -> yaml.Node:
        """Hook used when loading a single document.

        This is the hook we use to hook yatiml into ruamel.yaml. It is \
        called by the yaml libray when the user uses load() to load a \
        YAML document.

        Returns:
            A processed node representing the document.
        """
        node = super().get_single_node()
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
        node = self.__process_node(node, type(self).document_type)
        return node

    def __type_to_tag(self, type_: Type) -> str:
        """Convert a type to the corresponding YAML tag.

        Args:
            type_: The type to convert

        Returns:
            A string containing the YAML tag.
        """
        if type_ == str:
            return 'tag:yaml.org,2002:str'
        return ''

    def __recognize_str(self, node: yaml.Node) -> List[Type]:
        """Recognize a node that we expect to be a str.

        Args:
            node: The node to recognize

        Returns:
            A list of recognized types
        """
        if isinstance(node, yaml.ScalarNode) and node.tag == 'tag:yaml.org,2002:str':
            return [str]
        return []

    def __recognize(self, node: yaml.Node, expected_type: Type) -> List[Type]:
        """Figure out how to interpret this node.

        This is not quite a type check. This function makes a list of \
        all types that match the expected type and also the node, and \
        returns that list. The goal here is not to test validity, but \
        to determine how to process this node further.

        Args:
            node: The YAML node to recognize.
            expected_type: The type we expect this node to be, based \
                    on the context provided by our type definitions.

        Returns:
            A list of matching types.
        """
        if expected_type == str:
            recognized_types = self.__recognize_str(node)

        return recognized_types

    def __process_node(self, node: yaml.Node, expected_type: Type) -> yaml.Node:
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
        # figure out how to interpret this node
        recognized_types = self.__recognize(node, expected_type)

        if len(recognized_types) == 0:
            raise RecognitionError('{}{}Type mismatch, expected a {}'.format(
                node.start_mark, os.linesep, expected_type.__name__))
        if len(recognized_types) > 1:
            raise RecognitionError('{}{}Ambiguous value, could be any of {}'.format(
                node.start_mark, os.linesep, [c.__name__ for c in recognized_types]))

        recognized_type = recognized_types[0]
        node.tag = self.__type_to_tag(recognized_type)

        return node

    @classmethod
    def set_document_type(cls, type_: Type) -> None:
        """Set the type corresponding to the whole document.

        Args:
            type_: The type to try to process the document into.
        """
        cls.document_type = type_


def make_loader(document_type: Type) -> Type:
    """Make a Loader class for use with yaml.load().

    This function returns a class that loads YAML documents as the \
    given type. Pass it to the Loader argument of yaml.load() or \
    yaml.load_all().

    Args:
        document_type: The type to match with the document.

    Returns:
        A yaml Loader class.
    """
    NewLoader = copy.deepcopy(Loader)
    NewLoader.set_document_type(document_type)
    return NewLoader
