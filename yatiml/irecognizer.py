import abc
from typing import List, Tuple, Type

from ruamel import yaml

RecResult = Tuple[List[Type], str]
"""A recognition result.

The first list is a list of recognised types, the second list an error
message to display if no type was recognised or more than one type was
recognised.
"""


class IRecognizer(abc.ABC):
    """An interface for Recognizer.

    I don't like interfaces that have only one implementation, but \
    needed one here to break an import cycle.
    """

    def recognize(self, node: yaml.Node, expected_type: Type) -> RecResult:
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
        raise NotImplementedError()  # pragma: no cover
