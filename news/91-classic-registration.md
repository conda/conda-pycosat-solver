### Bug fixes

* Detect whether another plugin provides `classic` from its registered solver hooks. Avoid duplicate solver registration with released conda versions, and provide the alias when conda no longer includes the solver. (#91)

### Other

* Require Python 3.11 or newer and include Python 3.13 and 3.14 in the package metadata. (#91)
* Use calendar versioning (`YY.MM.MICRO`), as agreed in #4.
