import inspect
from typing import Any, Generator, Tuple, Type


def class_subobjects(
        class_: Type) -> Generator[Tuple[str, Type, bool], None, None]:
    """Find the aggregated subobjects of an object.

    These are the public attributes.

    Args:
        class_: The class whose subobjects to return.

    Yields:
        Tuples (name, type, required) describing subobjects.
    """
    argspec = inspect.getfullargspec(class_.__init__)
    defaults = argspec.defaults if argspec.defaults else []
    num_optional = len(defaults)
    first_optional = len(argspec.args) - num_optional

    for i, attr_name in enumerate(argspec.args):
        if attr_name == 'self':
            continue
        if attr_name == 'yatiml_extra':
            continue
        attr_type = argspec.annotations.get(attr_name, Any)
        yield attr_name, attr_type, i < first_optional
