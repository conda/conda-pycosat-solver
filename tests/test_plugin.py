# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from conda_pycosat_solver import plugin
from conda_pycosat_solver.plugin import conda_solvers

if TYPE_CHECKING:
    from pytest import Monkeypatch


@pytest.fixture(autouse=True)
def clear_conda_has_classic_cache():
    # _conda_has_classic is cached; ensure each test starts fresh and doesn't
    # leak its cached result into subsequent tests.
    plugin._conda_has_classic.cache_clear()
    yield
    plugin._conda_has_classic.cache_clear()


def test_plugin_yields_pycosat():
    solvers = list(conda_solvers())
    names = [s.name for s in solvers]
    assert "pycosat" in names


def test_plugin_has_classic_true(monkeypatch: Monkeypatch):
    monkeypatch.setattr(plugin, "conda_version", "26.9")
    assert plugin._conda_has_classic()
    names = [s.name for s in conda_solvers()]
    assert "classic" not in names


def test_plugin_has_classic_false(monkeypatch: Monkeypatch):
    monkeypatch.setattr(plugin, "conda_version", "26.10")
    assert not plugin._conda_has_classic()
    names = [s.name for s in conda_solvers()]
    assert "classic" in names


def test_plugin_has_classic_is_cached(monkeypatch: Monkeypatch):
    monkeypatch.setattr(plugin, "conda_version", "26.9")
    assert plugin._conda_has_classic()

    # changing conda_version after the first call has no effect until the
    # cache is cleared
    monkeypatch.setattr(plugin, "conda_version", "26.10")
    assert plugin._conda_has_classic()

    plugin._conda_has_classic.cache_clear()
    assert not plugin._conda_has_classic()
