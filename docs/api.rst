API Reference
=============

Loading / Saving
----------------

.. autofunction:: yatiml.load_function
.. autofunction:: yatiml.dumps_function
.. autofunction:: yatiml.dumps_json_function
.. autofunction:: yatiml.dump_function
.. autofunction:: yatiml.dump_json_function

Seasoning
---------

.. autoclass:: yatiml.UnknownNode
    :no-special-members:

.. autoclass:: yatiml.Node
    :no-special-members:

Errors
------

.. autoclass:: yatiml.RecognitionError
.. autoclass:: yatiml.SeasoningError

Miscellaneous
-------------

.. autoclass:: yatiml.bool_union_fix
.. autoclass:: yatiml.logger
.. autoclass:: yatiml.String

Deprecated
----------

.. autoclass:: yatiml.Dumper
    :exclude-members: emit, emit_json

.. autofunction:: yatiml.add_to_dumper

.. autoclass:: yatiml.Loader
    :exclude-members: get_node, get_single_node

.. autofunction:: yatiml.add_to_loader
.. autofunction:: yatiml.set_document_type
