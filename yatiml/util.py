from datetime import datetime
from typing import Dict, GenericMeta, List, Type, Union

scalar_type_to_tag = {
    str: 'tag:yaml.org,2002:str',
    int: 'tag:yaml.org,2002:int',
    float: 'tag:yaml.org,2002:float',
    bool: 'tag:yaml.org,2002:bool',
    None: 'tag:yaml.org,2002:null',
    type(None): 'tag:yaml.org,2002:null',
    datetime: 'tag:yaml.org,2002:timestamp'
}

ScalarType = Union[str, int, float, bool, None]


def type_to_desc(type_: Type) -> str:
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
        return 'union of {}'.format([type_to_desc(t) for t in types])

    if isinstance(type_, GenericMeta):
        if type_.__origin__ == List:
            return 'list of ({})'.format(type_to_desc(type_.__args__[0]))
        if type_.__origin__ == Dict:
            return 'dict of string to ({})'.format(
                type_to_desc(type_.__args__[1]))

    return type_.__name__
