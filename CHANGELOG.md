[//]: # (current developments)

## 0.1.0 (2026-09-25)

### Enhancements

* Initial release of conda's pycosat-based solver as a standalone plugin.
* Provide `--solver=pycosat` and retain `classic` as a permanent compatibility alias.

### Bug fixes

* Preserve timestamp cutoffs, lazy supplied indexes, and channel information for missing pinned versions when extracting the solver from conda. (#71)

### Other

* Stop using %-style formatting. (#7)
