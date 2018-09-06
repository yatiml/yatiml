import copy
import os
from typing import Dict, GenericMeta, List, Type, Union, UnionMeta

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
                None: 'null value'
                }

        if type_ in scalar_type_to_str:
            return scalar_type_to_str[type_]

        if isinstance(type_, UnionMeta):
            return 'union of {}'.format(
                    [self.__type_to_desc(t) for t in type_.__union_params__])

        if isinstance(type_, GenericMeta):
            if type_.__origin__ == List:
                return 'list of ({})'.format(self.__type_to_desc(type_.__args__[0]))
            if type_.__origin__ == Dict:
                return 'dict of string to ({})'.format(self.__type_to_desc(type_.__args__[1]))
        raise RuntimeError('Unknown type in type_to_tag, please report a YAtiML bug.')

    def __type_to_tag(self, type_: Type) -> str:
        """Convert a type to the corresponding YAML tag.

        Args:
            type_: The type to convert

        Returns:
            A string containing the YAML tag.
        """
        scalar_type_to_tag = {
                str: 'tag:yaml.org,2002:str',
                int: 'tag:yaml.org,2002:int',
                float: 'tag:yaml.org,2002:float',
                bool: 'tag:yaml.org,2002:bool',
                None: 'tag:yaml.org,2002:null'
                }

        if type_ in scalar_type_to_tag:
            return scalar_type_to_tag[type_]
        if isinstance(type_, GenericMeta):
                if type_.__origin__ == List:
                    return 'tag:yaml.org,2002:seq'
                elif type_.__origin__ == Dict:
                    return 'tag:yaml.org,2002:map'
        raise RuntimeError('Unknown type in type_to_tag, please report a YAtiML bug.')

    def __recognize_scalar(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a node that we expect to be a scalar.

        Args:
            node: The node to recognize.
            expected_type: The type it is expected to be.

        Returns:
            A list of recognized types
        """
        if (isinstance(node, yaml.ScalarNode) and
                node.tag == self.__type_to_tag(expected_type)):
            return [expected_type]
        return []

    def __recognize_list(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a node that we expect to be a list of some kind.

        Args:
            node: The node to recognize.
            expected_type: List[...something...]

        Returns
            expected_type if it was recognized, [] otherwise.
        """
        if not isinstance(node, yaml.SequenceNode):
            return []
        item_type = expected_type.__args__[0]
        for item in node.value:
            recognized_types = self.__recognize(item, item_type)
            if len(recognized_types) == 0:
                return []
            if len(recognized_types) > 1:
                return [List[t] for t in recognized_types]      # type: ignore

        return [expected_type]

    def __recognize_dict(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a node that we expect to be a dict of some kind.

        Args:
            node: The node to recognize.
            expected_type: Dict[str, ...something...]

        Returns:
            expected_type if it was recognized, [] otherwise.
        """
        if not issubclass(expected_type.__args__[0], str):
            raise RuntimeError('YAtiML only supports dicts with strings as keys')
        if not isinstance(node, yaml.MappingNode):
            return []
        value_type = expected_type.__args__[1]
        for key, value in node.value:
            recognized_value_types = self.__recognize(value, value_type)
            if len(recognized_value_types) == 0:
                return []
            if len(recognized_value_types) > 1:
                return [Dict[str, t] for t in recognized_value_types]      # type: ignore

        return [expected_type]

    def __recognize_union(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a node that we expect to be one of a union of types.

        Args:
            node: The node to recognize.
            expected_type: Union[...something...]

        Returns:
            The specific type that was recognized, multiple, or none.
        """
        recognized_types = []
        for possible_type in expected_type.__union_set_params__:
            recognized_types.extend(self.__recognize(node, possible_type))
        recognized_types = list(set(recognized_types))
        return recognized_types

    def __recognize(self, node: yaml.Node, expected_type: Type) -> List[Type]:
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
        if expected_type in [str, int, float, bool, None]:
            recognized_types = self.__recognize_scalar(node, expected_type)
        if isinstance(expected_type, UnionMeta):
            recognized_types = self.__recognize_union(node, expected_type)
        if isinstance(expected_type, GenericMeta):
                if expected_type.__origin__ == List:
                    recognized_types = self.__recognize_list(node, expected_type)
                elif expected_type.__origin__ == Dict:
                    recognized_types = self.__recognize_dict(node, expected_type)

        print('    Recognized {}, expected {}, got {}'.format(node, expected_type, recognized_types))
        return recognized_types

    def __process_node(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> yaml.Node:
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
                node.start_mark, os.linesep, self.__type_to_desc(expected_type)))
        if len(recognized_types) > 1:
            raise RecognitionError(
                    '{}{}Ambiguous value, could be any of {}'.format(
                        node.start_mark, os.linesep,
                        [self.__type_to_desc(t) for t in recognized_types]))

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
