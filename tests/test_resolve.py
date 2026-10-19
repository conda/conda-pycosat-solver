# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pytest
from conda.exceptions import ResolvePackageNotFound
from conda.models.match_spec import MatchSpec
from conda.models.records import PackageRecord

from conda_pycosat_solver.resolve import Resolve


def test_solve_missing_optional_package_raises_resolve_package_not_found():
    record = PackageRecord(
        name="available",
        version="1.0",
        build="0",
        build_number=0,
        subdir="noarch",
        depends=[],
    )
    resolve = Resolve({record: record})
    spec = MatchSpec("missing", optional=True)

    with pytest.raises(ResolvePackageNotFound) as exc:
        resolve.solve([spec])

    assert exc.value.bad_deps == (spec,)
