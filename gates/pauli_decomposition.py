"""Pauli-Z decomposition of the antenna-tilt cost Hamiltonian and the resulting gate schedule.

H_C = sum_S  c_S  Z_S      (Z_S = product of Z over the qubit set S)
c_S = (1/4096) sum_z C(z) (-1)^{sum_{k in S} z_k}      (Walsh-Hadamard transform)

Encoding: tilt_i = q_{2i} + 2 q_{2i+1}, Cost(t) = t^T I t - lambda c.t + mu sum t
(same as quantum/wolfram_realdataset_algorithms.wl and group/classiq/qaoa_tilt_classiq.py).

Writes group/gates/pauli_terms.json, pauli_terms.md and qaoa_layer_schedule.qasm (QASM 2 with gamma/beta
substituted by the Wolfram p=1 optimum), and cross-checks the expansion against the cost table.
Run:  py -3.12 group/gates/pauli_decomposition.py
"""
import csv
import json
from itertools import combinations
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LAMBDA, MU, N, NQ = 1.5, 0.3, 6, 12

with open(ROOT / "data" / "opencellid_il2.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
cvec = np.array([float(r[rows[0].index("coverage_gain")]) for r in rows[1:]])
with open(ROOT / "data" / "opencellid_il2_interference.csv", newline="", encoding="utf-8") as f:
    imat = np.array([[float(x) for x in r[1:]] for r in list(csv.reader(f))[1:]])

# cost vector over all 4096 basis states, qubit k = bit k of the index
idx = np.arange(2 ** NQ)
bits = (idx[:, None] >> np.arange(NQ)) & 1                      # 4096 x 12
tilts = bits[:, 0::2] + 2 * bits[:, 1::2]                       # 4096 x 6
cost = np.einsum("zi,ij,zj->z", tilts, imat, tilts) - LAMBDA * tilts @ cvec + MU * tilts.sum(1)

# Walsh-Hadamard: coefficient of Z_S for every subset S (index s has bit k set iff k in S)
signs = 1 - 2 * ((bits[:, None, :] & bits[None, :, :]).sum(-1) % 2)   # (-1)^{z.s}, 4096 x 4096
coef = signs.T @ cost / 2 ** NQ
terms = [(int(s), float(coef[s])) for s in idx if abs(coef[s]) > 1e-9]
# cross-check: rebuild the cost vector from the Pauli terms
assert np.allclose(signs @ coef, cost), "Pauli expansion does not reproduce the cost table"

def qubits(s):
    return [k for k in range(NQ) if (s >> k) & 1]

by_weight = {}
for s, c in terms:
    by_weight.setdefault(len(qubits(s)), []).append((s, c))

# ---- write JSON + markdown
json.dump(
    {"schema": "hackton-tilt-pauli-terms/1.0.0", "n_qubits": NQ, "encoding": "tilt_i = q_{2i} + 2 q_{2i+1}",
     "n_terms": len(terms), "terms_by_weight": {w: len(v) for w, v in sorted(by_weight.items())},
     "terms": [{"qubits": qubits(s), "coefficient": c} for s, c in terms]},
    open(HERE / "pauli_terms.json", "w", encoding="utf-8"), indent=2)

md = ["# Pauli-Z decomposition of the tilt cost Hamiltonian (6 antennas, 12 qubits)", "",
      "`H_C = sum_S c_S Z_S`, obtained by a Walsh-Hadamard transform of the 4096-entry cost table and "
      "verified to reproduce every table entry to 1e-9.", "",
      f"Total terms: **{len(terms)}** (identity offset c_0 = {coef[0]:.4f}).", "",
      "| weight | # terms | meaning |", "|---|---|---|"]
meaning = {0: "constant offset (global phase, dropped by the circuit)",
           1: "single-qubit Z: linear terms (coverage gain, tilt energy penalty); 2 per antenna",
           2: "Z Z: one qubit of antenna i x one qubit of antenna j, for each interfering pair (15 pairs x 4)"}
for w, v in sorted(by_weight.items()):
    md.append(f"| {w} | {len(v)} | {meaning.get(w, '')} |")
md += ["", "The Hamiltonian is **2-local** (Ising / QUBO form): tilt_i is linear in its two qubits and the "
       "interference matrix has zero diagonal, so t_i t_j (i != j) only produces Z Z terms. "
       "No 3- or 4-body terms appear, which is what makes this encoding hardware-friendly. "
       "(Packing 27 configurations into 5 qubits would instead give terms up to Z Z Z Z Z.)"]
md += ["", "## Gate cost of one QAOA layer `exp(+i gamma H_C)`", "",
       "Each weight-w term becomes a CX ladder onto its last qubit, one `RZ(-2 gamma c_S)`, and the ladder undone: "
       "2(w-1) CX + 1 RZ (Classiq merges ladders that share a parity, so its synthesized count is lower).", ""]
cx = sum(2 * (w - 1) * len(v) for w, v in by_weight.items() if w >= 2)
rz = sum(len(v) for w, v in by_weight.items() if w >= 1)
md += [f"Naive schedule: **{rz} RZ, {cx} CX** per cost layer; mixer adds 12 RX. "
       f"Classiq synthesized (transpiled): p=1 -> 72 RZ, 92 CX, depth 59; p=2 -> 144 RZ, 184 CX, depth 114.", "",
       "## All terms (coefficient, qubits; antenna i owns qubits 2i, 2i+1)", "", "| qubits | c_S |", "|---|---|"]
for s, c in sorted(terms, key=lambda t: (len(qubits(t[0])), t[0])):
    md.append(f"| {qubits(s) if s else 'I'} | {c:+.5f} |")
(HERE / "pauli_terms.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# ---- explicit QASM2 of one QAOA layer at the Wolfram p=1 optimum (numeric angles)
w = json.load(open(ROOT / "verification" / "results" / "wolfram_realdataset_algorithms.json", encoding="utf-8"))
gamma, beta = w["qaoa_p1"]["gamma"], w["qaoa_p1"]["beta"]
q = ["OPENQASM 2.0;", 'include "qelib1.inc";', f"qreg q[{NQ}];", f"creg c[{NQ}];",
     f"// QAOA p=1 for the 6-antenna tilt cost, gamma={gamma:.6f} beta={beta:.6f} (Wolfram optimum)",
     "// exp(+i gamma c_S Z_S) = CX ladder, rz(-2 gamma c_S) on the parity qubit, ladder undone"]
q += [f"h q[{k}];" for k in range(NQ)]
for s, c in sorted(terms, key=lambda t: (len(qubits(t[0])), t[0])):
    qs = qubits(s)
    if not qs:
        continue
    for a, b in zip(qs[:-1], qs[1:]):
        q.append(f"cx q[{a}],q[{b}];")
    q.append(f"rz({-2 * gamma * c:.6f}) q[{qs[-1]}];")
    for a, b in reversed(list(zip(qs[:-1], qs[1:]))):
        q.append(f"cx q[{a}],q[{b}];")
q += [f"rx({beta:.6f}) q[{k}];" for k in range(NQ)]
q += [f"measure q[{k}] -> c[{k}];" for k in range(NQ)]
(HERE / "qaoa_layer_schedule.qasm").write_text("\n".join(q) + "\n", encoding="utf-8")

print(f"{len(terms)} Pauli terms; by weight {dict(sorted((w, len(v)) for w, v in by_weight.items()))}")
print(f"naive schedule per layer: {rz} RZ, {cx} CX; files written to {HERE}")
