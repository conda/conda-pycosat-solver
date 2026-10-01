# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause
"""
The hooks for the conda solver plugin system.
"""

from functools import cache
from typing import Iterable

from conda import __version__ as conda_version
from conda.plugins import hookimpl
from conda.plugins.types import CondaSolver
from packaging.version import Version

from .solve import PycosatSolver

# conda ships a built-in ``classic`` solver through 26.9; the remove-classic
# work no longer loads it.
CLASSIC_LAST_RELEASE = Version("26.9")


@cache
def _conda_has_classic() -> bool:
    """Return whether conda already ships a built-in ``classic`` solver."""
    return Version(conda_version) <= CLASSIC_LAST_RELEASE


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
