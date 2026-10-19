# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from types import SimpleNamespace

import pytest

from conda_pycosat_solver import plugin
from conda_pycosat_solver.plugin import conda_solvers

SUBSET_HOOK_CALLER = "conda.plugins.manager.CondaPluginManager.subset_hook_caller"


@pytest.fixture(autouse=True)
def clear_conda_has_classic_cache():
    # _conda_has_classic is cached; ensure each test starts fresh and doesn't
    # leak its cached result into subsequent tests.
    plugin._conda_has_classic.cache_clear()
    yield
    plugin._conda_has_classic.cache_clear()


def test_plugin_yields_pycosat():
    names = [s.name for s in conda_solvers()]
    assert "pycosat" in names


def test_plugin_has_classic_true(mocker):
    # another plugin (e.g. conda's own built-in classic solver) already
    # provides a "classic" solver
    mocker.patch(
        SUBSET_HOOK_CALLER,
        return_value=lambda: [[SimpleNamespace(name="classic")]],
    )
    assert plugin._conda_has_classic()
    names = [s.name for s in conda_solvers()]
    assert "classic" not in names


def test_plugin_has_classic_false(mocker):
    # no other plugin provides a "classic" solver (e.g. the classic-removal
    # work has landed on this checkout), regardless of what conda.__version__
    # reports -- a dev/pre-release build of that work can report a version
    # that sorts before the release it belongs to.
    mocker.patch(SUBSET_HOOK_CALLER, return_value=lambda: [[]])
    assert not plugin._conda_has_classic()
    names = [s.name for s in conda_solvers()]
    assert "classic" in names


def test_plugin_has_classic_is_cached(mocker):
    mocked = mocker.patch(
        SUBSET_HOOK_CALLER,
        side_effect=[
            lambda: [[SimpleNamespace(name="classic")]],  # first call
            lambda: [[]],  # second call
        ],
    )

    assert plugin._conda_has_classic()
    assert mocked.call_count == 1

    # still cached: a second call must not re-invoke subset_hook_caller
    assert plugin._conda_has_classic()
    assert mocked.call_count == 1

    plugin._conda_has_classic.cache_clear()
    assert not plugin._conda_has_classic()
    assert mocked.call_count == 2
