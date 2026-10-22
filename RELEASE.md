# Release process

Use calendar versions in the form `YY.MM.MICRO`, without a `v` prefix, as
agreed in [#4](https://github.com/conda/conda-pycosat-solver/issues/4).
The package version comes from Git tags through hatch-vcs.

## Prepare the release

1. Search for an existing release tracker before opening an issue titled
   ``Release `YY.MM.MICRO` ``. Record the release pilot, included changes,
   downstream dependencies, and the checklist below. Pin the tracker.
2. Fetch `origin` and its tags. Start a release PR branch from `origin/main`
   in a clean checkout, preserving unrelated work.
3. Compare changes since the previous release with the fragments in `news/`.
   Add missing entries, including changed Python or conda requirements.
   Move any fragments already shipped into their historical changelog entry.
4. Keep the `[//]: # (current developments)` marker in `CHANGELOG.md`.
   Update `.authors.yml` for contributors or aliases that rever does not know.
   Commit the prepared fragments before generating the release notes.
5. Run the configured authors and changelog activities together:

   ```console
   rever --force YY.MM.MICRO
   ```

   Rever creates local commits for the author files and changelog, and consumes
   the news fragments. Review those commits and include the fragment deletions
   in the release PR. Check that the release date matches the intended date.
6. Confirm the latest tests, shared solver tests, and canary build passed for
   the code being released. Check the package version and metadata in built
   artifacts. For a release needed by a conda PR, also confirm the plugin works
   with that PR and with the released conda versions it must support.
7. Push the release branch and open a PR targeting `main`. Link the tracker
   with `Xref #<issue>` so merging the PR leaves publication work open.
8. Save a draft GitHub release with the version as its tag, `main` as its target,
   and the new changelog entry as its notes. Publication follows PR review and
   merge.

## Publish and distribute

1. Merge the reviewed release PR. Check that the draft targets the merged
   commit and that its date and notes are current, then publish the release.
2. Confirm the `Upload release` workflow succeeds. It attaches the source
   archive, its SHA-256 checksum, and GitHub artifact attestations. Verify the
   checksum and attestation before using the archive in feedstocks.
3. Update the
   [conda-forge feedstock](https://github.com/conda-forge/conda-pycosat-solver-feedstock)
   and [Anaconda Recipes feedstock](https://github.com/AnacondaRecipes/conda-pycosat-solver-feedstock).
   Update source hashes, Python and conda requirements, and build dependencies
   as needed. Test both `--solver=pycosat` and `--solver=classic`, and require
   the installed package and distribution metadata to report the release version.
4. Confirm the release is installable from each target channel. A merged
   feedstock PR does not establish package availability.
5. For coordinated conda releases, raise the conda recipe and test requirements
   to the published solver version before merging the extraction PR. Record
   feedstock PRs and package availability in the tracker.
6. Arrange packaging handoff and release announcements, then close the tracker
   after its tasks are complete.

## Tracker checklist

```markdown
- [ ] Merge required solver changes
- [ ] Open the release PR
- [ ] Review and merge the release PR
- [ ] Prepare a draft GitHub release
- [ ] Publish the GitHub release and verify its source archive and attestation
- [ ] Update the conda-forge feedstock and verify channel availability
- [ ] Update the Anaconda Recipes feedstock and verify channel availability
- [ ] Update dependent conda requirements, if applicable
- [ ] Complete packaging handoff and release announcements
```
