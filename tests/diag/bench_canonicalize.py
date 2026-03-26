"""
Benchmark for canonicalize_contraction_graph.

Measures the wall-clock cost of canonicalization across a representative set
of operator products, in three orbital-space configurations.

Usage
-----
Save a baseline (run before an optimization):
    python tests/diag/bench_canonicalize.py --save

Compare against the baseline (run after an optimization):
    python tests/diag/bench_canonicalize.py --compare

Just print timings without saving or comparing:
    python tests/diag/bench_canonicalize.py
"""

import argparse
import json
import time
from pathlib import Path

import wickd as w

BASELINE_FILE = Path(__file__).resolve().parent / "bench_canonicalize_baseline.json"
REPS = 3  # repetitions per case; result is the minimum


# ── orbital-space setup ───────────────────────────────────────────────────────

def setup_ov():
    w.reset_space()
    w.add_space("o", "fermion", "occupied",   ["i", "j", "k", "l", "m", "n"])
    w.add_space("v", "fermion", "unoccupied", ["a", "b", "c", "d", "e", "f"])


def setup_cav():
    w.reset_space()
    w.add_space("c", "fermion", "occupied",   ["i", "j", "k", "l", "m", "n"])
    w.add_space("a", "fermion", "general",    ["u", "v", "w", "x", "y", "z"])
    w.add_space("v", "fermion", "unoccupied", ["a", "b", "c", "d", "e", "f"])


def setup_cabv():
    w.reset_space()
    w.add_space("c", "fermion", "occupied",   ["i", "j", "k", "l", "m", "n"])
    w.add_space("a", "fermion", "general",    ["u", "v", "w", "x", "y", "z"])
    w.add_space("b", "fermion", "general",    ["p", "q", "r", "s", "t", "U"])
    w.add_space("v", "fermion", "unoccupied", ["a", "b", "c", "d", "e", "f"])


# ── benchmark cases ───────────────────────────────────────────────────────────

def build_cases():
    cases = []   # list of (config_name, case_label, operator_expr)

    # ── o/v ──────────────────────────────────────────────────────────────────
    setup_ov()
    F  = w.utils.gen_op("f", 1, "ov", "ov")
    V  = w.utils.gen_op("v", 2, "ov", "ov")
    W  = w.utils.gen_op("w", 3, "ov", "ov")
    T1 = w.op("t", ["v+ o"])
    T2 = w.op("t", ["v+ v+ o o"])
    T3 = w.op("t", ["v+ v+ v+ o o o"])
    T4 = w.op("t", ["v+ v+ v+ v+ o o o o"])
    for label, expr in [
        ("F@T4",        F@T4),
        ("V@T4",        V@T4),
        ("W@T4",        W@T4),
        ("V@T3@T3",     V@T3@T3),
        ("V@T4@T4",     V@T4@T4),
        ("V@T4@T1",     V@T4@T1),
        ("V@T4@T2",     V@T4@T2),
        ("W@T4@T1",     W@T4@T1),
        ("V@T3@T3@T1",  V@T3@T3@T1),
        ("V@T4@T1@T1",  V@T4@T1@T1),
        ("V@T4@T2@T1",  V@T4@T2@T1),
    ]:
        cases.append(("o/v", label, expr))

    # ── c/a/v ────────────────────────────────────────────────────────────────
    setup_cav()
    Fca  = w.utils.gen_op("f", 1, "ca",  "ca")
    Vca  = w.utils.gen_op("v", 2, "ca",  "ca")
    T1m  = w.utils.gen_op("t", 1, "av",  "ca", diagonal=False)
    T2m  = w.utils.gen_op("t", 2, "av",  "ca", diagonal=False)
    T4m  = w.utils.gen_op("t", 4, "av",  "ca", diagonal=False)
    v_caav    = w.op("v", ["v+ a+ c a"])
    t2_ccav   = w.op("t", ["v+ a+ c c"])
    t4_ccaavv = w.op("t", ["v+ v+ a+ a+ c c a a"])
    for label, expr in [
        ("Fca@T1",                              Fca@T1m),
        ("Fca@T2",                              Fca@T2m),
        ("Fca@T4",                              Fca@T4m),
        ("Vca@T1@T1",                           Vca@T1m@T1m),
        ("Vca@T2@T1",                           Vca@T2m@T1m),
        ("Vca@T4",                              Vca@T4m),
        ("v_caav@t2_ccav@t2_ccav",              v_caav@t2_ccav@t2_ccav),
        ("v_caav@t4_ccaavv@t2_ccav",            v_caav@t4_ccaavv@t2_ccav),
        ("v_caav@t4_ccaavv@t2_ccav@t2_ccav",    v_caav@t4_ccaavv@t2_ccav@t2_ccav),
    ]:
        cases.append(("c/a/v", label, expr))

    # ── c/a/b/v ──────────────────────────────────────────────────────────────
    setup_cabv()
    v4_cabv  = w.op("v", ["v+ b+ c a"])
    v4_ccab  = w.op("v", ["a+ b+ c c"])
    t2_4a    = w.op("t", ["v+ a+ c c"])
    t2_4b    = w.op("t", ["v+ b+ c c"])
    t3_4a    = w.op("t", ["v+ v+ a+ c c c"])
    t4_4ab   = w.op("t", ["v+ v+ a+ b+ c c a b"])
    t4_4mix  = w.op("t", ["v+ v+ v+ a+ c c c c"])
    for label, expr in [
        ("v4_cabv@t2_4a@t2_4b",       v4_cabv@t2_4a@t2_4b),
        ("v4_ccab@t4_4ab@t2_4a",      v4_ccab@t4_4ab@t2_4a),
        ("v4_cabv@t4_4mix@t2_4a",     v4_cabv@t4_4mix@t2_4a),
        ("v4_ccab@t3_4a@t3_4a",       v4_ccab@t3_4a@t3_4a),
        ("v4_cabv@t4_4ab@t2_4a@t2_4b",v4_cabv@t4_4ab@t2_4a@t2_4b),
    ]:
        cases.append(("c/a/b/v", label, expr))

    return cases


# ── timing helper ─────────────────────────────────────────────────────────────

def time_one(expr, *, canon: bool) -> tuple[float, int]:
    """Return (min wall-time in seconds, term count)."""
    best = float("inf")
    nterms = 0
    for _ in range(REPS):
        wt = w.WickTheorem()
        wt.set_single_threaded(True)
        if not canon:
            wt.do_canonicalize_graph(False)
        t0 = time.perf_counter()
        result = wt.contract(w.rational(1), expr, 0, 999)
        elapsed = time.perf_counter() - t0
        best = min(best, elapsed)
        nterms = len(result)
    return best, nterms


# ── main ─────────────────────────────────────────────────────────────────────

def run_benchmark(cases):
    results = {}
    header = f"{'config':>8}  {'case':<42}  {'canon(s)':>10}  {'no-canon(s)':>12}  {'canon%':>7}  {'terms':>6}"
    print(header)
    print("-" * len(header))
    for config, label, expr in cases:
        t_on,  n_on  = time_one(expr, canon=True)
        t_off, _     = time_one(expr, canon=False)
        pct = 100.0 * (t_on - t_off) / t_on if t_on > 0 else 0.0
        key = f"{config}::{label}"
        results[key] = {"t_canon": t_on, "t_nocanon": t_off, "terms": n_on}
        print(f"{config:>8}  {label:<42}  {t_on:>10.4f}  {t_off:>12.4f}  {pct:>6.1f}%  {n_on:>6}")
    return results


def compare(current: dict, baseline: dict, tol: float = 0.20):
    print(f"\n{'case':<52}  {'baseline(s)':>12}  {'current(s)':>11}  {'ratio':>7}  {'status':>8}")
    print("-" * 100)
    all_ok = True
    for key, cur in current.items():
        base = baseline.get(key)
        if base is None:
            print(f"  {key:<50}  {'(no baseline)':>12}")
            continue
        t_base = base["t_canon"]
        t_cur  = cur["t_canon"]
        ratio  = t_cur / t_base if t_base > 0 else float("inf")
        ok     = ratio <= (1.0 + tol)
        status = "OK" if ok else "REGRESSED"
        if not ok:
            all_ok = False
        print(f"  {key:<50}  {t_base:>12.4f}  {t_cur:>11.4f}  {ratio:>7.2f}x  {status:>8}")
    return all_ok


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save",    action="store_true", help="Save results as baseline")
    parser.add_argument("--compare", action="store_true", help="Compare against baseline")
    parser.add_argument("--tol",     type=float, default=0.20,
                        help="Allowed slowdown fraction before REGRESSED (default 0.20)")
    args = parser.parse_args()

    print("Building operator cases...")
    cases = build_cases()

    print(f"\nRunning {len(cases)} cases × {REPS} reps each...\n")
    results = run_benchmark(cases)

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
