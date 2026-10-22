[//]: # (current developments)

## 26.10.0 (2026-10-22)

### Bug fixes

* Detect whether another plugin provides `classic` from its registered solver hooks. Avoid duplicate solver registration with released conda versions, and provide the alias when conda no longer includes the solver. (#91)
* Inherit conda's update notice so it recommends `conda self update` when available and includes `--override-frozen` when needed. (#112)
* Raise `ResolvePackageNotFound` instead of `TypeError` when the reduced index is empty and a requested package is missing. (#112)

### Other

* Require Python 3.11 or newer and include Python 3.13 and 3.14 in the package metadata. (#91)
* Use calendar versioning (`YY.MM.MICRO`), as agreed in #4.

### Contributors

* @jezdez
* @kenodegard
* @conda-bot
* @dependabot[bot]
* @pre-commit-ci[bot]



## 0.1.0 (2026-09-25)

### Enhancements

* Initial release of conda's pycosat-based solver as a standalone plugin.
* Provide `--solver=pycosat` and retain `classic` as a permanent compatibility alias.

### Bug fixes

* Preserve timestamp cutoffs, lazy supplied indexes, and channel information for missing pinned versions when extracting the solver from conda. (#71)

### Other

* Stop using %-style formatting. (#7)
