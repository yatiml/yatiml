from collections import abc, UserString
from datetime import date
import typing
from typing import (
        Any, cast, Dict, Mapping, MutableMapping, MutableSequence, List,
        Sequence, Union)
from typing_extensions import Type

import ruamel.yaml as yaml


class bool_union_fix:
    pass


scalar_type_to_tag = {
    str: 'tag:yaml.org,2002:str',
    int: 'tag:yaml.org,2002:int',
    float: 'tag:yaml.org,2002:float',
    bool: 'tag:yaml.org,2002:bool',
    bool_union_fix: 'tag:yaml.org,2002:bool',
    None: 'tag:yaml.org,2002:null',
    type(None): 'tag:yaml.org,2002:null',
    date: 'tag:yaml.org,2002:timestamp'
    }


ScalarType = Union[str, int, float, bool, None]


class String:
    """Tag for classes that should be serialised to YAML as a string.

    If your class has this class as a base class, then YAtiML will:

    - expect a string on the YAML side when recognising,
    - call ``__init__`` with that string as the sole argument when loading,
    - use ``str(obj)`` to obtain the string representation on dumping.

    You can still override what's written to the YAML file by defining
    ``_yatiml_sweeten()`` in the usual way.

    Like classes derived from ``str`` and ``UserString``, classes tagged like
    this can be used as keys for dictionaries. Be sure to implement
    ``__hash__()`` and ``__eq__()`` to make that work on the Python side.
    """
    pass


def is_generic_sequence(type_: Type) -> bool:
    """Determines whether a type is a sequence tag.

    How to do this varies for different Python versions, due to the
    typing library not having a stable API. This functions smooths
    over the differences, returning True if the type is a List[],
    Sequence[] or MutableSequence[].

    Args:
        type_: The type to check.

    Returns:
        True iff it's a generic sequence.
    """
    if hasattr(typing, '_GenericAlias'):
        # 3.7
        # _GenericAlias cannot be imported from typing, because it doesn't
        # exist in all versions, and it will fail the type check in those
        # versions as well, so we ignore it.
        return (isinstance(type_, typing._GenericAlias) and     # type: ignore
                (
                    type_.__origin__ is list or
                    type_.__origin__ is abc.Sequence or
                    type_.__origin__ is abc.MutableSequence))
    else:
        # 3.6 and earlier
        # GenericMeta cannot be imported from typing, because it doesn't
        # exist in all versions, and it will fail the type check in those
        # versions as well, so we ignore it.
        return (isinstance(type_, typing.GenericMeta) and
                (
                    cast(Any, type_).__origin__ is List or
                    cast(Any, type_).__origin__ is Sequence or
                    cast(Any, type_).__origin__ is MutableSequence))


def is_generic_mapping(type_: Type) -> bool:
    """Determines whether a type is a mapping tag.

    How to do this varies for different Python versions, due to the
    typing library not having a stable API. This functions smoothes
    over the differences, returning True if the type is a Dict[],
    Mapping[] or MutableMapping[].

    Args:
        type_: The type to check.

    Returns:
        True iff it's a generic mapping.
    """
    if hasattr(typing, '_GenericAlias'):
        # 3.7
        return (isinstance(type_, typing._GenericAlias) and     # type: ignore
                (
                    type_.__origin__ is dict or
                    type_.__origin__ is abc.Mapping or
                    type_.__origin__ is abc.MutableMapping))
    else:
        # 3.6 and earlier
        return (isinstance(type_, typing.GenericMeta) and
                (
                    cast(Any, type_).__origin__ is Dict or
                    cast(Any, type_).__origin__ is Mapping or
                    cast(Any, type_).__origin__ is MutableMapping))


def is_generic_union(type_: Type) -> bool:
    """Determines whether a type is a Union[...].

    How to do this varies for different Python versions, due to the
    typing library not having a stable API. This functions smooths
    over the differences.

    Args:
        type_: The type to check.

    Returns:
        True iff it's a Union[...something...].
    """
    if hasattr(typing, '_GenericAlias'):
        # 3.7
        return (isinstance(type_, typing._GenericAlias) and     # type: ignore
                type_.__origin__ is Union)
    else:
        if hasattr(typing, '_Union'):
            # 3.6
            return isinstance(type_, typing._Union)             # type: ignore
        else:
            # 3.5 and earlier (?)
            return isinstance(type_, typing.UnionMeta)          # type: ignore
    raise RuntimeError('Could not determine whether type is a Union. Is this'
                       ' a YAtiML-supported Python version?')


def generic_type_args(type_: Type) -> List[Type]:
    """Gets the type argument list for the given generic type.

    If you give this function List[int], it will return [int], and
    if you give it Union[int, str] it will give you [int, str]. Note
    that on Python < 3.7, Union[int, bool] collapses to Union[int] and
    then to int; this is already done by the time this function is
    called, so it does not help with that.

    Args:
        type_: The type to get the arguments list of.

    Returns:
        A list of Type objects.
    """
    if hasattr(type_, '__union_params__'):
        # 3.5 Union
        return list(type_.__union_params__)
    if hasattr(type_, '__args__'):
        # >3.5
        return list(type_.__args__)
    # 3.5
    return list(type_.__parameters__)


def type_to_desc(type_: Type) -> str:
    """Convert a type to a human-readable description.

    This is used for generating nice error messages. We want users
    to see a nice readable text, rather than something like
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

    if is_generic_union(type_):
        return 'union of {}'.format([type_to_desc(t)
                                     for t in generic_type_args(type_)])

    if is_generic_sequence(type_):
        return 'list of ({})'.format(type_to_desc(generic_type_args(type_)[0]))

    if is_generic_mapping(type_):
        return 'dict of string to ({})'.format(
                type_to_desc(generic_type_args(type_)[1]))

    if type_ is Any:
        return 'string, int, float, boolean, null value, list or dict'

    return type_.__name__


def is_string_like(type_: Type) -> bool:
    """Returns whether the type is string-like.

    That means it takes a string as its only constructor argument, and
    is allowed to be a key in dicts. See UserStringConstructor.

    Args:
        type_: The type to check.
    """
    return issubclass(type_, (str, UserString, String))


def strip_tags(resolver: yaml.VersionedResolver, node: yaml.Node) -> None:
    """Strips tags from mappings in the tree headed by node.

    This keeps yaml from constructing any objects in this tree.

    Args:
        resolver: Resolver to tag scalar nodes with
        node: Head of the tree to strip
    """
    if isinstance(node, yaml.ScalarNode):
        if not node.tag.startswith('tag:yaml.org,2002:'):
            node.tag = resolver.resolve(
                    yaml.ScalarNode, node.value, (True, False))
    elif isinstance(node, yaml.SequenceNode):
        node.tag = 'tag:yaml.org,2002:seq'
        for subnode in node.value:
            strip_tags(resolver, subnode)
    elif isinstance(node, yaml.MappingNode):
        node.tag = 'tag:yaml.org,2002:map'
        for key_node, value_node in node.value:
            strip_tags(resolver, key_node)
            strip_tags(resolver, value_node)
