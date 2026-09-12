# Pauli-Z decomposition of the tilt cost Hamiltonian (6 antennas, 12 qubits)

`H_C = sum_S c_S Z_S`, obtained by a Walsh-Hadamard transform of the 4096-entry cost table and verified to reproduce every table entry to 1e-9.

Total terms: **73** (identity offset c_0 = 35.4992).

| weight | # terms | meaning |
|---|---|---|
| 0 | 1 | constant offset (global phase, dropped by the circuit) |
| 1 | 12 | single-qubit Z: linear terms (coverage gain, tilt energy penalty); 2 per antenna |
| 2 | 60 | Z Z: one qubit of antenna i x one qubit of antenna j, for each interfering pair (15 pairs x 4) |

The Hamiltonian is **2-local** (Ising / QUBO form): tilt_i is linear in its two qubits and the interference matrix has zero diagonal, so t_i t_j (i != j) only produces Z Z terms. No 3- or 4-body terms appear, which is what makes this encoding hardware-friendly. (Packing 27 configurations into 5 qubits would instead give terms up to Z Z Z Z Z.)

## Gate cost of one QAOA layer `exp(+i gamma H_C)`

Each weight-w term becomes a CX ladder onto its last qubit, one `RZ(-2 gamma c_S)`, and the ladder undone: 2(w-1) CX + 1 RZ (Classiq merges ladders that share a parity, so its synthesized count is lower).

Naive schedule: **72 RZ, 120 CX** per cost layer; mixer adds 12 RX. Classiq synthesized (transpiled): p=1 -> 72 RZ, 92 CX, depth 59; p=2 -> 144 RZ, 184 CX, depth 114.

## All terms (coefficient, qubits; antenna i owns qubits 2i, 2i+1)

| qubits | c_S |
|---|---|
| I | +35.49915 |
| [0] | -4.40190 |
| [1] | -8.80380 |
| [2] | -4.40895 |
| [3] | -8.81790 |
| [4] | -4.37220 |
| [5] | -8.74440 |
| [6] | -4.40985 |
| [7] | -8.81970 |
| [8] | -4.40985 |
| [9] | -8.81970 |
| [10] | -4.40985 |
| [11] | -8.81970 |
| [0, 2] | +0.67500 |
| [1, 2] | +1.35000 |
| [0, 3] | +1.35000 |
| [1, 3] | +2.70000 |
| [0, 4] | +0.67500 |
| [1, 4] | +1.35000 |
| [2, 4] | +0.67500 |
| [3, 4] | +1.35000 |
| [0, 5] | +1.35000 |
| [1, 5] | +2.70000 |
| [2, 5] | +1.35000 |
| [3, 5] | +2.70000 |
| [0, 6] | +0.09035 |
| [1, 6] | +0.18070 |
| [2, 6] | +0.09255 |
| [3, 6] | +0.18510 |
| [4, 6] | +0.08705 |
| [5, 6] | +0.17410 |
| [0, 7] | +0.18070 |
| [1, 7] | +0.36140 |
| [2, 7] | +0.18510 |
| [3, 7] | +0.37020 |
| [4, 7] | +0.17410 |
| [5, 7] | +0.34820 |
| [0, 8] | +0.09035 |
| [1, 8] | +0.18070 |
| [2, 8] | +0.09255 |
| [3, 8] | +0.18510 |
| [4, 8] | +0.08705 |
| [5, 8] | +0.17410 |
| [6, 8] | +0.67500 |
| [7, 8] | +1.35000 |
| [0, 9] | +0.18070 |
| [1, 9] | +0.36140 |
| [2, 9] | +0.18510 |
| [3, 9] | +0.37020 |
| [4, 9] | +0.17410 |
| [5, 9] | +0.34820 |
| [6, 9] | +1.35000 |
| [7, 9] | +2.70000 |
| [0, 10] | +0.09035 |
| [1, 10] | +0.18070 |
| [2, 10] | +0.09255 |
| [3, 10] | +0.18510 |
| [4, 10] | +0.08705 |
| [5, 10] | +0.17410 |
| [6, 10] | +0.67500 |
| [7, 10] | +1.35000 |
| [8, 10] | +0.67500 |
| [9, 10] | +1.35000 |
| [0, 11] | +0.18070 |
| [1, 11] | +0.36140 |
| [2, 11] | +0.18510 |
| [3, 11] | +0.37020 |
| [4, 11] | +0.17410 |
| [5, 11] | +0.34820 |
| [6, 11] | +1.35000 |
| [7, 11] | +2.70000 |
| [8, 11] | +1.35000 |
| [9, 11] | +2.70000 |
