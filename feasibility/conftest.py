"""Fixtures for the feasibility guard tests.

Each test module here exposes two interfaces: a ``run_all(path)`` driver used from the
command line, and per-guard ``test_T*`` functions that take the loaded artifact as their
single argument. Under pytest those argument names are fixture requests, so they are
defined here and loaded from the committed artifacts in ``data/``.

Fixtures are READ-ONLY. Nothing here regenerates an artifact or writes anything under
``data/``. Paths honour the same environment variables the modules' own
``test_*_passes_all_guards`` wrappers read, so both entry points always agree, and they
resolve against the repo root so the suite runs from any working directory.

CLAUDE.md section 4 bans decorators; ``@pytest.fixture`` is the sanctioned exception for
files under ``feasibility/`` and ``tests/``, since a fixture cannot be written as a plain
function. Fixture bodies themselves follow section 4.
"""

import json
import os

import pandas as pd
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CURVE_M1 = "data/tradeoff_curve.json"
CURVE_M2 = "data/tradeoff_curve_v2.json"


def resolve(path):
    """Interpret an artifact path relative to the repo root, not the cwd."""
    if os.path.isabs(path):
        return path
    return os.path.join(REPO_ROOT, path)


def require(path, what):
    """Return the resolved path, or skip with a named reason if it is absent.

    Skipping only on a MISSING FILE is deliberate: a missing artifact must read as
    cannot-run, never as a silent pass, and never as a substantive failure.
    """
    resolved = resolve(path)
    if not os.path.exists(resolved):
        pytest.skip(f"artifact not present: {path} ({what})")
    return resolved


def load_curve(path, what):
    """Load one coverage-sweep curve JSON.

    Parameterised by path so the same three tradeoff guards can run against either the
    committed M1 curve or the promoted M2 curve.
    """
    resolved = require(path, what)
    with open(resolved) as f:
        return json.load(f)


@pytest.fixture(scope="session")
def data_dir():
    """The artifact directory itself.

    test_manifest.py joins names onto this and derives each .manifest.json sidecar from
    them, so this is a directory path, not a loaded file.
    """
    return require(os.environ.get("DATA_DIR", "data"), "artifact directory")


@pytest.fixture(scope="session")
def df():
    """The raw N-1 dataset, unfiltered.

    Deliberately NOT make_splits.load_dataset: that drops the outaged_type == "none"
    base-case rows and the non-converged rows, but test_dataset T1 tests exactly the
    base-case rows and T7/T8 apply the converged filter themselves. A pre-filtered frame
    would leave T1 asserting over zero rows, which passes vacuously.
    """
    path = require(os.environ.get("DATASET_PATH", "data/dataset.parquet"),
                   "N-1 dataset; regenerate with feasibility/generate_dataset.py")
    return pd.read_parquet(path)


@pytest.fixture(scope="session")
def ctx():
    """The fitted screener pipeline context.

    Built by the module's own build_context so the fixture cannot drift from the
    split/fit/calibrate/gate sequence the guards assert about. T6 re-runs make_splits and
    refits, so a hand-rolled context here would have T6 comparing conftest against
    make_splits rather than make_splits against itself.
    """
    import test_pipeline as tp

    path = require(os.environ.get("DATASET_PATH", tp.DEFAULT_PATH),
                   "N-1 dataset; regenerate with feasibility/generate_dataset.py")
    return tp.build_context(path, tp.SEED)


@pytest.fixture(scope="session")
def d():
    """The committed M1 coverage-sweep curve, mirroring test_tradeoff.DEFAULT_PATH."""
    return load_curve(os.environ.get("TRADEOFF_PATH", CURVE_M1),
                      "M1 coverage sweep; regenerate with feasibility/tradeoff.py")


@pytest.fixture(scope="session")
def d_v2():
    """The promoted M2 coverage-sweep curve.

    Same three guards, different curve: the M2 sweep is what every reported number
    derives from, so it should not be the untested one.
    """
    return load_curve(os.environ.get("TRADEOFF_V2_PATH", CURVE_M2),
                      "M2 coverage sweep; built by scripts/build_v2_frozen.py")
