[//]: # (current developments)

## 26.10.0 (2026-10-22)

### Bug fixes

* Detect whether another plugin provides `classic` from its registered solver hooks. Avoid duplicate solver registration with released conda versions, and provide the alias when conda no longer includes the solver. (#91)
* Inherit conda's update notice so it recommends `conda self update` when available and includes `--override-frozen` when needed. (#112)
* Raise `ResolvePackageNotFound` instead of `TypeError` when the reduced index is empty and a requested package is missing. (#112)
* Raise `NoChannelsConfiguredError` when a direct solve requests packages without configured channels. (conda/conda#15345)
* Raise `PackagesNotFoundInChannelsError` for unavailable packages and `PackagesNotFoundInPrefixError` for missing installed packages, including the target prefix. (conda/conda#15653)

### Other

* Require Python 3.11 or newer and include Python 3.13 and 3.14 in the package metadata. (#91)
* Require conda 26.5 or newer to match the solver APIs used by this package.
* Use calendar versioning (`YY.MM.MICRO`), as agreed in #4.
* Use `retrying with next repodata source.` for repodata retry messages. (conda/conda#16599)

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
