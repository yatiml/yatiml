##########
Change Log
##########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

0.10.0
******

Incompatible changes
--------------------

* Ignore abstract base classes (abc.ABC and/or @abstractmethod)

New functionality
-----------------

* Easier-to-understand error messages
* Installation via Conda (already worked, now documented)
* Small documentation improvements
* Python 3.11 support
* Compatibility with ruamel.yaml 0.17

Fixes
-----

* Bug in map_attribute_to_index

Removed
-------

* Support for Python 3.6


0.9.0
*****

New functionality
-----------------

* Support for Python 3.10 (worked fine already, now official)
* Error messages now quote attribute names, making them easier to read.


Fixes
-----

* `map_attribute_to_index()` caused load failure for dictionaries indexed by
  a user-defined string class.
* All examples in the documentation now use the new `_yatiml_*` function names,
  instead of the old ones without the leading underscore.


Removed
-------

* Loader and Dumper classes, which were deprecated and broken in 0.8.0. Please
  use the new `load_function`,   `dump_function` and `dumps_function` functions
  instead.


0.8.0
*****

Incompatible changes
--------------------

* Accept explicit tags only if compatible with the recognised type(s)

New functionality
-----------------

* Support for untyped documents and attributes
* Support for Any-typed documents and attributes
* Support for Python dataclasses


Fixes
-----

* Dumping of OrderedDict to a file (but not to a string) produced a stray
  !!omap.
* Various fixes and improvements to development infrastructure


Removed
-------

* Official support for Python 3.5, which is no longer supported upstream. It
  will probably still work, but getting anything to install on 3.5 is getting to
  be pretty difficult so it's probably time to upgrade.


0.7.0
*****

Incompatible changes
--------------------

* Use seasoning functions only on the class they're defined on

New functionality
-----------------

* New yatiml.String to mark string-serialisable classes
* User-defined strings may be used as dictionary keys
* Support for index mappings
* Support for latest ruamel.yaml
* Documentation improvements


0.6.1
*****

Incompatible changes
--------------------

* Use datetime.date instead of datetime.datetime

New functionality
-----------------

* Support for loading and dumping pathlib.Path objects
* Support for Python 3.9


0.6.0
*****

New functionality
-----------------

* New make_loader and make_dumper functions improve ease-of-use
* JSON support
* Support for Mapping and Sequence types
* UnknownNode.require_attribute_value_not() function
* Node.remove_attributes_with_default_values() function
* Recipe for seasoning Enums

Fixes
-----

* Various documentation improvements
* Better error message if constructor raises


0.5.1
*****

Fixes
-----

* Fixed support for Python 3.5.1 (again, sorry)

0.5.0
*****

Incompatible changes
--------------------

* yatiml_* methods should now be called _yatiml_*
* Dropped support for Python 3.4, which is end-of-life

Fixes
-----

* Savourised classes in lists and dicts now load correctly
* Fixed compatibility with the latest versions of ruamel.yaml
* Fixed support for Python 3.5.1

0.4.2
*****

Fixes
-----

* Don't generate cross-references for enum values
* Various small fixes

0.4.1
*****

New functionality
-----------------

* Added fix_union_bool type for fixing Union[int, bool] on Python < 3.7
* Added support for Python 3.7

Fixes
-----

* Return scalar values with the correct type

0.4.0
*****

New functionality
-----------------

* Extended map_to_seq seasoning
* Support for YAML timestamp / Python datetime
* Support for YAML keys with dashes

Fixes
-----

* Much improved error messages

0.3.0
*****

New functionality
-----------------

* Support for classes that are represented by a string in the YAML file
* New unified yatiml.Node interface (API change)

Fixes
-----

* Small improvements to documentation
* Miscellaneous small fixes

0.2.0
*****

New functionality
-----------------

* Support for enumerations
* Support for user-defined string types

Fixes
-----

* Various small tooling fixes
* Some refactoring

0.1.0
*****

* Initial release with basic functionality
