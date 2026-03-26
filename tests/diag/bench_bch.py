"""
Benchmark for the BCH + Wick contraction pipeline at high excitation level.

Measures the wall-clock cost of the full bch_series → contract() path for
excitation levels n = 3 … 6, with canonicalization on and off.  Because
canonicalize_contraction_graph accounts for ~92 % of contract() runtime, the
ratio t_canon / t_nocanon directly quantifies the canonicalization overhead.

Usage
-----
Save a baseline (run before an optimization):
    python tests/diag/bench_bch.py --save

Compare against the baseline (run after an optimization):
    python tests/diag/bench_bch.py --compare

Just print timings without saving or comparing:
    python tests/diag/bench_bch.py

Select which excitation levels to run (default: 3 4; add 5 for a ~10 s run):
    python tests/diag/bench_bch.py --levels 4 5
"""

import argparse
import json
import time
from pathlib import Path

import wickd as w

BASELINE_FILE = Path(__file__).resolve().parent / "bench_bch_baseline.json"
REPS = 1  # BCH n=5 already takes ~10 s; one rep is sufficient


# ── setup ─────────────────────────────────────────────────────────────────────

def setup_ov():
    w.reset_space()
    w.add_space("o", "fermion", "occupied",   ["i", "j", "k", "l", "m", "n"])
    w.add_space("v", "fermion", "unoccupied", ["a", "b", "c", "d", "e", "f"])


def make_hamiltonian():
    """H = E_0 + F + V  (scalar + 1-body + 2-body)."""
    return (
        w.op("E_0", [""])
        + w.utils.gen_op("f", 1, "ov", "ov")
        + w.utils.gen_op("v", 2, "ov", "ov")
    )


def make_T(n):
    """Cluster operator T_1 + T_2 + … + T_n as a single w.op."""
    return w.op("t", [f"{'v+' * k} {'o' * k}" for k in range(1, n + 1)])


# ── timing helpers ────────────────────────────────────────────────────────────

def time_contract(hbar, maxrank: int, *, canon: bool) -> tuple[float, int]:
    """Return (min wall-time in seconds, output term count)."""
    best = float("inf")
    nterms = 0
    for _ in range(REPS):
        wt = w.WickTheorem()
        wt.set_single_threaded(True)
        if not canon:
            wt.do_canonicalize_graph(False)
        t0 = time.perf_counter()
        result = wt.contract(w.rational(1), hbar, 0, maxrank)
        elapsed = time.perf_counter() - t0
        best = min(best, elapsed)
        nterms = len(result)
    return best, nterms


# ── benchmark ─────────────────────────────────────────────────────────────────

def run_benchmark(levels):
    setup_ov()
    H = make_hamiltonian()

    results = {}
    header = (
        f"{'n':>3}  {'hbar ops':>9}  {'bch(s)':>8}  "
        f"{'canon(s)':>10}  {'nocanon(s)':>11}  {'ratio':>6}  {'terms':>6}"
    )
    print(header)
    print("-" * len(header))

    for n in levels:
        T = make_T(n)

        t0 = time.perf_counter()
        hbar = w.bch_series(H, T, 4)
        t_bch = time.perf_counter() - t0

        maxrank = 2 * n   # physical CC residuals (same range as test_cc.py)
        t_on,  nterms = time_contract(hbar, maxrank, canon=True)
        t_off, _      = time_contract(hbar, maxrank, canon=False)

        ratio = t_on / t_off if t_off > 0 else float("inf")
        key = f"n={n}"
        results[key] = {
            "hbar_size": len(hbar),
            "t_bch":     t_bch,
            "t_canon":   t_on,
            "t_nocanon": t_off,
            "terms":     nterms,
        }
        print(
            f"{n:>3}  {len(hbar):>9}  {t_bch:>8.2f}  "
            f"{t_on:>10.2f}  {t_off:>11.2f}  {ratio:>5.1f}x  {nterms:>6}"
        )

    return results


# ── comparison ────────────────────────────────────────────────────────────────

def compare(current: dict, baseline: dict, tol: float = 0.20):
    print(
        f"\n{'case':<8}  {'baseline(s)':>12}  {'current(s)':>11}  "
        f"{'ratio':>7}  {'status':>9}"
    )
    print("-" * 56)
    all_ok = True
    for key, cur in current.items():
        base = baseline.get(key)
        if base is None:
            print(f"  {key:<6}  {'(no baseline)':>12}")
            continue
        t_base = base["t_canon"]
        t_cur  = cur["t_canon"]
        ratio  = t_cur / t_base if t_base > 0 else float("inf")
        ok     = ratio <= (1.0 + tol)
        status = "OK" if ok else "REGRESSED"
        if not ok:
            all_ok = False
        print(
            f"  {key:<6}  {t_base:>12.2f}  {t_cur:>11.2f}  "
            f"{ratio:>7.2f}x  {status:>9}"
        )
    return all_ok


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--save",    action="store_true",
                        help="Save results as baseline")
    parser.add_argument("--compare", action="store_true",
                        help="Compare against baseline")
    parser.add_argument("--tol",     type=float, default=0.20,
                        help="Allowed slowdown fraction before REGRESSED (default 0.20)")
    parser.add_argument("--levels",  type=int, nargs="+", default=[3, 4],
                        metavar="N",
                        help="Excitation levels to benchmark (default: 3 4 5)")
    args = parser.parse_args()

    print(f"Running BCH benchmark for excitation levels: {args.levels}")
    print(f"({REPS} rep(s) per case; reporting minimum time)\n")

    results = run_benchmark(args.levels)

    if args.save:
        BASELINE_FILE.write_text(json.dumps(results, indent=2))
        print(f"\nBaseline saved to {BASELINE_FILE}")

    if args.compare:
        if not BASELINE_FILE.exists():
            print(f"\nNo baseline found at {BASELINE_FILE}. Run with --save first.")
            raise SystemExit(1)
        baseline = json.loads(BASELINE_FILE.read_text())
        print("\n=== Comparison vs baseline ===")
        ok = compare(results, baseline, tol=args.tol)
        if not ok:
            print("\nOne or more cases REGRESSED.")
            raise SystemExit(1)
        else:
            print("\nAll cases within tolerance.")


if __name__ == "__main__":
    main()
