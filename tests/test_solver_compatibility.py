# Copyright (C) 2012 Anaconda, Inc
# Copyright (C) 2023 conda
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import pytest
from conda import __version__ as conda_version
from conda.base.constants import UpdateModifier
from conda.base.context import context, reset_context
from conda.common.serialize import json
from conda.core.index import Index, ReducedIndex
from conda.core.prefix_data import PrefixData
from conda.core.subdir_data import SubdirData
from conda.exceptions import (
    NoChannelsConfiguredError,
    PackagesNotFoundInChannelsError,
    PackagesNotFoundInPrefixError,
)
from conda.models.match_spec import MatchSpec
from conda.models.records import PackageRecord
from conda.models.version import VersionOrder
from conda.testing.solver_helpers import SimpleEnvironment

from conda_pycosat_solver import solve as solve_module
from conda_pycosat_solver.solve import PycosatSolver


@pytest.fixture
def solver_env(tmp_path, tmp_pkgs_dir, reset_conda_context, monkeypatch):
    monkeypatch.setenv("CONDA_SOLVER", "pycosat")
    reset_context(search_path=())
    return SimpleEnvironment(tmp_path, PycosatSolver, subdirs=("noarch",))


@pytest.mark.parametrize(
    "method", ["solve_final_state", "solve_for_diff", "solve_for_transaction"]
)
def test_requested_packages_without_channels(solver_env, mocker, method):
    solver_env.repo_packages = {}
    solver = solver_env.solver(add=("sample",), remove=())
    collect_metadata = mocker.spy(solver, "_collect_all_metadata")

    with pytest.raises(NoChannelsConfiguredError) as exc:
        getattr(solver, method)()

    assert exc.value.dump_map()["packages"] == ["sample"]
    collect_metadata.assert_not_called()


@pytest.mark.parametrize("remove_installed", [False, True])
def test_no_channels_without_requested_packages(solver_env, remove_installed):
    solver_env.repo_packages = {}
    if remove_installed:
        solver_env.installed_packages = [
            PackageRecord(
                name="sample",
                version="1.0",
                build="0",
                build_number=0,
                subdir="noarch",
                depends=[],
            )
        ]
    solver = solver_env.solver(add=(), remove=("sample",) if remove_installed else ())

    assert not solver.solve_final_state()


def test_remove_missing_package_reports_prefix(solver_env):
    solver_env.repo_packages = [
        PackageRecord(
            name="sample",
            version="1.0",
            build="0",
            build_number=0,
            subdir="noarch",
            depends=[],
        )
    ]
    solver = solver_env.solver(add=(), remove=("sample",))

    with pytest.raises(PackagesNotFoundInPrefixError) as exc:
        solver.solve_final_state()

    error_details = exc.value.dump_map()
    assert error_details["package_name"] == ("sample",)
    assert error_details["prefix"] == solver.prefix


def test_nondefault_repodata_retry_message(solver_env, mocker):
    solver_env.repo_packages = [
        PackageRecord(
            name="sample",
            version="1.0",
            build="0",
            build_number=0,
            subdir="noarch",
            depends=[],
        )
    ]
    fixture_solver = solver_env.solver(add=("sample",), remove=())
    solver = PycosatSolver(
        prefix=fixture_solver.prefix,
        channels=fixture_solver.channels,
        subdirs=("noarch",),
        specs_to_add=("sample",),
        repodata_fn="current_repodata.json",
    )
    spinner = mocker.spy(solve_module, "get_spinner")

    solution = solver.solve_final_state()

    assert [record.name for record in solution] == ["sample"]
    solve_calls = [
        call for call in spinner.call_args_list if call.args == ("Solving environment",)
    ]
    assert len(solve_calls) == 1
    assert solve_calls[0].kwargs["fail_message"] == (
        "retrying with next repodata source.\n"
    )


@pytest.mark.skipif(
    not hasattr(context, "exclude_newer_policy"),
    reason="conda does not support exclude-newer policies",
)
@pytest.mark.parametrize("policy", ["global", "channel", "package"])
def test_exclude_newer_selects_older_package(
    solver_env, tmp_path, policy, http_test_server
):
    solver_env = SimpleEnvironment(
        http_test_server.directory, PycosatSolver, subdirs=("noarch",)
    )
    solver_env.repo_packages = [
        PackageRecord(
            name="sample",
            version=version,
            build="0",
            build_number=0,
            subdir="noarch",
            timestamp=timestamp,
            depends=[],
        )
        for version, timestamp in (("1.0", 1704067200000), ("2.0", 1706745600000))
    ]
    solver_env.solver(add=(), remove=())
    channel = http_test_server.get_url("channels/test")
    cutoff = "2024-01-15"
    settings = {
        "global": {"exclude_newer": cutoff},
        "channel": {
            "channel_settings": [
                {
                    "channel": channel,
                    "exclude_newer": cutoff,
                }
            ]
        },
        "package": {"exclude_newer_package": {"sample": cutoff}},
    }
    condarc = tmp_path / "condarc"
    condarc.write_text(json.dumps(settings[policy]))
    reset_context(search_path=(str(condarc),))

    solver = PycosatSolver(
        prefix=tmp_path / "prefix",
        channels=(channel,),
        subdirs=("noarch",),
        specs_to_add=("sample",),
    )
    reset_context(search_path=())
    solution = solver.solve_final_state()

    assert [(record.name, record.version) for record in solution] == [("sample", "1.0")]


@pytest.mark.parametrize("index_prefix", [None, "target", "other"])
@pytest.mark.parametrize("realized", [False, True])
def test_solve_with_provided_index(
    solver_env, tmp_path, mocker, index_prefix, realized
):
    records = {
        name: PackageRecord(
            name=name,
            version="1.0",
            build="0",
            build_number=0,
            subdir="noarch",
            channel=(tmp_path / "channels" / "test").as_uri(),
            depends=depends,
        )
        for name, depends in (
            ("installed-app", ["dependency"]),
            ("dependency", ["leaf"]),
            ("leaf", []),
            ("requested", []),
            ("unrelated", []),
        )
    }
    solver_env.repo_packages = list(records.values())
    solver_env.installed_packages = [
        records[name] for name in ("installed-app", "dependency", "leaf")
    ]
    solver = solver_env.solver(add=("requested",), remove=())
    source_prefix = (
        PrefixData(solver.prefix if index_prefix == "target" else tmp_path / "other")
        if index_prefix is not None
        else None
    )
    provided_index = Index(
        channels=solver.channels,
        prepend=False,
        subdirs=("noarch",),
        use_cache=False,
        use_system=True,
        prefix=source_prefix,
    )
    if realized:
        provided_index.data
    elif index_prefix != "other":
        mocker.patch.object(
            Index, "_realize", side_effect=AssertionError("Eager index")
        )
    solver._index = provided_index

    solution = solver.solve_final_state()

    assert {record.name for record in solution} == {
        "installed-app",
        "dependency",
        "leaf",
        "requested",
    }
    assert provided_index.prefix_data is source_prefix
    assert ("_data" in provided_index.__dict__) is (realized or index_prefix == "other")


def test_prepare_reduces_provided_index_for_each_spec_set(tmp_path, mocker):
    solver = PycosatSolver(prefix=tmp_path, channels=())
    provided_index = Index(prepend=False)
    reduced_indexes = [mocker.Mock(spec=ReducedIndex), mocker.Mock(spec=ReducedIndex)]
    reduce_index = mocker.patch.object(
        Index, "get_reduced_index", autospec=True, side_effect=reduced_indexes
    )
    mocker.patch("conda_pycosat_solver.solve.Resolve")
    mocker.patch.object(Index, "_realize", side_effect=AssertionError("Eager index"))
    solver._index = provided_index

    for name, reduced_index in zip(("first", "second"), reduced_indexes):
        prepared_index, _ = solver._prepare({MatchSpec(name)})
        assert prepared_index is reduced_index

    assert "_data" not in provided_index.__dict__
    assert provided_index.prefix_data is None
    assert reduce_index.call_count == 2
    for call in reduce_index.call_args_list:
        assert call.args[0].prefix_data.prefix_path == tmp_path


def test_missing_pinned_version_reports_channels(solver_env, monkeypatch):
    solver_env.repo_packages = [
        PackageRecord(
            name=name,
            version="1.0",
            build="0",
            build_number=0,
            subdir="noarch",
            depends=depends,
        )
        for name, depends in (("app", ["dependency >=1"]), ("dependency", []))
    ]
    solver = solver_env.solver(add=("app",), remove=())
    channels = tuple(channel.url() for channel in solver.channels)
    monkeypatch.setenv("CONDA_CHANNELS", ",".join(channels))
    monkeypatch.setenv("CONDA_PINNED_PACKAGES", "dependency=99")
    reset_context(search_path=())

    with pytest.raises(PackagesNotFoundInChannelsError) as exc:
        solver.solve_final_state(update_modifier=UpdateModifier.FREEZE_INSTALLED)

    assert tuple(map(str, exc.value.packages)) == ("dependency=99",)
    assert exc.value.channel_urls == channels


@pytest.mark.skipif(
    VersionOrder(conda_version) < VersionOrder("26.7.0"),
    reason="conda 26.7 introduced the current update-notice commands",
)
@pytest.mark.parametrize(
    "has_conda_self,is_frozen,expected_command",
    [
        (True, False, "conda self update"),
        (True, True, "conda self update"),
        (False, False, "conda update -n base -c test conda"),
        (False, True, "conda update -n base -c test conda --override-frozen"),
    ],
)
def test_outdated_conda_update_command(
    solver_env, monkeypatch, mocker, capsys, has_conda_self, is_frozen, expected_command
):
    monkeypatch.setenv("CONDA_NOTIFY_OUTDATED_CONDA", "true")
    monkeypatch.setenv("CONDA_QUIET", "false")
    reset_context(search_path=())
    solver_env.installed_packages = [
        PackageRecord(
            name=name,
            version="0.0.1",
            build="0",
            build_number=0,
            subdir="noarch",
            channel="test",
        )
        for name in (("conda", "conda-self") if has_conda_self else ("conda",))
    ]
    solver = solver_env.solver(add=(), remove=())
    mocker.patch(
        "conda.base.context.Context.conda_prefix",
        new_callable=mocker.PropertyMock,
        return_value=solver.prefix,
    )
    if is_frozen:
        (PrefixData(solver.prefix).prefix_path / "conda-meta" / "frozen").touch()
    mocker.patch.object(
        SubdirData,
        "query_all",
        return_value=[
            PackageRecord.from_objects(
                solver_env.installed_packages[0], version="99.0.0"
            )
        ],
    )

    solver._notify_conda_outdated(link_precs=())

    commands = [
        line.strip()
        for line in capsys.readouterr().err.splitlines()
        if line.strip().startswith(("$ conda", "conda install"))
    ]
    assert commands == [f"$ {expected_command}"]
