import inspect
import logging
import os
from collections import OrderedDict
from typing import TYPE_CHECKING, Any, Generator, List, Type, Union

import ruamel.yaml as yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from yatiml.exceptions import RecognitionError
from yatiml.introspection import class_subobjects
from yatiml.util import (bool_union_fix, generic_type_args, is_generic_list,
                         is_generic_dict, is_generic_union)

if TYPE_CHECKING:
    from yatiml.loader import Loader  # noqa: F401

logger = logging.getLogger(__name__)


class Constructor:
    """A constructor for user classes to register with YAML."""

    def __init__(self, class_: Type) -> None:
        """Create a constructor

        Args:
            class_: The class that this is a constructor for.
        """
        self.class_ = class_

    def __call__(self, loader: 'Loader',
                 node: yaml.Node) -> Generator[Any, None, None]:
        """Construct an object from a yaml node.

        This constructs an object of the user-defined type that this \
        is the constructor for. It is registered with the yaml library, \
        and called by it. Recursion is handled by calling the yaml \
        library, so we only need to construct an object using the keys \
        and values of the given MappingNode, and those values have been \
        converted recursively for us.

        Since Python does not do type checks, we do a type check \
        manually, to ensure that the class's constructor gets the types \
        it expects. This avoids confusing errors, but moreover is a \
        security features that ensures that regardless of the content \
        of the YAML file, we produce the objects that the programmer \
        defined and expects.

        Note that this yields rather than returns, in a somewhat odd \
        way. That's directly from the PyYAML/ruamel.yaml documentation.

        Args:
            loader: The yatiml.loader that is creating this object.
            node: The node to construct from.

        Yields:
            The incomplete constructed object.
        """
        logger.debug('Constructing an object of type {}'.format(
            self.class_.__name__))
        if not isinstance(node, yaml.MappingNode):
            raise RecognitionError(
                ('{}{}Expected a MappingNode. There'
                 ' is probably something wrong with your yatiml_savorize()'
                 ' function.').format(node.start_mark, os.linesep))

        # figure out which keys are extra and strip them of tags
        # to prevent constructing objects we haven't type checked
        argspec = inspect.getfullargspec(self.class_.__init__)
        self.__strip_extra_attributes(node, argspec.args)

        # create object and let yaml lib construct subobjects
        new_obj = self.class_.__new__(self.class_)  # type: ignore
        yield new_obj
        mapping = CommentedMap()
        loader.construct_mapping(node, mapping, deep=True)

        # Convert ruamel.yaml's round-trip types to list and OrderedDict,
        # recursively for each attribute value in our mapping. Note that
        # mapping itself is still a CommentedMap.
        for key, value in mapping.copy().items():
            if (isinstance(value, CommentedMap)
                    or isinstance(value, CommentedSeq)):
                mapping[key] = self.__to_plain_containers(value)

        # do type check
        self.__check_no_missing_attributes(node, mapping)
        self.__type_check_attributes(node, mapping, argspec)

        # construct object, this should work now
        try:
            logger.debug('Calling __init__')
            if 'yatiml_extra' in argspec.args:
                attrs = self.__split_off_extra_attributes(
                    mapping, argspec.args)
                new_obj.__init__(**attrs)

            else:
                new_obj.__init__(**mapping)

        except TypeError:  # pragma: no cover
            raise RecognitionError(
                ('{}{}Could not construct object of class {}'
                 ' from {}. This is a bug in YAtiML, please report.'.format(
                     node.start_mark, os.linesep, self.class_.__name__, node)))
        logger.debug('Done constructing {}'.format(self.class_.__name__))

    def __to_plain_containers(self,
                              container: Union[CommentedSeq, CommentedMap]
                              ) -> Union[OrderedDict, list]:
        """Converts any sequence or mapping to list or OrderedDict

        Stops at anything that isn't a sequence or a mapping.

        One day, we'll extract the comments and formatting and store \
        them out-of-band.

        Args:
            mapping: The mapping of constructed subobjects to edit
        """
        if isinstance(container, CommentedMap):
            new_container = OrderedDict()  # type: Union[OrderedDict, list]
            for key, value_obj in container.items():
                if (isinstance(value_obj, CommentedMap)
                        or isinstance(value_obj, CommentedSeq)):
                    new_container[key] = self.__to_plain_containers(value_obj)
                else:
                    new_container[key] = value_obj

        elif isinstance(container, CommentedSeq):
            new_container = list()
            for value_obj in container:
                if (isinstance(value_obj, CommentedMap)
                        or isinstance(value_obj, CommentedSeq)):
                    new_container.append(self.__to_plain_containers(value_obj))
                else:
                    new_container.append(value_obj)
        return new_container

    def __split_off_extra_attributes(self, mapping: CommentedMap,
                                     known_attrs: List[str]) -> CommentedMap:
        """Separates the extra attributes in mapping into yatiml_extra.

        This returns a mapping containing all key-value pairs from \
        mapping whose key is in known_attrs, and an additional key \
        yatiml_extra which maps to a dict containing the remaining \
        key-value pairs.

        Args:
            mapping: The mapping to split
            known_attrs: Attributes that should be kept in the main \
                    map, and not moved to yatiml_extra.

        Returns:
            A map with attributes reorganised as described above.
        """
        attr_names = list(mapping.keys())
        main_attrs = mapping.copy()
        extra_attrs = OrderedDict(mapping.items())
        for name in attr_names:
            if name not in known_attrs or name == 'yatiml_extra':
                del (main_attrs[name])
            else:
                del (extra_attrs[name])
        main_attrs['yatiml_extra'] = extra_attrs
        return main_attrs

    def __type_matches(self, obj: Any, type_: Type) -> bool:
        """Checks that the object matches the given type.

        Like isinstance(), but will work with union types using Union, \
        Dict and List.

        Args:
            obj: The object to check
            type_: The type to check against

        Returns:
            True iff obj is of type type_
        """
        if is_generic_union(type_):
            for t in generic_type_args(type_):
                if self.__type_matches(obj, t):
                    return True
            return False
        elif is_generic_list(type_):
            if not isinstance(obj, list):
                return False
            for item in obj:
                if not self.__type_matches(item, generic_type_args(type_)[0]):
                    return False
            return True
        elif is_generic_dict(type_):
            if not isinstance(obj, OrderedDict):
                return False
            for key, value in obj.items():
                if not isinstance(key, generic_type_args(type_)[0]):
                    return False
                if not self.__type_matches(value, generic_type_args(type_)[1]):
                    return False
            return True
        elif type_ is bool_union_fix:
            return isinstance(obj, bool)
        else:
            return isinstance(obj, type_)

    def __check_no_missing_attributes(self, node: yaml.Node,
                                      mapping: CommentedMap) -> None:
        """Checks that all required attributes are present.

        Also checks that they're of the correct type.

        Args:
            mapping: The mapping with subobjects of this object.

        Raises:
            RecognitionError: if an attribute is missing or the type \
                is incorrect.
        """
        logger.debug('Checking presence of required attributes')
        for name, type_, required in class_subobjects(self.class_):
            if required and name not in mapping:
                raise RecognitionError(('{}{}Missing attribute {} needed for'
                                        ' constructing a {}').format(
                                            node.start_mark, os.linesep, name,
                                            self.class_.__name__))
            if name in mapping and not self.__type_matches(
                    mapping[name], type_):
                raise RecognitionError(('{}{}Attribute {} has incorrect type'
                                        ' {}, expecting a {}').format(
                                            node.start_mark, os.linesep, name,
                                            type(mapping[name]), type_))

    def __type_check_attributes(self, node: yaml.Node, mapping: CommentedMap,
                                argspec: inspect.FullArgSpec) -> None:
        """Ensure all attributes have a matching constructor argument.

        This checks that there is a constructor argument with a \
        matching type for each existing attribute.

        If the class has a yatiml_extra attribute, then extra \
        attributes are okay and no error will be raised if they exist.

        Args:
            node: The node we're processing
            mapping: The mapping with constructed subobjects
            constructor_attrs: The attributes of the constructor, \
                    including self and yatiml_extra, if applicable
        """
        logger.debug('Checking for extraneous attributes')
        logger.debug('Constructor arguments: {}, mapping: {}'.format(
            argspec.args, list(mapping.keys())))
        for key, value in mapping.items():
            if not isinstance(key, str):
                raise RecognitionError(('{}{}YAtiML only supports strings'
                                        ' for mapping keys').format(
                                            node.start_mark, os.linesep))
            if key not in argspec.args and 'yatiml_extra' not in argspec.args:
                raise RecognitionError(
                    ('{}{}Found additional attributes'
                     ' and {} does not support those').format(
                         node.start_mark, os.linesep, self.class_.__name__))

            if key in argspec.args and not self.__type_matches(
                    value, argspec.annotations[key]):
                raise RecognitionError(('{}{}Expected attribute {} to be of'
                                        ' type {} but it is a(n) {}').format(
                                            node.start_mark, os.linesep, key,
                                            argspec.annotations[key],
                                            type(value)))

    def __strip_extra_attributes(self, node: yaml.Node,
                                 known_attrs: List[str]) -> None:
        """Strips tags from extra attributes.

        This prevents nodes under attributes that are not part of our \
        data model from being converted to objects. They'll be plain \
        CommentedMaps instead, which then get converted to OrderedDicts \
        for the user.

        Args:
            node: The node to process
            known_attrs: The attributes to not strip
        """
        known_keys = list(known_attrs)
        if 'self' not in known_keys:
            raise RuntimeError('The __init__ method of {} does not have a'
                               ' "self" attribute! Please add one, this is'
                               ' not a valid constructor.'.format(
                                   self.class_.__name__))
        known_keys.remove('self')
        if 'yatiml_extra' in known_keys:
            known_keys.remove('yatiml_extra')

        for key_node, value_node in node.value:
            if (not isinstance(key_node, yaml.ScalarNode)
                    or key_node.tag != 'tag:yaml.org,2002:str'):
                raise RecognitionError(
                    ('{}{}Mapping keys that are not of type'
                     ' string are not supported by YAtiML.').format(
                         node.start_mark, os.linesep))
            if key_node.value not in known_keys:
                self.__strip_tags(value_node)

    def __strip_tags(self, node: yaml.Node) -> None:
        """Strips tags from mappings in the tree headed by node.

        This keeps yaml from constructing any objects in this tree.

        Args:
            node: Head of the tree to strip
        """
        if isinstance(node, yaml.SequenceNode):
            for subnode in node.value:
                self.__strip_tags(subnode)
        elif isinstance(node, yaml.MappingNode):
            node.tag = 'tag:yaml.org,2002:map'
            for key_node, value_node in node.value:
                self.__strip_tags(key_node)
                self.__strip_tags(value_node)


class EnumConstructor:
    """A constructor for user enum classes to register with YAML.

    This constructor should be used in place of Constructor for enums, \
    i.e. classes derived from enum.Enum.
    """

    def __init__(self, class_: Type) -> None:
        """Create a constructor

        Args:
            class_: The class that this is a constructor for.
        """
        self.class_ = class_

    def __call__(self, loader: 'Loader',
                 node: yaml.Node) -> Generator[Any, None, None]:
        """Construct an enum value from a yaml node.

        This constructs an object of the user-defined enum that this \
        is the constructor for. It is registered with the yaml library, \
        and called by it.

        Note that this yields rather than returns, in a somewhat odd \
        way. That's directly from the PyYAML/ruamel.yaml documentation.

        Args:
            loader: The yatiml.loader that is creating this object.
            node: The node to construct from.

        Yields:
            The incomplete constructed object.
        """
        logger.debug('Constructing an object of type {}'.format(
            self.class_.__name__))

        if not isinstance(node, yaml.ScalarNode) or not isinstance(
                node.value, str):
            raise RecognitionError(
                ('{}{}Expected a string matching a {}.').format(
                    node.start_mark, os.linesep, self.class_.__name__))

        # ruamel.yaml expects us to yield an incomplete object, but enums are
        # immutable, so we'll have to make the whole thing right away.
        try:
            new_obj = self.class_[node.value]
        except KeyError:
            raise RecognitionError(
                ('Expected a string matching a {}\n{}').format(
                    self.class_.__name__, node.start_mark))
        yield new_obj


class UserStringConstructor:
    """A constructor for user-defined string classes to register with YAML.

    This constructor should be used in place of Constructor for \
    user-defined strings, i.e. classes derived from str or \
    collections.UserString.
    """

    def __init__(self, class_: Type) -> None:
        """Create a constructor

        Args:
            class_: The class that this is a constructor for.
        """
        self.class_ = class_

    def __call__(self, loader: 'Loader',
                 node: yaml.Node) -> Generator[Any, None, None]:
        """Construct an user string value from a yaml node.

        This constructs an object of the user-defined string class that \
        this is the constructor for. It is registered with the yaml \
        library, and called by it.

        Note that this yields rather than returns, in a somewhat odd \
        way. That's directly from the PyYAML/ruamel.yaml documentation.

        Args:
            loader: The yatiml.loader that is creating this object.
            node: The node to construct from.

        Yields:
            The incomplete constructed object.
        """
        logger.debug('Constructing an object of type {}'.format(
            self.class_.__name__))

        if not isinstance(node, yaml.ScalarNode) or not isinstance(
                node.value, str):
            raise RecognitionError(
                ('{}{}Expected a string matching a {}.').format(
                    node.start_mark, os.linesep, self.class_.__name__))

        # ruamel.yaml expects us to yield an incomplete object, but strings are
        # immutable, so we'll have to make the whole thing right away.
        new_obj = self.class_(node.value)
        yield new_obj
