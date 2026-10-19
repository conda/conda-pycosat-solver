# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause
"""
The hooks for the conda solver plugin system.
"""

import sys
from collections.abc import Iterable
from functools import cache

from conda.base.context import context
from conda.plugins import hookimpl
from conda.plugins.types import CondaSolver

from .solve import PycosatSolver


@cache
def _conda_has_classic() -> bool:
    """Return whether any other registered plugin already provides a ``classic`` solver.

    This checks the plugin manager's actual hook results rather than
    comparing ``conda.__version__`` against a cutoff: a dev/pre-release build
    of conda's classic-removal work can report a version that sorts *before*
    the release it belongs to (e.g. ``26.10.0.dev5`` sorts below ``26.10``),
    even though that exact build already stopped loading the classic solver.
    Version comparison can't distinguish that case from an actual pre-26.10
    release, so it's not a reliable signal here.

    Uses ``subset_hook_caller`` to exclude this module's own ``conda_solvers``
    hookimpl from the call, since this function is itself called from within
    that hookimpl -- calling the unfiltered hook here would recurse into it.
    """
    others = context.plugin_manager.subset_hook_caller(
        "conda_solvers",
        remove_plugins=[sys.modules[__name__]],
    )
    return any(solver.name == "classic" for solvers in others() for solver in solvers)


@hookimpl
def conda_solvers() -> Iterable[CondaSolver]:
    """
    The conda plugin hook implementation to load the solver into conda.
    """
    yield CondaSolver(
        name="pycosat",
        backend=PycosatSolver,
    )
    # Only register the "classic" alias when conda does not already provide it.
    if not _conda_has_classic():
        yield CondaSolver(
            name="classic",
            backend=PycosatSolver,
        )
