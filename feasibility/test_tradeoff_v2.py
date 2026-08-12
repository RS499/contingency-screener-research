"""The tradeoff guards, run against the PROMOTED M2 curve.

test_tradeoff.py runs its three guards against data/tradeoff_curve.json (M1). Every
reported number derives from the M2 curve, data/tradeoff_curve_v2.json, which no test
covered. This module re-runs the SAME three guard functions -- imported, not copied, so
the assertions cannot drift -- against the M2 curve via the d_v2 fixture.

Imported as a module alias on purpose: `from test_tradeoff import ...` would rebind those
test names here and make pytest collect the M1 guards a second time.
"""

import pytest

import test_tradeoff as tt

GUARD_IDS = [t.__name__.replace("test_", "") for t in tt.TESTS]


@pytest.mark.parametrize("guard", tt.TESTS, ids=GUARD_IDS)
def test_v2_curve_guard(guard, d_v2):
    """Run one committed tradeoff guard against the M2 curve."""
    guard(d_v2)
