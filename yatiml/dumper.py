import enum
import json
import logging
from collections import UserString
from typing import Any, List, Optional
from typing_extensions import Type

from ruamel import yaml
from ruamel.yaml.events import (
        AliasEvent, DocumentEndEvent, MappingEndEvent, MappingStartEvent,
        ScalarEvent, SequenceEndEvent, SequenceStartEvent)

from yatiml.representers import (EnumRepresenter, Representer,
                                 UserStringRepresenter)

logger = logging.getLogger(__name__)


class JsonDumperState(enum.Enum):
    NONE = 0,
    SEQUENCE = 1,
    SEQUENCE_FIRST = 2,
    MAPPING_KEY = 3,
    MAPPING_KEY_FIRST = 4,
    MAPPING_VALUE = 5


class Dumper(yaml.RoundTripDumper):
    """The YAtiML Dumper class.

    Derive your own Dumper class from this one, then add classes to it \
    using add_to_dumper(). Set output_format = "json" to output JSON.
    """
    output_format = 'yaml'

    def __init__(
            self, stream: Any, default_style: Any,
            default_flow_style: Optional[bool], canonical: Optional[int],
            indent: Optional[int], width: Optional[int],
            allow_unicode: Optional[bool], line_break: Any, encoding: Any,
            explicit_start: Optional[bool], explicit_end: Optional[bool],
            version: Any, tags: Any, block_seq_indent: Any,
            top_level_colon_align: Any, prefix_colon: Any
            ) -> None:
        """Create a JsonDumper, called by ruamel.yaml."""
        yaml.RoundTripDumper.__init__(
                self, stream, default_style, default_flow_style, canonical,
                indent, width, allow_unicode, line_break, encoding,
                explicit_start, explicit_end, version, tags, block_seq_indent,
                top_level_colon_align, prefix_colon)

        self._json_state = [JsonDumperState.NONE]
        self._cur_indent = 0

        if self.requested_indent is not None:
            self._kv_sep = ': '
        else:
            self._kv_sep = ':'

    def emit(self, event: yaml.events.Event) -> None:
        """Emit an event.

        This is called by ruamel.yaml, and we dispatch to the original
        implementation (which emits YAML) or our emit_json() below if
        the user selected JSON output.

        Args:
            event: The event to output.
        """
        if self.output_format == 'json':
            self.emit_json(event)
        else:
            yaml.RoundTripDumper.emit(self, event)

    def emit_json(self, event: yaml.events.Event) -> None:
        """Emit a YAML event to the JSON output.

        Args:
            event: The event to output.
        """
        if isinstance(event, AliasEvent):
            raise RuntimeError('Aliases are not supported by JSON')
        elif isinstance(event, SequenceEndEvent):
            self._cur_indent -= self.best_sequence_indent
            self._do_endline()
            self.stream.write(']')
            self._json_state.pop()
        elif isinstance(event, MappingEndEvent):
            self._cur_indent -= self.best_map_indent
            self._do_endline()
            self.stream.write('}')
            self._json_state.pop()
        elif isinstance(event, DocumentEndEvent):
            self._do_endline()
        else:
            # top-level scalar, or continuing a sequence or mapping
            cur_level = len(self._json_state) - 1
            cur_state = self._json_state[cur_level]

            # write separator if necessary
            if cur_state == JsonDumperState.SEQUENCE:
                self.stream.write(',')
                self._do_endline()
            elif cur_state == JsonDumperState.MAPPING_KEY:
                self.stream.write(',')
                self._do_endline()
            elif cur_state == JsonDumperState.MAPPING_VALUE:
                self.stream.write(self._kv_sep)

            # output value
            if isinstance(event, SequenceStartEvent):
                self.stream.write('[')
                self._cur_indent += self.best_sequence_indent
                self._do_endline()
                self._json_state.append(JsonDumperState.SEQUENCE_FIRST)
            elif isinstance(event, MappingStartEvent):
                self.stream.write('{')
                self._cur_indent += self.best_map_indent
                self._do_endline()
                self._json_state.append(JsonDumperState.MAPPING_KEY_FIRST)
            elif isinstance(event, ScalarEvent):
                if event.tag == 'tag:yaml.org,2002:str':
                    self.stream.write(json.dumps(
                        event.value, ensure_ascii=not self.allow_unicode))
                elif event.tag == 'tag:yaml.org,2002:null':
                    self.stream.write('null')
                elif event.tag == 'tag:yaml.org,2002:bool':
                    self.stream.write(event.value.lower())
                elif event.tag == 'tag:yaml.org,2002:timestamp':
                    self.stream.write(json.dumps(
                        event.value, ensure_ascii=not self.allow_unicode))
                else:
                    self.stream.write(event.value)

            # set next state
            if cur_state == JsonDumperState.SEQUENCE_FIRST:
                self._json_state[cur_level] = JsonDumperState.SEQUENCE
            elif cur_state == JsonDumperState.MAPPING_KEY_FIRST:
                self._json_state[cur_level] = JsonDumperState.MAPPING_VALUE
            elif cur_state == JsonDumperState.MAPPING_KEY:
                self._json_state[cur_level] = JsonDumperState.MAPPING_VALUE
            elif cur_state == JsonDumperState.MAPPING_VALUE:
                self._json_state[cur_level] = JsonDumperState.MAPPING_KEY

    def _do_endline(self) -> None:
        """Write EOL and subsequent indent if enabled."""
        if self.requested_indent is not None:
            self.stream.write(self.best_line_break)
            self.stream.write(' ' * self._cur_indent)


# Python errors if we define classes as Union[List[Type], Type]
# So List[Type] it is, and if the user ignores that and passes
# a single class, it'll work anyway, with a little mypy override.
def add_to_dumper(dumper: Type, classes: List[Type]) -> None:
    """Register user-defined classes with the Dumper.

    This enables the Dumper to write objects of your classes to a \
    YAML file. Note that all the arguments are types, not instances!

    Args:
        dumper: Your dumper class(!), derived from yatiml.Dumper
        classes: One or more classes to add.
    """
    if not isinstance(classes, list):
        classes = [classes]  # type: ignore
    for class_ in classes:
        if issubclass(class_, enum.Enum):
            dumper.add_representer(class_, EnumRepresenter(class_))
        elif issubclass(class_, str) or issubclass(class_, UserString):
            dumper.add_representer(class_, UserStringRepresenter(class_))
        else:
            dumper.add_representer(class_, Representer(class_))
