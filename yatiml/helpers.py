from ruamel import yaml

import os
from typing import Type, Union

from yatiml.exceptions import RecognitionError

class ClassNode:
    """A wrapper class for yaml Nodes that provides utility functions.

    This class defines a number of helper function for you to use \
    when writing yatiml_recognize() functions.
    """
    def __init__(self, node: yaml.MappingNode) -> None:
        """Create a ClassNode for a particular mapping node.

        The member functions will act on the contained node.

        Args:
            node: The node to provide help for.
        """
        self.yaml_node = node

    def require_attribute_value(
            self,
            attribute: str,
            value: Union[int, str, float, bool, None]
            ) -> None:
        """Require an attribute on the node to have a particular value.

        This requires the attribute to exist, and to have the given value
        and corresponding type.

        Args:
            attribute: The name of the attribute / mapping key.
            value: The value the attribute must have to recognize an \
                    object of this type.
        """
        found = False
        for key_node, value_node in self.yaml_node.value:
            if (key_node.tag == 'tag:yaml.org,2002:str' and
                    key_node.value == attribute):
                found = True
                if value_node.value != value:
                    raise RecognitionError(('{}{}Incorrect attribute value'
                        ' {} where {} was required').format(
                            self.yaml_node.start_mark, os.linesep, value_node.value,
                            value))

        if not found:
            raise RecognitionError(('{}{}Required attribute {} not found'
                ).format(self.yaml_node.start_mark, os.linesep, attribute))

    def has_attribute(self, attribute: str) -> bool:
        """Whether the node has an attribute with the given name.

        Args:
            attribute: The name of the attribute to check for.

        Returns:
            True iff the attribute is present.
        """
        return any([key_node
                for key_node, _ in self.yaml_node.value
                if key_node.value == attribute])

    def has_attribute_type(self, attribute: str, type_: Type) -> bool:
        """Whether the given attribute exists and has a compatible type.

        Returns true iff the attribute exists and is an instance of \
        the given type.

        Args:
            attribute: The name of the attribute to check.
            type_: The type to check against.

        Returns:
            True iff the attribute exists and matches the type.
        """
        if not self.has_attribute(attribute):
            return False
        return isinstance(self.get_attribute(attribute), type_)


    def get_attribute(self, attribute: str) -> yaml.Node:
        """Returns the node representing the given attribute's value.

        Args:
            attribute: The name of the attribute to retrieve.

        Raises:
            KeyError: If the attribute does not exist.

        Returns:
            A node representing the value.
        """
        matches = [value_node
                for key_node, value_node in self.yaml_node.value
                if key_node.value == attribute]
        if len(matches) != 1:
            raise KeyError('Attribute not found, or found multiple times: {}'.format(
                matches))
        return matches[0]
