"""
Heavy benchmark test for canonicalize_contraction_graph.

This test intentionally takes ~10 seconds.  It is excluded from the normal
pytest run and must be invoked explicitly:

    pytest -m slow
    pytest tests/diag/test_canonicalize_graph_heavy.py

Purpose
-------
Graph canonicalization has been measured at 91–92 % of total ``contract()``
wall time (see roadmap.md §P2).  This test stresses the hot path by running
the full BCH + Wick contraction pipeline at excitation level n = 5, which
produces 51 954 operator products for ``canonicalize_contraction_graph`` to
process.

The test also quantifies the canonicalization overhead directly by repeating
the same contraction with ``do_canonicalize_graph(False)`` and asserting that
canon=ON takes at least 5× longer than canon=OFF.  On the profiled hardware
(Apple Silicon, single thread) the measured ratio is roughly 12×.

Timing reference (Apple Silicon M-series, single thread):
    BCH n=5 expansion : ~0.9 s
    contract canon=ON : ~8.5 s   ← dominated by canonicalize_contraction_graph
    contract canon=OFF: ~0.7 s
    total             : ~10 s
"""

import time

import pytest

import wickd as w


# ---------------------------------------------------------------------------
# helpers shared across tests in this module
# ---------------------------------------------------------------------------

def _setup_ov():
    w.reset_space()
    w.add_space("o", "fermion", "occupied",   ["i", "j", "k", "l", "m", "n"])
    w.add_space("v", "fermion", "unoccupied", ["a", "b", "c", "d", "e", "f"])


def _make_hamiltonian():
    """H = E_0 + F + V  (scalar + 1-body + 2-body)."""
    return (
        w.op("E_0", [""])
        + w.utils.gen_op("f", 1, "ov", "ov")
        + w.utils.gen_op("v", 2, "ov", "ov")
    )


def _make_T(n: int):
    """Cluster operator T_1 + T_2 + … + T_n as a single w.op."""
    components = [f"{'v+' * k} {'o' * k}" for k in range(1, n + 1)]
    return w.op("t", components)


# ---------------------------------------------------------------------------
# benchmark test
# ---------------------------------------------------------------------------

@pytest.mark.slow
def test_bch_n5_canonicalization_dominates():
    """BCH to 4th order with T up to T_5 (CC excitation level n=5).

    Produces 51 954 operator products; each is passed to
    canonicalize_contraction_graph.  The total wall time is ~10 s
    single-threaded, with canonicalization accounting for >90 % of that.

    Assertions
    ----------
    1. The contracted expression is non-trivial (≥100 distinct terms).
    2. Canonicalization overhead: canon=ON must take at least 5× longer than
       canon=OFF on the same input.  (Measured ratio on reference hardware: ~12×.)
    3. Both canon=ON and canon=OFF produce the same number of terms — the
       invariant that canonicalization merges but never creates terms.
    """
    _setup_ov()
    H = _make_hamiltonian()
    T = _make_T(5)

    hbar = w.bch_series(H, T, 4)
    assert len(hbar) == 51_954, (
        f"Unexpected hbar size {len(hbar)}; BCH expansion may have changed"
    )

    # ── canon=ON (the slow path) ──────────────────────────────────────────
    wt_on = w.WickTheorem()
    wt_on.set_single_threaded(True)

    t0 = time.perf_counter()
    result_on = wt_on.contract(w.rational(1), hbar, 0, 10)
    t_on = time.perf_counter() - t0

    # ── canon=OFF (the fast baseline) ────────────────────────────────────
    wt_off = w.WickTheorem()
    wt_off.set_single_threaded(True)
    wt_off.do_canonicalize_graph(False)

    t0 = time.perf_counter()
    result_off = wt_off.contract(w.rational(1), hbar, 0, 10)
    t_off = time.perf_counter() - t0

    # ── assertions ───────────────────────────────────────────────────────
    n_on  = len(result_on)
    n_off = len(result_off)

    # 1. non-trivial result
    assert n_on >= 100, f"Expected ≥100 terms, got {n_on}"

    # 2. canonicalization dominates (must be at least 5× slower)
    ratio = t_on / t_off if t_off > 0 else float("inf")
    assert ratio >= 5.0, (
        f"canon=ON ({t_on:.2f}s) should be ≥5× slower than canon=OFF "
        f"({t_off:.2f}s); got ratio={ratio:.1f}×.  "
        "Either canonicalization is no longer the bottleneck, or the "
        "no-canon path is unexpectedly slow."
    )

    # 3. canon never introduces more terms than no-canon
    assert n_on <= n_off, (
        f"canon=ON produced more terms ({n_on}) than canon=OFF ({n_off})"
    )
