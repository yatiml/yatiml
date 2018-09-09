import copy
import inspect
import os
from typing import Any, Dict, Generator, GenericMeta, List, Tuple, Type, Union

import ruamel.yaml as yaml

from yatiml.exceptions import RecognitionError
from yatiml.helpers import ClassNode


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
        for name, type_, required in loader._Loader__class_subobjects(self.class_):
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

        if type(type_).__name__ == 'UnionMeta':
            return 'union of {}'.format(
                    [self.__type_to_desc(t) for t in type_.__union_params__])

        if isinstance(type_, GenericMeta):
            if type_.__origin__ == List:
                return 'list of ({})'.format(self.__type_to_desc(type_.__args__[0]))
            if type_.__origin__ == Dict:
                return 'dict of string to ({})'.format(self.__type_to_desc(type_.__args__[1]))

        if type_ in self.registered_classes:
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
        scalar_type_to_tag = {
                str: 'tag:yaml.org,2002:str',
                int: 'tag:yaml.org,2002:int',
                float: 'tag:yaml.org,2002:float',
                bool: 'tag:yaml.org,2002:bool',
                None: 'tag:yaml.org,2002:null',
                type(None): 'tag:yaml.org,2002:null'
                }

        if type_ in scalar_type_to_tag:
            return scalar_type_to_tag[type_]

        if isinstance(type_, GenericMeta):
                if type_.__origin__ == List:
                    return 'tag:yaml.org,2002:seq'
                elif type_.__origin__ == Dict:
                    return 'tag:yaml.org,2002:map'

        if type_ in self.registered_classes:
            return '!{}'.format(type_.__name__)

        raise RuntimeError(('Unknown type {} in type_to_tag,'       # pragma: no cover
                ' please report a YAtiML bug.').format(type_))

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

    def __class_subobjects(
            self, class_: Type
            ) -> Generator[Tuple[str, Type, bool], None, None]:
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
            attr_type = argspec.annotations.get(attr_name, Any)
            yield attr_name, attr_type, i < first_optional

    def __recognize_user_class(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a user-defined class in the node.

        This tries to recognize only exactly the specified class. It \
        recurses down into the class's attributes, but not to its \
        subclasses. See also __recognize_user_classes().

        Args:
            node The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing the user-defined class, or an empty list.
        """
        if hasattr(expected_type, 'yatiml_recognize'):
            try:
                cnode = ClassNode(node)
                expected_type.yatiml_recognize(cnode)
                return [expected_type]
            except RecognitionError:
                return []
        else:
            # auto-recognize based on constructor signature
            if not isinstance(node, yaml.MappingNode):
                return []

            for attr_name, type_, required in self.__class_subobjects(expected_type):
                cnode = ClassNode(node)
                if cnode.has_attribute(attr_name):
                    subnode = cnode.get_attribute(attr_name)
                    recognized_types = self.__recognize(subnode, type_)
                    if len(recognized_types) == 0:
                        return []
                elif required:
                    return []

            return [expected_type]

    def __recognize_user_classes(
            self,
            node: yaml.Node,
            expected_type: Type
            ) -> List[Type]:
        """Recognize a user-defined class in the node.

        This returns a list of classes from the inheritance hierarchy \
        headed by expected_type which match the given node and which \
        do not have a registered derived class that matches the given \
        node. So, the returned classes are the most derived matching \
        classes that inherit from expected_type.

        This function recurses down the user's inheritance hierarchy.

        Args:
            node: The node to recognize.
            expected_type: A user-defined class.

        Returns:
            A list containing matched user-defined classes.
        """
        # Let the user override with an explicit tag
        if node.tag in self.registered_tags:
            return [self.yaml_constructors[node.tag].class_]

        recognized_subclasses = []
        for other_class in self.registered_classes:
            if expected_type in other_class.__bases__:
                sub_subclasses = self.__recognize_user_classes(node, other_class)
                recognized_subclasses.extend(sub_subclasses)

        if len(recognized_subclasses) == 0:
            recognized_subclasses = self.__recognize_user_class(node, expected_type)

        return recognized_subclasses

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
        recognized_types = None
        if expected_type in [str, int, float, bool, None, type(None)]:
            recognized_types = self.__recognize_scalar(node, expected_type)
        elif type(expected_type).__name__ == 'UnionMeta':
            recognized_types = self.__recognize_union(node, expected_type)
        elif isinstance(expected_type, GenericMeta):
                if expected_type.__origin__ == List:
                    recognized_types = self.__recognize_list(node, expected_type)
                elif expected_type.__origin__ == Dict:
                    recognized_types = self.__recognize_dict(node, expected_type)
        elif expected_type in self.registered_classes:
            recognized_types = self.__recognize_user_classes(node, expected_type)

        print('{} {} {}'.format(
            expected_type, type(expected_type), type(expected_type).__name__))
        if recognized_types is None:
            raise RecognitionError(('Could not recognize for type {},'
                    ' is it registered?').format(expected_type))
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

        elif recognized_type in self.registered_classes:
            for attr_name, type_, required in self.__class_subobjects(expected_type):
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

    if not hasattr(loader_cls, 'registered_classes'):
        loader_cls.registered_classes = []
    if not hasattr(loader_cls, 'registered_tags'):
        loader_cls.registered_tags = []


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

        if not hasattr(loader_cls, 'registered_classes'):
            loader_cls.registered_classes = []
        loader_cls.registered_classes.append(class_)

        if not hasattr(loader_cls, 'registered_tags'):
            loader_cls.registered_tags = []
        loader_cls.registered_tags.append(tag)
