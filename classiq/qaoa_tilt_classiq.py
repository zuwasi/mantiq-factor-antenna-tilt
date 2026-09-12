"""QAOA antenna-tilt on Classiq: 6 real antennas (opencellid_il2), 2 qubits per antenna.

Same model as quantum/wolfram_realdataset_algorithms.wl:
    tilt_i in {0,1,2,3} encoded as QNum[2]  (12 qubits total)
    Cost(t) = t^T I t - lambda * c.t + mu * sum(t)
    phase layer  = phase(Cost, gamma)      (Classiq convention exp(+i gamma C))
    mixer layer  = RX(beta) on every qubit
Warm-start angles come from the Wolfram statevector optimization
(verification/results/wolfram_realdataset_algorithms.json).

Run (from any cwd):
    py -3.12 group/classiq/qaoa_tilt_classiq.py --layers 2 --shots 4096
    py -3.12 group/classiq/qaoa_tilt_classiq.py --layers 2 --optimize 20     # short COBYLA refine
    py -3.12 group/classiq/qaoa_tilt_classiq.py --layers 1 --backend ionq_simulator
Outputs go to group/classiq/results/.
"""
import argparse
import csv
import json
import time
from pathlib import Path

import numpy as np
from classiq import *  # noqa: F403

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
OUT = Path(__file__).resolve().parent / "results"
WOLFRAM = ROOT / "verification" / "results" / "wolfram_realdataset_algorithms.json"

LAMBDA, MU = 1.5, 0.3
N_ANT, LEVELS = 6, 4
NUM_LAYERS = 1  # overwritten from --layers before synthesis


# ---------------------------------------------------------------- instance
def load_instance():
    with open(DATA / "opencellid_il2.csv", newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    cix = rows[0].index("coverage_gain")
    cvec = np.array([float(r[cix]) for r in rows[1:]])
    with open(DATA / "opencellid_il2_interference.csv", newline="", encoding="utf-8") as f:
        irows = list(csv.reader(f))
    imat = np.array([[float(x) for x in r[1:]] for r in irows[1:]])
    assert cvec.shape == (N_ANT,) and imat.shape == (N_ANT, N_ANT)
    return cvec, imat


CVEC, IMAT = load_instance()


def cost_of(t):
    t = np.asarray(t, dtype=float)
    return float(t @ IMAT @ t - LAMBDA * (CVEC @ t) + MU * t.sum())


def full_table():
    """all 4^6 = 4096 configurations, in Wolfram basis order (antenna 0 = low bits)."""
    tab = {}
    for idx in range(LEVELS ** N_ANT):
        t = tuple((idx >> (2 * k)) & 3 for k in range(N_ANT))
        tab[t] = cost_of(t)
    return tab


TABLE = full_table()
OPT_T = min(TABLE, key=TABLE.get)
OPT_C = TABLE[OPT_T]


# ---------------------------------------------------------------- Qmod model
class TiltVars(QStruct):
    tilts: QArray[QNum[2], N_ANT]


def tilt_cost(t: TiltVars):
    expr = 0
    for i in range(N_ANT):
        for j in range(N_ANT):
            if IMAT[i, j] != 0.0:
                expr += float(IMAT[i, j]) * t.tilts[i] * t.tilts[j]
        expr += (MU - LAMBDA * float(CVEC[i])) * t.tilts[i]
    return expr


def build_main(num_layers):
    @qfunc
    def main(params: CArray[CReal, 2 * num_layers], t: Output[TiltVars]) -> None:
        allocate(t)
        hadamard_transform(t)
        repeat(
            count=num_layers,
            iteration=lambda i: (
                phase(tilt_cost(t), params[2 * i]),
                apply_to_all(lambda q: RX(params[2 * i + 1], q), t),
            ),
        )

    return main


# ---------------------------------------------------------------- helpers
def warm_start(num_layers):
    w = json.loads(WOLFRAM.read_text(encoding="utf-8"))
    if num_layers == 1:
        return [w["qaoa_p1"]["gamma"], w["qaoa_p1"]["beta"]], w["qaoa_p1"]
    if num_layers == 2:
        return list(w["qaoa_p2"]["params"]), w["qaoa_p2"]
    p, _ = warm_start(2)
    return p + [0.0, 0.0] * (num_layers - 2), None


def summarize(parsed_counts):
    total = sum(pc.shots for pc in parsed_counts)
    rows = []
    for pc in parsed_counts:
        t = tuple(int(x) for x in pc.state["t"]["tilts"])
        rows.append((t, pc.shots, TABLE[t]))
    rows.sort(key=lambda r: -r[1])
    exp_cost = sum(s * c for _, s, c in rows) / total
    p_neg = sum(s for _, s, c in rows if c < 0) / total
    p_opt = sum(s for t, s, _ in rows if t == OPT_T) / total
    best = min(rows, key=lambda r: r[2])
    return dict(total=total, expected_cost=exp_cost, p_cost_negative=p_neg,
                p_optimum=p_opt, best_sampled_tilts=list(best[0]),
                best_sampled_cost=best[2], rows=rows)


def gate_stats(qprog):
    """width / depth / gate counts of the transpiled circuit, plus its QASM."""
    m = get_transpiled_circuit_metrics(qprog)
    st = {"width": m.width, "depth": m.depth, "count_ops": dict(m.count_ops)}
    # parametric (gamma/beta symbolic) programs can only be exported as QASM3
    qasm = export(qprog, TargetLanguage.QASM3, transpilation_config=True)
    return st, qasm


# ---------------------------------------------------------------- main
def main_run():
    global NUM_LAYERS
    ap = argparse.ArgumentParser()
    ap.add_argument("--layers", type=int, default=2)
    ap.add_argument("--shots", type=int, default=4096)
    ap.add_argument("--backend", default=None, help="e.g. ionq_simulator; default Classiq simulator")
    ap.add_argument("--optimize", type=int, default=0, help="COBYLA iterations from the warm start (0 = sample only)")
    ap.add_argument("--show", action="store_true", help="open the circuit in the Classiq IDE (for screenshots)")
    ap.add_argument("--start", default=None, help="comma-separated start angles (overrides the Wolfram warm start)")
    ap.add_argument("--rhobeg", type=float, default=0.02, help="COBYLA initial step")
    ap.add_argument("--tag", default=None, help="suffix for the output file names")
    args = ap.parse_args()
    NUM_LAYERS = args.layers
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"p{args.layers}_{args.backend or 'classiq_simulator'}" + (f"_{args.tag}" if args.tag else "")

    print(f"instance: {N_ANT} antennas, {2 * N_ANT} qubits, {len(TABLE)} configurations")
    print(f"classical optimum: cost {OPT_C:.4f} at tilts {list(OPT_T)}")

    params, wolfram = warm_start(args.layers)
    if args.start:
        params = [float(x) for x in args.start.split(",")]
        assert len(params) == 2 * args.layers
        print(f"start angles (user): {[round(p, 5) for p in params]}")
    else:
        print(f"warm-start angles (Wolfram): {[round(p, 5) for p in params]}")
    if wolfram:
        print(f"  Wolfram prediction: <C> = {wolfram['expected_cost']:.4f}, P(opt) = {wolfram['p_optimum']:.4f}")

    t0 = time.time()
    qprog = synthesize(build_main(args.layers))
    print(f"synthesis OK ({time.time() - t0:.1f} s)")
    stats, qasm = gate_stats(qprog)
    print("circuit:", {k: v for k, v in stats.items() if k != "count_ops"}, "gates:", stats.get("count_ops"))
    (OUT / f"qaoa_tilt_{tag}.qasm").write_text(qasm or "", encoding="utf-8")
    qprog.save(OUT / f"qaoa_tilt_{tag}.qprog") if hasattr(qprog, "save") else None
    if args.show:
        show(qprog)

    ep = ExecutionPreferences(num_shots=args.shots, **({"backend_name": args.backend} if args.backend else {}))
    es = ExecutionSession(qprog, execution_preferences=ep)
    trace = []

    def run(p):
        t1 = time.time()
        res = es.sample({"params": [float(x) for x in p]})
        s = summarize(res.parsed_counts)
        s["params"] = [float(x) for x in p]
        s["seconds"] = time.time() - t1
        return s

    s0 = run(params)
    trace.append({k: v for k, v in s0.items() if k != "rows"})
    print(f"\nsampled at warm start ({s0['seconds']:.1f} s): <C> = {s0['expected_cost']:.4f}, "
          f"P(cost<0) = {s0['p_cost_negative']:.3f}, P(opt) = {s0['p_optimum']:.4f}, "
          f"best sampled {s0['best_sampled_tilts']} cost {s0['best_sampled_cost']:.4f}")

    final = s0
    if args.optimize > 0:
        from scipy.optimize import minimize

        def obj(p):
            s = run(p)
            trace.append({k: v for k, v in s.items() if k != "rows"})
            print(f"  iter {len(trace) - 1:3d}: <C> = {s['expected_cost']:.4f}  P(opt) = {s['p_optimum']:.4f}")
            return s["expected_cost"]

        r = minimize(obj, np.array(params), method="COBYLA",
                     options={"maxiter": args.optimize, "rhobeg": args.rhobeg})
        final = run(r.x)
        trace.append({k: v for k, v in final.items() if k != "rows"})
        print(f"after {args.optimize} COBYLA iterations: <C> = {final['expected_cost']:.4f}, "
              f"P(opt) = {final['p_optimum']:.4f}, params {[round(float(x), 5) for x in r.x]}")
    es.close()

    print("\ntop 10 sampled configurations:")
    for t, sh, c in final["rows"][:10]:
        flag = "  <-- optimum" if t == OPT_T else ""
        print(f"  tilts={list(t)}  shots={sh:5d}  cost={c:8.4f}{flag}")

    payload = {
        "schema": "hackton-tilt-qaoa-classiq/1.0.0",
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "backend": args.backend or "classiq_simulator",
        "instance": "opencellid_il2 (6 antennas, 12 qubits, 2 qubits/antenna)",
        "layers": args.layers, "shots": args.shots,
        "lambda": LAMBDA, "mu": MU,
        "classical_optimum_cost": OPT_C, "classical_optimum_tilts": list(OPT_T),
        "warm_start_params": params, "wolfram_prediction": wolfram,
        "circuit": {k: v for k, v in stats.items()},
        "final": {k: v for k, v in final.items() if k != "rows"},
        "counts": {",".join(map(str, t)): sh for t, sh, _ in final["rows"]},
        "trace": trace,
    }
    out = OUT / f"qaoa_tilt_{tag}.json"
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"\nwritten: {out}")


if __name__ == "__main__":
    main_run()
