import os
from typing import Optional, Set, Type, Union  # noqa: F401

from ruamel import yaml
from ruamel.yaml.error import StreamMark

from yatiml.exceptions import RecognitionError, SeasoningError
from yatiml.irecognizer import IRecognizer
from yatiml.util import scalar_type_to_tag


class UnknownNode:
    """Utility functions for recognizing nodes.

    This class defines a number of helper function for you to use \
    when writing yatiml_recognize() functions.
    """

    def __init__(self, recognizer: IRecognizer,
                 node: yaml.MappingNode) -> None:
        """Create an UnknownNode for a particular mapping node.

        The member functions will act on the contained node.

        Args:
            node: The node to operate on.
        """
        self.__recognizer = recognizer
        self.yaml_node = node

    def __str__(self) -> str:
        """Convert to a human-readable string."""
        return 'UnknownNode({})'.format(self.yaml_node)

    def require_attribute(self, attribute: str, type_: Type = None) -> None:
        """Require an attribute on the node to exist.

        Args:
            attribute: The name of the attribute / mapping key.
        """
        attr_nodes = [
            value_node for key_node, value_node in self.yaml_node.value
            if key_node.value == attribute
        ]
        if len(attr_nodes) == 0:
            raise RecognitionError(
                ('{}{}Missing required attribute {}').format(
                    self.yaml_node.start_mark, os.linesep, attribute))
        attr_node = attr_nodes[0]

        if type_ is not None:
            recognized_types = self.__recognizer.recognize(attr_node, type_)
            if len(recognized_types) == 0:
                raise RecognitionError(('{}{}Attribute {} is not of required'
                                        ' type {}').format(
                                            self.yaml_node.start_mark,
                                            os.linesep, attribute, type_))

    def require_attribute_value(
            self, attribute: str,
            value: Union[int, str, float, bool, None]) -> None:
        """Require an attribute on the node to have a particular value.

        This requires the attribute to exist, and to have the given value \
        and corresponding type. Handy for in your yatiml_recognize() \
        function.

        Args:
            attribute: The name of the attribute / mapping key.
            value: The value the attribute must have to recognize an \
                    object of this type.

        Raises:
            RecognitionError: If the attribute does not exist, or does \
                    not have the required value.
        """
        found = False
        for key_node, value_node in self.yaml_node.value:
            if (key_node.tag == 'tag:yaml.org,2002:str'
                    and key_node.value == attribute):
                found = True
                if value_node.value != value:
                    raise RecognitionError(
                        ('{}{}Incorrect attribute value'
                         ' {} where {} was required').format(
                             self.yaml_node.start_mark, os.linesep,
                             value_node.value, value))

        if not found:
            raise RecognitionError(
                ('{}{}Required attribute {} not found').format(
                    self.yaml_node.start_mark, os.linesep, attribute))


class ClassNode:
    """A wrapper class for yaml MappingNodes that provides utility functions.

    This class defines a number of helper function for you to use \
    when writing yatiml_sweeten() and yatiml_savorize() functions.
    """

    def __init__(self, node: yaml.MappingNode) -> None:
        """Create a ClassNode for a particular mapping node.

        The member functions will act on the contained node.

        Args:
            node: The node to provide help for.
        """
        self.yaml_node = node

    def __str__(self) -> str:
        """Convert to a human-readable string."""
        return 'ClassNode({})'.format(self.yaml_node)

    def has_attribute(self, attribute: str) -> bool:
        """Whether the node has an attribute with the given name.

        Args:
            attribute: The name of the attribute to check for.

        Returns:
            True iff the attribute is present.
        """
        return any([
            key_node.value == attribute for key_node, _ in self.yaml_node.value
        ])

    def has_attribute_type(self, attribute: str, type_: Type) -> bool:
        """Whether the given attribute exists and has a compatible type.

        Returns true iff the attribute exists and is an instance of \
        the given type. Matching between types passed as type_ and \
        yaml node types is as follows:

        +---------+-------------------------------------------+
        |   type  |                 yaml                      |
        +=========+===========================================+
        |   str   |      ScalarNode containing string         |
        +---------+-------------------------------------------+
        |   int   |      ScalarNode containing int            |
        +---------+-------------------------------------------+
        |  float  |      ScalarNode containing float          |
        +---------+-------------------------------------------+
        |   bool  |      ScalarNode containing bool           |
        +---------+-------------------------------------------+
        |   None  |      ScalarNode containing null           |
        +---------+-------------------------------------------+
        |   list  |      SequenceNode                         |
        +---------+-------------------------------------------+
        |   dict  |      MappingNode                          |
        +---------+-------------------------------------------+

        Args:
            attribute: The name of the attribute to check.
            type_: The type to check against.

        Returns:
            True iff the attribute exists and matches the type.
        """
        if not self.has_attribute(attribute):
            return False

        attr_node = self.get_attribute(attribute)

        if type_ in scalar_type_to_tag:
            tag = scalar_type_to_tag[type_]
            return attr_node.tag == tag
        elif type_ == list:
            return isinstance(attr_node, yaml.SequenceNode)
        elif type_ == dict:
            return isinstance(attr_node, yaml.MappingNode)

        raise ValueError('Invalid argument for type_ attribute')

    def get_attribute(self, attribute: str) -> yaml.Node:
        """Returns the node representing the given attribute's value.

        Args:
            attribute: The name of the attribute to retrieve.

        Raises:
            KeyError: If the attribute does not exist.

        Returns:
            A node representing the value.
        """
        matches = [
            value_node for key_node, value_node in self.yaml_node.value
            if key_node.value == attribute
        ]
        if len(matches) != 1:
            raise SeasoningError(
                'Attribute not found, or found multiple times: {}'.format(
                    matches))
        return matches[0]

    def set_attribute(
            self, attribute: str,
            value: Union[str, int, float, bool, None, yaml.Node]) -> None:
        """Sets the attribute to the given value.

        If the attribute does not exist, this adds a new attribute, \
        if it does, it will be overwritten.

        If value is a str, int, float, bool or None, the attribute will \
        be set to this value. If you want to set the value to a list or \
        dict containing other values, build a yaml.Node and pass it here.

        Args:
            attribute: Name of the attribute whose value to change.
            value: The value to set.
        """
        start_mark = StreamMark('generated node', 0, 0, 0)
        end_mark = StreamMark('generated node', 0, 0, 0)
        if isinstance(value, str):
            value_node = yaml.ScalarNode('tag:yaml.org,2002:str', value,
                                         start_mark, end_mark)
        elif isinstance(value, bool):
            value_str = 'true' if value else 'false'
            value_node = yaml.ScalarNode('tag:yaml.org,2002:bool', value_str,
                                         start_mark, end_mark)
        elif isinstance(value, int):
            value_node = yaml.ScalarNode('tag:yaml.org,2002:int', str(value),
                                         start_mark, end_mark)
        elif isinstance(value, float):
            value_node = yaml.ScalarNode('tag:yaml.org,2002:float', str(value),
                                         start_mark, end_mark)
        elif value is None:
            value_node = yaml.ScalarNode('tag:yaml.org,2002:null', '',
                                         start_mark, end_mark)
        elif isinstance(value, yaml.Node):
            value_node = value
        else:
            raise TypeError('Invalid kind of value passed to set_attribute()')

        attr_index = self.__attr_index(attribute)
        if attr_index is not None:
            key_node = self.yaml_node.value[attr_index][0]
            self.yaml_node.value[attr_index] = key_node, value_node
        else:
            key_node = yaml.ScalarNode('tag:yaml.org,2002:str', attribute)
            self.yaml_node.value.append((key_node, value_node))

    def remove_attribute(self, attribute: str) -> None:
        """Remove an attribute from the node.

        Useful in yatiml_sweeten() and yatiml_savorize().

        Args:
            attribute: The name of the attribute to remove.
        """
        attr_index = self.__attr_index(attribute)
        if attr_index is not None:
            self.yaml_node.value.pop(attr_index)

    def rename_attribute(self, attribute: str, new_name: str) -> None:
        """Renames an attribute.

        If the attribute does not exist, this will do nothing.

        Args:
            attribute: The (old) name of the attribute to rename.
            new_name: The new name to rename it to.
        """
        for key_node, value_node in self.yaml_node.value:
            if key_node.value == attribute:
                key_node.value = new_name
                break

    def seq_attribute_to_map(self,
                             attribute: str,
                             key_attribute: str,
                             strict: bool = True) -> None:
        """Converts a sequence attribute to a map.

        This function takes an attribute of this ClassNode that is \
        a sequence of mappings and turns it into a mapping of mappings. \
        It assumes that each of the mappings in the original sequence \
        has an attribute containing a unique value, which it will use \
        as a key for the new outer mapping.

        An example probably helps. If you have a ClassNode representing \
        this piece of YAML::

            items:
            - item_id: item1
              description: Basic widget
              price: 100.0
            - item_id: item2
              description: Premium quality widget
              price: 200.0

        and call seq_attribute_to_map('items', 'item_id'), then the \
        ClassNode will be modified to represent this::

            items:
              item1:
                description: Basic widget
                price: 100.0
              item2:
                description: Premium quality widget
                price: 200.0

        which is often more intuitive for people to read and write.

        If the attribute does not exist, or is not a sequence of \
        mappings, this function will silently do nothing. If the keys \
        are not unique and strict is False, it will also do nothing. If \
        the keys are not unique and strict is True, it will raise an \
        error.

        With thanks to the makers of the Common Workflow Language for \
        the idea.

        Args:
            attribute: Name of the attribute whose value to modify.
            key_attribute: Name of the attribute in each item to use \
                    as a key for the new mapping.
            strict: Whether to give an error if the intended keys are \
                    not unique.

        Raises:
            SeasoningError: If the keys are not unique and strict is \
                    True.
        """
        if not self.has_attribute(attribute):
            return

        attr_node = self.get_attribute(attribute)
        if not isinstance(attr_node, yaml.SequenceNode):
            return

        # check that all list items are mappings and that the keys are unique
        # strings
        seen_keys = set()  # type: Set[str]
        for item in attr_node.value:
            if not isinstance(item, yaml.MappingNode):
                if strict:
                    raise SeasoningError(('Expected a sequence of mappings'
                                          ' but got {}'.format(attr_node)))
                return

            item_cnode = ClassNode(item)
            key_attr_node = item_cnode.get_attribute(key_attribute)
            if key_attr_node.tag != 'tag:yaml.org,2002:str':
                raise SeasoningError(
                    ('Attribute names must be strings in'
                     'YAtiML, {} is not a string.').format(key_attr_node))
            if key_attr_node.value in seen_keys:
                if strict:
                    raise SeasoningError(
                        ('Found a duplicate key {}: {} when'
                         ' converting from sequence to mapping'.format(
                             key_attribute, key_attr_node.value)))
                return
            seen_keys.add(key_attr_node.value)

        # construct mapping
        mapping_values = list()
        for item in attr_node.value:
            # we've already checked that it's a MappingNode above
            item_cnode = ClassNode(item)
            key_node = item_cnode.get_attribute(key_attribute)
            item_cnode.remove_attribute(key_attribute)
            mapping_values.append((key_node, item))

        # create mapping node
        mapping = yaml.MappingNode('tag:yaml.org,2002:map', mapping_values)
        self.set_attribute(attribute, mapping)

    def map_attribute_to_seq(self, attribute: str, key_attribute: str) -> None:
        """Converts a mapping attribute to a sequence.

        This function takes an attribute of this ClassNode whose value \
        is a mapping of mappings and turns it into a sequence of \
        mappings. It adds to each of the sub-mappings in the original \
        mapping an attribute containing the value of the corresponding \
        key in the outer mapping, then replace the outer mapping with a \
        sequence containing all the inner mappings.

        An example probably helps. If you have a ClassNode representing \
        this piece of YAML::

            items:
              item1:
                description: Basic widget
                price: 100.0
              item2:
                description: Premium quality widget
                price: 200.0

        and call map_attribute_to_seq('items', 'item_id'), then the \
        ClassNode will be modified to represent this::

            items:
            - item_id: item1
              description: Basic widget
              price: 100.0
            - item_id: item2
              description: Premium quality widget
              price: 200.0

        which once converted to an object is often easier to deal with \
        in code.

        If the attribute does not exist, or is not a mapping of \
        mappings, this function will silently do nothing.

        With thanks to the makers of the Common Workflow Language for \
        the idea.

        Args:
            attribute: Name of the attribute whose value to modify.
            key_attribute: Name of the new attribute in each item to \
                    add with the value of the key.
        """
        if not self.has_attribute(attribute):
            return

        attr_node = self.get_attribute(attribute)
        if not isinstance(attr_node, yaml.MappingNode):
            return

        object_list = []
        for item_key, item_value in attr_node.value:
            item_value_cnode = ClassNode(item_value)
            item_value_cnode.set_attribute(key_attribute, item_key.value)
            object_list.append(item_value_cnode.yaml_node)
        seq_node = yaml.SequenceNode('tag:yaml.org,2002:seq', object_list)
        self.set_attribute(attribute, seq_node)

    def __attr_index(self, attribute: str) -> Optional[int]:
        """Finds an attribute's index in the yaml_node.value list."""
        attr_index = None
        for i, (key_node, _) in enumerate(self.yaml_node.value):
            if key_node.value == attribute:
                attr_index = i
                break
        return attr_index


class ScalarNode:
    """A wrapper class for yaml scalar nodes.

    Provides utility functions for use in savorize/sweeten methods.
    """

    def __init__(self, node: yaml.ScalarNode) -> None:
        """Create a ClassNode for a particular mapping node.

        The member functions will act on the contained node.

        Args:
            node: The node to provide help for.
        """
        self.yaml_node = node

    def to_upper(self) -> None:
        """Convert the string to all upper case."""
        self.yaml_node.value = self.yaml_node.value.upper()

    def to_lower(self) -> None:
        """Convert the string to all lower case."""
        self.yaml_node.value = self.yaml_node.value.lower()

    def to_title(self) -> None:
        """Convert the string to title case.

        This will make every word start with a capital, and all the \
        other letters lowercase.
        """
        self.yaml_node.value = self.yaml_node.value.title()
