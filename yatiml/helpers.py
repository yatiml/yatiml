import os
from typing import (  # noqa: F401
    List,
    Optional,
    Set,
    Type,
    TypeVar,
    Union,
    cast)

from ruamel import yaml
from ruamel.yaml.error import StreamMark

from yatiml.exceptions import RecognitionError, SeasoningError
from yatiml.irecognizer import IRecognizer
from yatiml.util import ScalarType, scalar_type_to_tag

_Any = TypeVar('_Any')


class Node:
    """A wrapper class for yaml Nodes that provides utility functions.

    This class defines a number of helper function for you to use \
    when writing yatiml_sweeten() and yatiml_savorize() functions. It \
    also gives access to the underlying `yaml.Node`, so you can do \
    anything ruamel.yaml can do if you're willing to dive into its \
    internals.

    Attributes:
        yaml_node: The wrapped yaml Node. You can read and modify this,\
                yourself if you want, or replace it completely with a \
                new yaml.Node.
    """

    def __init__(self, node: yaml.Node) -> None:
        """Create a Node for a particular node.

        The member functions will act on the contained node.

        Args:
            node: The node to provide help for.
        """
        self.yaml_node = node

    def __str__(self) -> str:
        """Convert to a human-readable string."""
        return 'Node({})'.format(self.yaml_node)

    def is_scalar(self, typ: Type = _Any) -> bool:
        """Returns True iff this represents a scalar node.

        If a type is given, checks that the ScalarNode represents this \
        type. Type may be `str`, `int`, `float`, `bool`, or `None`.

        If no type is given, any ScalarNode will return True.
        """
        if isinstance(self.yaml_node, yaml.ScalarNode):
            if typ != _Any and typ in scalar_type_to_tag:
                if typ is None:
                    typ = type(None)
                return self.yaml_node.tag == scalar_type_to_tag[typ]

            if typ is _Any:
                return True
            raise ValueError('Invalid scalar type passed to is_scalar()')
        return False

    def is_mapping(self) -> bool:
        """Returns True iff this represents a mapping node."""
        return isinstance(self.yaml_node, yaml.MappingNode)

    def is_sequence(self) -> bool:
        """Returns True iff this represents a sequence node."""
        return isinstance(self.yaml_node, yaml.SequenceNode)

    # Functions for Scalar nodes
    def get_value(self) -> ScalarType:
        """Returns the value of a Scalar node.

        Use is_scalar(type) to check which type the node has.
        """
        if self.yaml_node.tag == 'tag:yaml.org,2002:str':
            return self.yaml_node.value
        if self.yaml_node.tag == 'tag:yaml.org,2002:int':
            return int(self.yaml_node.value)
        if self.yaml_node.tag == 'tag:yaml.org,2002:float':
            return float(self.yaml_node.value)
        if self.yaml_node.tag == 'tag:yaml.org,2002:bool':
            return self.yaml_node.value in ['TRUE', 'True', 'true']
        if self.yaml_node.tag == 'tag:yaml.org,2002:null':
            return None
        raise RuntimeError('This node with tag {} is not of the right type'
                           ' for get_value()'.format(self.yaml_node.tag))

    def set_value(self, value: ScalarType) -> None:
        """Sets the value of the node to a scalar value.

        After this, is_scalar(type(value)) will return true.

        Args:
            value: The value to set this node to, a str, int, float, \
                    bool, or None.
        """
        if isinstance(value, bool):
            value_str = 'true' if value else 'false'
        else:
            value_str = str(value)
        start_mark = self.yaml_node.start_mark
        end_mark = self.yaml_node.end_mark
        # If we're of a class type, then we want to keep that tag so that the
        # correct Constructor is called. If we're a built-in type, set the tag
        # to the appropriate YAML tag.
        tag = self.yaml_node.tag
        if tag.startswith('tag:yaml.org,2002:'):
            tag = scalar_type_to_tag[type(value)]
        new_node = yaml.ScalarNode(tag, value_str, start_mark, end_mark)
        self.yaml_node = new_node

    # Functions for Mapping nodes

    def make_mapping(self) -> None:
        """Replaces the node with a new, empty mapping.

        Note that this will work on the Node object that is passed to \
        a yatiml_savorize() or yatiml_sweeten() function, but not on \
        any of its attributes or items. If you need to set an attribute \
        to a complex value, build a yaml.Node representing it and use \
        set_attribute with that.
        """
        start_mark = StreamMark('generated node', 0, 0, 0)
        end_mark = StreamMark('generated node', 0, 0, 0)
        self.yaml_node = yaml.MappingNode('tag:yaml.org,2002:map', list(),
                                          start_mark, end_mark)

    def has_attribute(self, attribute: str) -> bool:
        """Whether the node has an attribute with the given name.

        Use only if is_mapping() returns True.

        Args:
            attribute: The name of the attribute to check for.

        Returns:
            True iff the attribute is present.
        """
        return any([
            key_node.value == attribute for key_node, _ in self.yaml_node.value
        ])

    def has_attribute_type(self, attribute: str, typ: Type) -> bool:
        """Whether the given attribute exists and has a compatible type.

        Returns true iff the attribute exists and is an instance of \
        the given type. Matching between types passed as typ and \
        yaml node types is as follows:

        +---------+-------------------------------------------+
        |   typ   |                 yaml                      |
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
            typ: The type to check against.

        Returns:
            True iff the attribute exists and matches the type.
        """
        if not self.has_attribute(attribute):
            return False

        attr_node = self.get_attribute(attribute).yaml_node

        if typ in scalar_type_to_tag:
            tag = scalar_type_to_tag[typ]
            return attr_node.tag == tag
        elif typ == list:
            return isinstance(attr_node, yaml.SequenceNode)
        elif typ == dict:
            return isinstance(attr_node, yaml.MappingNode)

        raise ValueError('Invalid argument for typ attribute')

    def get_attribute(self, attribute: str) -> 'Node':
        """Returns the node representing the given attribute's value.

        Use only if is_mapping() returns true.

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
        return Node(matches[0])

    def set_attribute(self, attribute: str,
                      value: Union[ScalarType, yaml.Node]) -> None:
        """Sets the attribute to the given value.

        Use only if is_mapping() returns True.

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
            key_node = yaml.ScalarNode('tag:yaml.org,2002:str', attribute,
                                       start_mark, end_mark)
            self.yaml_node.value.append((key_node, value_node))

    def remove_attribute(self, attribute: str) -> None:
        """Remove an attribute from the node.

        Use only if is_mapping() returns True.

        Args:
            attribute: The name of the attribute to remove.
        """
        attr_index = self.__attr_index(attribute)
        if attr_index is not None:
            self.yaml_node.value.pop(attr_index)

    def rename_attribute(self, attribute: str, new_name: str) -> None:
        """Renames an attribute.

        Use only if is_mapping() returns true.

        If the attribute does not exist, this will do nothing.

        Args:
            attribute: The (old) name of the attribute to rename.
            new_name: The new name to rename it to.
        """
        for key_node, _ in self.yaml_node.value:
            if key_node.value == attribute:
                key_node.value = new_name
                break

    def unders_to_dashes_in_keys(self) -> None:
        """Replaces underscores with dashes in key names.

        For each attribute in a mapping, this replaces any underscores \
        in its keys with dashes. Handy because Python does not \
        accept dashes in identifiers, while some YAML-based formats use \
        dashes in their keys.
        """
        for key_node, _ in self.yaml_node.value:
            key_node.value = key_node.value.replace('_', '-')

    def dashes_to_unders_in_keys(self) -> None:
        """Replaces dashes with underscores in key names.

        For each attribute in a mapping, this replaces any dashes in \
        its keys with underscores. Handy because Python does not \
        accept dashes in identifiers, while some YAML-based file \
        formats use dashes in their keys.
        """
        for key_node, _ in self.yaml_node.value:
            key_node.value = key_node.value.replace('-', '_')

    def seq_attribute_to_map(self,
                             attribute: str,
                             key_attribute: str,
                             value_attribute: Optional[str] = None,
                             strict: Optional[bool] = True) -> None:
        """Converts a sequence attribute to a map.

        This function takes an attribute of this Node that is \
        a sequence of mappings and turns it into a mapping of mappings. \
        It assumes that each of the mappings in the original sequence \
        has an attribute containing a unique value, which it will use \
        as a key for the new outer mapping.

        An example probably helps. If you have a Node representing \
        this piece of YAML::

            items:
            - item_id: item1
              description: Basic widget
              price: 100.0
            - item_id: item2
              description: Premium quality widget
              price: 200.0

        and call seq_attribute_to_map('items', 'item_id'), then the \
        Node will be modified to represent this::

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
            value_attribute: Name of the attribute in each item to use \
                    for the value in the new mapping, if only a key and \
                    value have been given.
            strict: Whether to give an error if the intended keys are \
                    not unique.

        Raises:
            SeasoningError: If the keys are not unique and strict is \
                    True.
        """
        if not self.has_attribute(attribute):
            return

        attr_node = self.get_attribute(attribute)
        if not attr_node.is_sequence():
            return

        start_mark = attr_node.yaml_node.start_mark
        end_mark = attr_node.yaml_node.end_mark

        # check that all list items are mappings and that the keys are unique
        # strings
        seen_keys = set()  # type: Set[str]
        for item in attr_node.seq_items():
            key_attr_node = item.get_attribute(key_attribute)
            if not key_attr_node.is_scalar(str):
                raise SeasoningError(
                    ('Attribute names must be strings in'
                     'YAtiML, {} is not a string.').format(key_attr_node))
            if key_attr_node.get_value() in seen_keys:
                if strict:
                    raise SeasoningError(
                        ('Found a duplicate key {}: {} when'
                         ' converting from sequence to mapping'.format(
                             key_attribute, key_attr_node.get_value())))
                return
            seen_keys.add(key_attr_node.get_value())  # type: ignore

        # construct mapping
        mapping_values = list()
        for item in attr_node.seq_items():
            # we've already checked that it's a SequenceNode above
            key_node = item.get_attribute(key_attribute).yaml_node
            item.remove_attribute(key_attribute)
            if value_attribute is not None:
                value_node = item.get_attribute(value_attribute).yaml_node
                if len(item.yaml_node.value) == 1:
                    # no other attributes, use short form
                    mapping_values.append((key_node, value_node))
                else:
                    mapping_values.append((key_node, item.yaml_node))
            else:
                mapping_values.append((key_node, item.yaml_node))

        # create mapping node
        mapping = yaml.MappingNode('tag:yaml.org,2002:map', mapping_values,
                                   start_mark, end_mark)
        self.set_attribute(attribute, mapping)

    def map_attribute_to_seq(self,
                             attribute: str,
                             key_attribute: str,
                             value_attribute: Optional[str] = None) -> None:
        """Converts a mapping attribute to a sequence.

        This function takes an attribute of this Node whose value \
        is a mapping or a mapping of mappings and turns it into a \
        sequence of mappings. Each entry in the original mapping is \
        converted to an entry in the list. If only a key attribute is \
        given, then each entry in the original mapping must map to a \
        (sub)mapping. This submapping becomes the corresponding list \
        entry, with the key added to it as an additional attribute. If a \
        value attribute is also given, then an entry in the original \
        mapping may map to any object. If the mapped-to object is a \
        mapping, the conversion is as before, otherwise a new \
        submapping is created, and key and value are added using the \
        given key and value attribute names.

        An example probably helps. If you have a Node representing \
        this piece of YAML::

            items:
              item1:
                description: Basic widget
                price: 100.0
              item2:
                description: Premium quality widget
                price: 200.0

        and call map_attribute_to_seq('items', 'item_id'), then the \
        Node will be modified to represent this::

            items:
            - item_id: item1
              description: Basic widget
              price: 100.0
            - item_id: item2
              description: Premium quality widget
              price: 200.0

        which once converted to an object is often easier to deal with \
        in code.

        Slightly more complicated, this YAML::

            items:
              item1: Basic widget
              item2:
                description: Premium quality widget
                price: 200.0

        when passed through map_attribute_to_seq('items', 'item_id', \
        'description'), will result in th equivalent of::

            items:
            - item_id: item1
              description: Basic widget
            - item_id: item2
              description: Premium quality widget
              price: 200.0

        If the attribute does not exist, or is not a mapping, this \
        function will silently do nothing.

        With thanks to the makers of the Common Workflow Language for \
        the idea.

        Args:
            attribute: Name of the attribute whose value to modify.
            key_attribute: Name of the new attribute in each item to \
                    add with the value of the key.
            value_attribute: Name of the new attribute in each item to \
                    add with the value of the key.
        """
        if not self.has_attribute(attribute):
            return

        attr_node = self.get_attribute(attribute)
        if not attr_node.is_mapping():
            return

        start_mark = attr_node.yaml_node.start_mark
        end_mark = attr_node.yaml_node.end_mark
        object_list = []
        for item_key, item_value in attr_node.yaml_node.value:
            item_value_node = Node(item_value)
            if not item_value_node.is_mapping():
                if value_attribute is None:
                    return
                ynode = item_value_node.yaml_node
                item_value_node.make_mapping()
                item_value_node.set_attribute(value_attribute, ynode)

            item_value_node.set_attribute(key_attribute, item_key.value)
            object_list.append(item_value_node.yaml_node)
        seq_node = yaml.SequenceNode('tag:yaml.org,2002:seq', object_list,
                                     start_mark, end_mark)
        self.set_attribute(attribute, seq_node)

    # Functions for sequences

    def seq_items(self) -> List['Node']:
        """Returns the items in the sequence.

        Use only if is_sequence() returns True.
        """
        return list(map(Node, self.yaml_node.value))

    # Private helpers

    def __attr_index(self, attribute: str) -> Optional[int]:
        """Finds an attribute's index in the yaml_node.value list."""
        attr_index = None
        for i, (key_node, _) in enumerate(self.yaml_node.value):
            if key_node.value == attribute:
                attr_index = i
                break
        return attr_index


class UnknownNode:
    """Utility functions for recognizing nodes.

    This class defines a number of helper function for you to use \
    when writing yatiml_recognize() functions.

    Attributes:
        yaml_node: The yaml.Node wrapped by this object.
    """

    def __init__(self, recognizer: IRecognizer, node: yaml.Node) -> None:
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

    def require_scalar(self, *args: Type) -> None:
        """Require the node to be a scalar.

        If additional arguments are passed, these are taken as a list \
        of valid types; if the node matches one of these, then it is \
        accepted.

        Example:
            # Match either an int or a string
            node.require_scalar(int, str)

        Arguments:
            args: One or more types to match one of.
        """
        node = Node(self.yaml_node)
        if len(args) == 0:
            if not node.is_scalar():
                raise RecognitionError(('{}{}A scalar is required').format(
                    self.yaml_node.start_mark, os.linesep))
        else:
            for typ in args:
                if node.is_scalar(typ):
                    return
            raise RecognitionError(
                ('{}{}A scalar of type {} is required').format(
                    self.yaml_node.start_mark, os.linesep, args))

    def require_mapping(self) -> None:
        """Require the node to be a mapping."""
        if not isinstance(self.yaml_node, yaml.MappingNode):
            raise RecognitionError(('{}{}A mapping is required here').format(
                self.yaml_node.start_mark, os.linesep))

    def require_sequence(self) -> None:
        """Require the node to be a sequence."""
        if not isinstance(self.yaml_node, yaml.SequenceNode):
            raise RecognitionError(('{}{}A sequence is required here').format(
                self.yaml_node.start_mark, os.linesep))

    def require_attribute(self, attribute: str, typ: Type = _Any) -> None:
        """Require an attribute on the node to exist.

        This implies that the node must be a mapping.

        If `typ` is given, the attribute must have this type.

        Args:
            attribute: The name of the attribute / mapping key.
            typ: The type the attribute must have.
        """
        self.require_mapping()
        attr_nodes = [
            value_node for key_node, value_node in self.yaml_node.value
            if key_node.value == attribute
        ]
        if len(attr_nodes) == 0:
            raise RecognitionError(
                ('{}{}Missing required attribute {}').format(
                    self.yaml_node.start_mark, os.linesep, attribute))
        attr_node = attr_nodes[0]

        if typ != _Any:
            recognized_types, message = self.__recognizer.recognize(
                attr_node, cast(Type, typ))
            if len(recognized_types) == 0:
                raise RecognitionError(message)

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
                node = Node(value_node)
                if not node.is_scalar(type(value)):
                    raise RecognitionError(
                            ('{}{}Incorrect attribute type where value {}'
                             ' of type {} was required').format(
                                self.yaml_node.start_mark, os.linesep,
                                value, type(value)))
                if node.get_value() != value:
                    raise RecognitionError(
                        ('{}{}Incorrect attribute value'
                         ' {} where {} was required').format(
                             self.yaml_node.start_mark, os.linesep,
                             value_node.value, value))

        if not found:
            raise RecognitionError(
                ('{}{}Required attribute {} not found').format(
                    self.yaml_node.start_mark, os.linesep, attribute))
