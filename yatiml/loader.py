import copy
import inspect
import os
from typing import Any, Dict, Generator, GenericMeta, List, Tuple, Type, Union

import ruamel.yaml as yaml

from yatiml.exceptions import RecognitionError
from yatiml.helpers import ClassNode
from yatiml.introspection import class_subobjects
from yatiml.recognizer import Recognizer
from yatiml.util import scalar_type_to_tag


class Constructor:
    """A constructor for user classes to register with YAML."""
    def __init__(self, class_: Type) -> None:
        """Create a constructor

        Args:
            class_: The class that this is a constructor for.
        """
        self.class_ = class_

    def __call__(self, loader: 'Loader', node: yaml.Node) -> Generator[Any, None, None]:
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
        if not isinstance(node, yaml.MappingNode):
            raise RecognitionError(('{}{}Expected a MappingNode. There'
                    ' is probably something wrong with your yatiml_savorize()'
                    ' function.').format(node.start_mark, os.linesep))

        # construct object and let yaml lib construct subobjects
        new_obj = self.class_.__new__(self.class_)  # type: ignore
        yield new_obj
        mapping = loader.construct_mapping(node, deep=True)

        # check that we have an attribute for each required constructor argument
        for name, type_, required in class_subobjects(self.class_):
            if required and not name in mapping:
                raise RecognitionError(('{}{}Missing attribute {} needed for'
                    ' constructing a {}').format(node.start_mark, os.linesep,
                        name, self.class_.__name__))
            if name in mapping and not isinstance(mapping[name], type_):
                raise RecognitionError(('{}{}Attribute {} has incorrect type'
                    ' {}, expecting a {}').format(node.start_mark, os.linesep,
                        name, type(mapping[name]), type_))

        # check that we have a constructor argument for each attribute
        argspec = inspect.getfullargspec(self.class_.__init__)
        print('{} {}'.format(argspec, mapping))
        if argspec.varkw is None:
            for key, value in mapping.items():
                # ensure that we have a parameter of a matching type
                if not isinstance(key, str):
                    raise RecognitionError(('{}{}YAtiML only supports strings'
                        ' for mapping keys').format(node.start_mark,
                            os.linesep))
                if key not in argspec.args or not isinstance(value, argspec.annotations[key]):
                    raise RecognitionError(('{}{}Found additional attributes'
                        ' and {} does not support keyword args').format(node.start_mark,
                            os.linesep, self.class_.__name__))

        # construct object, this should work now
        try:
            new_obj.__init__(**mapping)
        except TypeError as e:  # pragma: no cover
            raise RecognitionError(('{}{}Could not construct object of class {}'
                ' from {}. This is a bug in YAtiML, please report.'.format(
                    node.start_mark, os.linesep, self.class_.__name__, node)))


class Loader(yaml.SafeLoader):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.__recognizer = Recognizer(self._registered_classes)

    def get_single_node(self) -> yaml.Node:
        """Hook used when loading a single document.

        This is the hook we use to hook yatiml into ruamel.yaml. It is \
        called by the yaml libray when the user uses load() to load a \
        YAML document.

        Returns:
            A processed node representing the document.
        """
        node = super().get_single_node()
        if node is not None:
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
        if node is not None:
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
            return 'union of {}'.format([self.__type_to_desc(t) for t in types])

        if isinstance(type_, GenericMeta):
            if type_.__origin__ == List:
                return 'list of ({})'.format(self.__type_to_desc(type_.__args__[0]))
            if type_.__origin__ == Dict:
                return 'dict of string to ({})'.format(self.__type_to_desc(type_.__args__[1]))

        if type_ in self._registered_classes.values():
            return type_.__name__

        raise RuntimeError(('Unknown type {} in type_to_desc,'      # pragma: no cover
                ' please report a YAtiML bug.').format(type_))

    def __type_to_tag(self, type_: Type) -> str:
        """Convert a type to the corresponding YAML tag.

        Args:
            type_: The type to convert

        Returns:
            A string containing the YAML tag.
        """
        if type_ in scalar_type_to_tag:
            return scalar_type_to_tag[type_]

        if isinstance(type_, GenericMeta):
                if type_.__origin__ == List:
                    return 'tag:yaml.org,2002:seq'
                elif type_.__origin__ == Dict:
                    return 'tag:yaml.org,2002:map'

        if type_ in self._registered_classes.values():
            return '!{}'.format(type_.__name__)

        raise RuntimeError(('Unknown type {} in type_to_tag,'       # pragma: no cover
                ' please report a YAtiML bug.').format(type_))

    def __savorize(self, node: yaml.MappingNode, expected_type: Type) -> None:
        """Removes syntactic sugar from the node.

        This calls yatiml_savorize(), first on the class's base \
        classes, then on the class itself.

        Args:
            node: The node to modify.
            expected_type: The type to assume this type is.
        """
        for base_class in expected_type.__bases__:
            if base_class in self._registered_classes.values():
                self.__savorize(node, base_class)

        if hasattr(expected_type, 'yatiml_savorize'):
            cnode = ClassNode(node)
            expected_type.yatiml_savorize(cnode)

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
        recognized_types = self.__recognizer.recognize(node, expected_type)

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

        # remove syntactic sugar
        if recognized_type in self._registered_classes.values():
            self.__savorize(node, recognized_type)

        # process subnodes
        if isinstance(recognized_type, GenericMeta):
            if recognized_type.__origin__ == List:
                if node.tag != 'tag:yaml.org,2002:seq':
                    raise RecognitionError('{}{}Expected a {} here'.format(
                        node.start_mark, os.linesep, self.__type_to_desc(expected_type)))
                for item in node.value:
                    self.__process_node(item, recognized_type.__args__[0])
            elif recognized_type.__origin__ == Dict:
                if node.tag != 'tag:yaml.org,2002:map':
                    raise RecognitionError('{}{}Expected a {} here'.format(
                        node.start_mark, os.linesep, self.__type_to_desc(expected_type)))
                for key_node, value_node in node.value:
                    self.__process_node(value_node, recognized_type.__args__[1])

        elif recognized_type in self._registered_classes.values():
            for attr_name, type_, required in class_subobjects(expected_type):
                cnode = ClassNode(node)
                if cnode.has_attribute(attr_name):
                    subnode = cnode.get_attribute(attr_name)
                    self.__process_node(subnode, type_)

        return node

def set_document_type(loader_cls: Type, type_: Type) -> None:
    """Set the type corresponding to the whole document.

    Args:
        loader_cls: The loader class to set the document type for.
        type_: The type to loader should process the document into.
    """
    loader_cls.document_type = type_

    if not hasattr(loader_cls, '_registered_classes'):
        loader_cls._registered_classes = dict()


# Python errors if we define classes as Union[List[Type], Type]
# So List[Type] it is, and if the user ignores that and passes
# a single class, it'll work anyway, with a little mypy override.
def add_to_loader(loader_cls: Type, classes: List[Type]) -> None:
    """Registers one or more classes with a YAtiML loader.

    Once a class has been registered, it can be recognized and \
    constructed when reading a YAML text.

    Args:
        loader_cls: The loader to register the classes with.
        classes: The class(es) to register, a plain Python class or a \
                list of them.
    """
    if not isinstance(classes, list):
        classes = [classes]     # type: ignore

    for class_ in classes:
        tag = '!{}'.format(class_.__name__)
        loader_cls.add_constructor(tag, Constructor(class_))

        if not hasattr(loader_cls, '_registered_classes'):
            loader_cls._registered_classes = dict()
        loader_cls._registered_classes[tag] = class_
