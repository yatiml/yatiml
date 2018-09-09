# -*- coding: utf-8 -*-
"""The :mod:`yatiml` module is the main API for YAtiML.

This module contains all the functions you need to use YAtiML.

Below, you will also find documentation for submodules. That is \
developer documentation, you do not need it to use YAtiML.
"""

__version__ = '0.1.0'

__author__ = 'Lourens Veen'
__email__ = 'l.veen@esciencecenter.nl'


from yatiml.exceptions import RecognitionError
from yatiml.loader import Loader, add_to_loader, set_document_type
from yatiml.dumper import Dumper, add_to_dumper
from yatiml.helpers import ClassNode

__all__ = [
        'RecognitionError',
        'ClassNode',
        'Loader',
        'add_to_loader', 'set_document_type',
        'Dumper', 'add_to_dumper']
