###########
Change Log
###########

All notable changes to this project will be documented in this file.
This project adheres to `Semantic Versioning <http://semver.org/>`_.

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
