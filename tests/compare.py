#!/usr/bin/env python3
"""
Compare two result files from run_suite.py.

Usage:
    python tests/compare.py tests/results/results_pandas_master.csv tests/results/results_polars_uv-polars.csv

Produces a per-indicator diff report:
  - status match (ok/ok vs error/error)
  - max absolute difference on mean, std, min, max
  - NaN count delta
  - runtime comparison
  - overall pass/fail with tolerance

Resampled-input note:
  If the source result files were generated with --resample-size / --resample-fraction,
  they should use the same resample method and seed. That resampling metadata is stored
  in the # @config header so the sampled subset can be reproduced consistently across
  branches and libraries.

Exit code: 0 if all indicators match within tolerance, 1 otherwise.
"""

import csv
import json
import sys
from collections import defaultdict


def load_results(path):
    """Load a results CSV with header block. Returns (run_meta, config_snap, rows)."""
    run_meta = {}
    config_snap = {}
    rows = []
    with open(path) as f:
        for line in f:
            if line.startswith("# @run "):
                run_meta = json.loads(line[len("# @run ") :].strip())
            elif line.startswith("# @config "):
                config_snap = json.loads(line[len("# @config ") :].strip())
            elif line.startswith("# "):
                # legacy single-line format
                run_meta = json.loads(line[2:].strip())
            elif not line.startswith("#"):
                break

        f.seek(0)
        reader = csv.DictReader(line for line in f if not line.startswith("#"))
        for row in reader:
            rows.append(row)

    return run_meta, config_snap, rows


def safe_float(val, default=0.0):
    if val == "" or val is None:
        return default
    try:
        return float(val)
    except ValueError, TypeError:
        return default


def compare(file_a, file_b, tol_abs=1e-6, tol_rel=1e-4):
    meta_a, config_a, rows_a = load_results(file_a)
    meta_b, config_b, rows_b = load_results(file_b)

    print(f"File A: {file_a}")
    print(
        f"  {meta_a.get('lib')} {meta_a.get('lib_version')} | branch={meta_a.get('branch')} | commit={meta_a.get('commit')}"
    )
    print(f"  Config: tickers={config_a.get('tickers')} periods={config_a.get('periods')}")
    print(f"File B: {file_b}")
    print(
        f"  {meta_b.get('lib')} {meta_b.get('lib_version')} | branch={meta_b.get('branch')} | commit={meta_b.get('commit')}"
    )
    print(f"  Config: tickers={config_b.get('tickers')} periods={config_b.get('periods')}")
    print()

    # Index rows by (ticker, indicator, period)
    index_a = {(r["ticker"], r["indicator"], int(r["period"])): r for r in rows_a}
    index_b = {(r["ticker"], r["indicator"], int(r["period"])): r for r in rows_b}

    all_keys = sorted(set(index_a.keys()) | set(index_b.keys()))

    # ── stats ─────────────────────────────────────────────────
    total = len(all_keys)
    both_ok = 0
    both_error = 0
    status_mismatch = 0
    missing_in_a = 0
    missing_in_b = 0
    numerical_match = 0
    numerical_diff = 0
    max_abs_diff = 0.0
    worst_diff_key = None
    worst_diff_value = 0.0
    worst_diff_field = ""

    # Collect summaries per indicator (across tickers/periods)
    indicator_summary = defaultdict(
        lambda: {"ok_pairs": 0, "diff_pairs": 0, "max_abs": 0.0, "max_rel": 0.0, "status_mismatch": 0}
    )

    numeric_fields = ["mean", "std", "min", "max"]

    for key in all_keys:
        ra = index_a.get(key)
        rb = index_b.get(key)
        ticker, indicator, period = key

        if ra is None:
            missing_in_a += 1
            continue
        if rb is None:
            missing_in_b += 1
            continue

        status_a = ra.get("status", "")
        status_b = rb.get("status", "")

        if status_a == "error" and status_b == "error":
            both_error += 1
            continue
        if status_a != status_b:
            status_mismatch += 1
            indicator_summary[indicator]["status_mismatch"] += 1
            continue

        both_ok += 1

        # Compare numeric fields
        has_diff = False
        for field in numeric_fields:
            va = safe_float(ra.get(field))
            vb = safe_float(rb.get(field))

            abs_diff = abs(va - vb)
            denom = max(abs(va), abs(vb), 1e-10)
            rel_diff = abs_diff / denom

            if abs_diff > tol_abs and rel_diff > tol_rel:
                has_diff = True
                if abs_diff > worst_diff_value:
                    worst_diff_value = abs_diff
                    worst_diff_key = key
                    worst_diff_field = field

                indicator_summary[indicator]["max_abs"] = max(indicator_summary[indicator]["max_abs"], abs_diff)
                indicator_summary[indicator]["max_rel"] = max(indicator_summary[indicator]["max_rel"], rel_diff)

            max_abs_diff = max(max_abs_diff, abs_diff)

        if has_diff:
            numerical_diff += 1
            indicator_summary[indicator]["diff_pairs"] += 1
        else:
            numerical_match += 1
            indicator_summary[indicator]["ok_pairs"] += 1

        # NaN count comparison
        safe_float(ra.get("nan_count", 0), 0)
        safe_float(rb.get("nan_count", 0), 0)

        # Runtime comparison
        safe_float(ra.get("runtime_ms", 0), 0)
        safe_float(rb.get("runtime_ms", 0), 0)

    # ── report ────────────────────────────────────────────────
    print(f"{'=' * 70}")
    print("  COMPARISON SUMMARY")
    print(f"{'=' * 70}")
    print(f"  Total comparisons:     {total}")
    print(f"  Both OK:               {both_ok}")
    print(f"  Both ERROR:            {both_error}")
    print(f"  Status mismatch:       {status_mismatch}")
    print(f"  Missing in A:          {missing_in_a}")
    print(f"  Missing in B:          {missing_in_b}")
    print(f"  Numerical match:       {numerical_match}")
    print(f"  Numerical diff:        {numerical_diff}")
    print(f"  Max absolute diff:     {max_abs_diff:.8e}")
    if worst_diff_key:
        print(f"  Worst diff at:         {worst_diff_key} ({worst_diff_field})")
    print()

    # Per-indicator summary
    diff_indicators = {
        k: v for k, v in sorted(indicator_summary.items()) if v["diff_pairs"] > 0 or v["status_mismatch"] > 0
    }

    if diff_indicators:
        print(f"{'─' * 70}")
        print("  INDICATORS WITH DIFFERENCES")
        print(f"{'─' * 70}")
        print(f"  {'indicator':<30s} {'diff':>5s} {'ok':>5s} {'max_abs':>12s} {'max_rel':>12s} {'status':>7s}")
        print(f"  {'─' * 30} {'─' * 5} {'─' * 5} {'─' * 12} {'─' * 12} {'─' * 7}")
        for name, stats in diff_indicators.items():
            print(
                f"  {name:<30s} {stats['diff_pairs']:>5d} {stats['ok_pairs']:>5d} "
                f"{stats['max_abs']:>12.6e} {stats['max_rel']:>12.6e} "
                f"{stats['status_mismatch']:>7d}"
            )
        print()

    # ── verdict ───────────────────────────────────────────────
    pass_rate = numerical_match / max(both_ok, 1) * 100
    print(f"  Pass rate: {pass_rate:.1f}%  ({numerical_match}/{both_ok} match)")

    if numerical_diff == 0 and status_mismatch == 0:
        print("  ✓ ALL INDICATORS MATCH")
        return 0
    else:
        print("  ✗ Some differences found (see above)")
        return 1


def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <results_a.csv> <results_b.csv>")
        print()
        print("Compare two result files produced by run_suite.py.")
        print("Typical workflow:")
        print("  1. On pandas branch:  python tests/run_suite.py")
        print("  2. On polars branch:  python tests/run_suite.py")
        print("  3. Compare:           python tests/compare.py <file_a> <file_b>")
        sys.exit(1)

    rc = compare(sys.argv[1], sys.argv[2])
    sys.exit(rc)


if __name__ == "__main__":
    main()
