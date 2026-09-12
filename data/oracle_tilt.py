"""Tilt oracle: brute-force optimum + greedy baseline for any instance
emitted by data/opencellid_pipeline.py (linear CSV + interference CSV).

Objective (docs/antenna_tilt_problem.md, minimize):
    Cost(t) = sum_ij I[i][j] * t_i * t_j  -  LAMBDA * sum_i c[i] * t_i
              + MU * sum_i t_i
with tilt levels t_i in {0..tilt_levels-1}.

Mirrors dispatch/oracle_dispatch.py conventions.
Run:
  py -3.12 data/oracle_tilt.py [--prefix data/opencellid_demo] [--lambda 1.5] [--mu 0.3] [--json-out PATH]
"""
import argparse
import csv
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load(prefix):
    prefix = Path(prefix) if Path(prefix).is_absolute() else HERE / prefix
    lin_path, int_path = Path(f"{prefix}.csv"), Path(f"{prefix}_interference.csv")
    with open(lin_path, encoding="utf-8", newline="") as f:
        antennas = list(csv.DictReader(f))
    with open(int_path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    n = len(antennas)
    I = [[float(rows[i + 1][j + 1]) for j in range(n)] for i in range(n)]
    c = [float(a["coverage_gain"]) for a in antennas]
    levels = int(antennas[0]["tilt_levels"])
    return I, c, levels


def cost(t, I, c, lam, mu):
    n = len(c)
    quad = sum(I[i][j] * t[i] * t[j] for i in range(n) for j in range(n))
    return quad - lam * sum(c[i] * t[i] for i in range(n)) + mu * sum(t)


def brute_force(I, c, levels, lam, mu):
    best, best_cost = None, float("inf")
    for t in itertools.product(range(levels), repeat=len(c)):
        cc = cost(t, I, c, lam, mu)
        if cc < best_cost:
            best, best_cost = t, cc
    return best, best_cost


def greedy(I, c, levels, lam, mu):
    """Coordinate-descent baseline: start at zero, improve one antenna at a time."""
    t = [0] * len(c)
    improved = True
    while improved:
        improved = False
        for i in range(len(c)):
            cur = cost(t, I, c, lam, mu)
            for lvl in range(levels):
                trial = list(t)
                trial[i] = lvl
                cc = cost(trial, I, c, lam, mu)
                if cc < cur - 1e-12:
                    t, cur, improved = trial, cc, True
    return t, cost(t, I, c, lam, mu)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", default="opencellid_demo",
                    help="instance prefix under data/ (or absolute), e.g. opencellid_demo")
    ap.add_argument("--lambda", dest="lam", type=float, default=1.5)
    ap.add_argument("--mu", type=float, default=0.3)
    ap.add_argument("--levels", type=int, default=None,
                    help="override tilt levels for brute force (coarse check on big instances)")
    ap.add_argument("--greedy-only", action="store_true",
                    help="skip brute force (instances whose search space is intractable)")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args()

    I, c, levels = load(args.prefix)
    if args.levels:
        levels = args.levels
    n = len(c)
    print(f"Instance: {n} antennas x {levels} tilt levels "
          f"({levels ** n} assignments)")
    if args.greedy_only:
        best, best_cost = None, None
        print("ORACLE  skipped (--greedy-only: search space intractable by enumeration)")
    else:
        best, best_cost = brute_force(I, c, levels, args.lam, args.mu)
        print(f"ORACLE  optimum: tilts={best}  cost={best_cost:.4f}")
    g, g_cost = greedy(I, c, levels, args.lam, args.mu)
    if best_cost is not None:
        gap = (g_cost - best_cost) / abs(best_cost) * 100 if best_cost else 0.0
        print(f"GREEDY  tilts={tuple(g)}  cost={g_cost:.4f}  (gap {gap:.2f}%)")
    else:
        gap = None
        print(f"GREEDY  tilts={tuple(g)}  cost={g_cost:.4f}")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps({
            "instance": str(args.prefix), "n_antennas": n, "tilt_levels": levels,
            "lambda": args.lam, "mu": args.mu, "search_space": levels ** n,
            "optimum_tilts": list(best) if best else None,
            "optimum_cost": best_cost,
            "greedy_tilts": g, "greedy_cost": g_cost, "greedy_gap_pct": gap,
        }, indent=2), encoding="utf-8")
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()
