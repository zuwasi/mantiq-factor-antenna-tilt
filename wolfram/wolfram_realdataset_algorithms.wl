(* ============================================================
   Quantum optimization algorithms for antenna tilt cost
   - real dataset: data/opencellid_il2 (6 antennas, OpenCelliD MCC 425)
   - coarse encoding: 2 qubits/antenna (4 tilt levels) = 12 qubits
   - objective: Cost(t) = t^T I t - lambda c^T t + mu sum(t)
   Algorithms demonstrated:
     1. QAOA p=1 (optimized gamma, beta)
     2. QAOA p=2 (grid refinement around the p=1 optimum)
     3. VQE (hardware-efficient RY+CZ ansatz, Nelder-Mead)
     4. Grover adaptive search (Durr-Hoyer) on a 2-antenna slice
   All cross-checked against exact classical enumeration.
   Conventions follow the verified quantum/wolfram_qaoa_sim.wl:
     basis index i, bit k of i = qubit k, tilt_i = q_{2i} + 2 q_{2i+1};
     phase layer = exp(+I gamma C) (Classiq `phase` convention).
   Implementation: plain 4096-dim statevector algebra (same engine as the
   verified QF cross-check, without per-eval QuantumOperator construction).
   ============================================================ *)

dir   = "C:\\Projects\\Hackton\\data\\";
outJS = "C:\\Projects\\Hackton\\verification\\results\\wolfram_realdataset_algorithms.json";
lambda = 1.5; mu = 0.3;

(* ---- load the REAL instance ---- *)
lin = Import[dir <> "opencellid_il2.csv", "CSV"];
head = First[lin]; rows = Rest[lin];
cix = First @ First @ Position[head, "coverage_gain"];
n = Length[rows];
cvec = N[rows[[All, cix]]];
int = Import[dir <> "opencellid_il2_interference.csv", "CSV"];
(* Mathematica may auto-detect the label row as a header; drop it if non-numeric *)
intData = If[NumericQ[int[[1, 2]]], int, Rest[int]];
imat = N[intData[[All, 2 ;;]]];
If[Length[cvec] != Length[imat], Print["dimension mismatch"]; Exit[1]];
levels = 4; nQ = 2 n; dim = 2^nQ;
Print["instance: ", n, " antennas, ", nQ, " qubits, dim ", dim];

(* ---- cost machinery ---- *)
tilts[i_] := Table[BitAnd[BitShiftRight[i, 2 k], 1] + 2 BitAnd[BitShiftRight[i, 2 k + 1], 1], {k, 0, n - 1}];
cost[t_List] := t.imat.t - lambda (cvec.t) + mu Total[t];
costVec = N[Table[cost[tilts[i]], {i, 0, dim - 1}]];
minCost = Min[costVec];
optIdx = Flatten[Position[costVec, minCost]];
Print["classical optimum: cost = ", minCost, "  tilts = ", tilts[First[optIdx] - 1]];

(* ---- fast statevector algebra (qubit k = bit k of the basis index) ---- *)
(* apply a 2x2 gate to qubit k: index = high*2^(k+1) + bit_k*2^k + low,
   so reshape to {2^(nQ-k-1), 2, 2^k}, bring the qubit axis to the front
   and hit it with a single packed Dot *)
apply1[g_, vec_, k_] := Module[{t},
   t = Transpose[ArrayReshape[vec, {2^(nQ - k - 1), 2, 2^k}], {2, 1, 3}];
   Flatten[Transpose[g . t, {2, 1, 3}]]];

hInit := ConstantArray[N[1/Sqrt[dim]], dim];
mixer[vec_, b_] := Fold[apply1[{{Cos[b/2], -I Sin[b/2]}, {-I Sin[b/2], Cos[b/2]}}, #1, #2] &,
   vec, Range[0, nQ - 1]];
phase[vec_, g_] := Exp[I g costVec] vec;
probs[vec_] := Abs[vec]^2;
expectCost[vec_] := costVec . probs[vec];
probOfOptimum[vec_] := Total[probs[vec][[optIdx]]];

(* ---- 1) QAOA p=1 ---- *)
qaoaP1[gv_?NumericQ, bv_?NumericQ] := expectCost[mixer[phase[hInit, gv], bv]];
t0 = TimeUsed[];
(* coarse landscape pre-scan: the p=1 surface has a flat plateau at the
   uniform-state mean (~35.5) that traps unseeded Nelder-Mead *)
scan = Flatten[Table[{g, b, qaoaP1[g, b]},
    {g, {0.02, 0.05, 0.1, 0.2}}, {b, {0.5, 0.8, 1.2, 1.6}}], 1];
seed = MinimalBy[scan, Last][[1]];
Print["grid pre-scan best: <C> = ", seed[[3]], " at (g,b) = ", Take[seed, 2]];
p1 = NMinimize[{qaoaP1[g, b], -2 Pi <= g <= 2 Pi, -Pi <= b <= Pi},
      {{g, seed[[1]] - 0.02, seed[[1]] + 0.02}, {b, seed[[2]] - 0.02, seed[[2]] + 0.02}},
      Method -> "NelderMead", MaxIterations -> 200];
psiP1 = mixer[phase[hInit, g /. p1[[2]]], b /. p1[[2]]];
p1res = <| "gamma" -> (g /. p1[[2]]), "beta" -> (b /. p1[[2]]),
   "expected_cost" -> p1[[1]], "p_optimum" -> probOfOptimum[psiP1] |>;
Print["QAOA p=1: <C> = ", p1res["expected_cost"],
  "  P(opt) = ", p1res["p_optimum"], "  (" , TimeUsed[] - t0, " s)"];

(* ---- 2) QAOA p=2 : grid refine around p=1 params ---- *)
g1 = p1res["gamma"]; b1 = p1res["beta"];
qaoaP2[g_, b_, g2_, b2_] := Module[{psi},
   psi = phase[hInit, g];  psi = mixer[psi, b];
   psi = phase[psi, g2];   psi = mixer[psi, b2];
   expectCost[psi]];
(* keep layer 1 at the p=1 optimum and scan layer 2; (g2,b2)=(0,0) is the
   identity, so the grid minimum can never be worse than p=1 *)
grid = Flatten[Table[{g1, b1, g2, b2},
   {g2, {0., 0.02, 0.05, 0.1, 0.2, 0.4}}, {b2, {0., 0.3, 0.6, 0.9, 1.2, 1.6}}], 1];
t0 = TimeUsed[];
evals = Table[{q, qaoaP2 @@ q}, {q, grid}];
best2 = MinimalBy[evals, Last][[1]];
(* local refinement of all four angles from the best grid point *)
qaoaP2n[ga_?NumericQ, ba_?NumericQ, gb_?NumericQ, bb_?NumericQ] := qaoaP2[ga, ba, gb, bb];
p2 = NMinimize[{qaoaP2n[ga, ba, gb, bb],
      -2 Pi <= ga <= 2 Pi, -Pi <= ba <= Pi, -2 Pi <= gb <= 2 Pi, -Pi <= bb <= Pi},
      MapThread[{#1, #2 - 0.02, #2 + 0.02} &, {{ga, ba, gb, bb}, best2[[1]]}],
      Method -> "NelderMead", MaxIterations -> 300];
p2params = {ga, ba, gb, bb} /. p2[[2]];
psiP2 = Fold[mixer[phase[#1, #2[[1]]], #2[[2]]] &, hInit,
   {p2params[[1 ;; 2]], p2params[[3 ;; 4]]}];
p2res = <| "params" -> p2params, "grid_expected_cost" -> best2[[2]],
   "expected_cost" -> p2[[1]], "p_optimum" -> probOfOptimum[psiP2] |>;
Print["QAOA p=2: <C> = ", p2res["expected_cost"],
  "  P(opt) = ", p2res["p_optimum"], "  (", TimeUsed[] - t0, " s)"];

(* ---- 3) VQE: RY + CZ hardware-efficient ansatz ---- *)
ry[t_] := {{Cos[t/2], -Sin[t/2]}, {Sin[t/2], Cos[t/2]}};
(* CZ signs for qubit pairs (2k, 2k+1): -1 where both bits are 1 *)
czSign = Table[If[BitAnd[BitShiftRight[x, 2 k], 1] == 1 &&
                  BitAnd[BitShiftRight[x, 2 k + 1], 1] == 1, -1., 1.],
   {k, 0, n/2 - 1}, {x, 0, dim - 1}];
vqeState[p_List] := Module[{psi, k},
   psi = ConstantArray[0. + 0. I, dim]; psi[[1]] = 1.; (* |0...0> *)
   Do[psi = apply1[ry[p[[k + 1]]], psi, k], {k, 0, nQ - 1}];
   Do[psi = psi * czSign[[k + 1]], {k, 0, n/2 - 1}];
   Do[psi = apply1[ry[p[[nQ + k + 1]]], psi, k], {k, 0, nQ - 1}];
   psi];
(* numeric guard: without it NMinimize evaluates vqeState on symbolic x[i]
   and builds a 4096-dim vector of symbolic trig expressions *)
vqeObj[p__?NumericQ] := With[{c = expectCost[vqeState[{p}]]}, Sow[c]; c];
t0 = TimeUsed[];
vars = Array[x, 2 nQ];
(* Nelder-Mead in 24 dims lands in local minima; keep the best of a few restarts.
   Reap collects the per-evaluation cost trace of each restart (vqeTraces). *)
reaped = Table[Reap[NMinimize[{vqeObj @@ vars, And @@ Map[-Pi <= # <= Pi &, vars]},
     vars, Method -> {"NelderMead", "RandomSeed" -> s}, MaxIterations -> 2000]], {s, 3}];
runs = reaped[[All, 1]];
vqeTraces = reaped[[All, 2, 1]];
vq = MinimalBy[runs, First][[1]];
psiVqe = vqeState[vars /. vq[[2]]];
vqeTilts = tilts[First[Ordering[probs[psiVqe], -1]] - 1];
vqeres = <| "expected_cost" -> vq[[1]], "p_optimum" -> probOfOptimum[psiVqe],
   "most_likely_tilts" -> vqeTilts, "most_likely_cost" -> cost[vqeTilts],
   "restart_costs" -> runs[[All, 1]] |>;
Print["VQE:      <C> = ", vqeres["expected_cost"],
  "  P(opt) = ", vqeres["p_optimum"], "  most likely tilts = ", vqeTilts,
  " (cost ", cost[vqeTilts], ")  (", TimeUsed[] - t0, " s)"];

(* ---- 4) Grover adaptive search (Durr-Hoyer) on a 2-antenna slice ---- *)
dim2 = 16;
sliceI = imat[[1 ;; 2, 1 ;; 2]]; sliceC = cvec[[1 ;; 2]];
cost2[i_] := Module[{q0, q1, q2, q3, t0, t1},
   q0 = BitAnd[i, 1]; q1 = BitAnd[BitShiftRight[i, 1], 1];
   q2 = BitAnd[BitShiftRight[i, 2], 1]; q3 = BitAnd[BitShiftRight[i, 3], 1];
   t0 = q0 + 2 q1; t1 = q2 + 2 q3;
   {t0, t1}.sliceI.{t0, t1} - lambda (sliceC.{t0, t1}) + mu (t0 + t1)];
cv2 = N[Table[cost2[i], {i, 0, dim2 - 1}]];
min2 = Min[cv2]; opt2 = Flatten[Position[cv2, min2]];
(* opt2 holds 1-based positions, so index the oracle 1-based too *)
marked = DiagonalMatrix[Table[If[MemberQ[opt2, i], -1., 1.], {i, 1, dim2}]];
uni = ConstantArray[1/Sqrt[dim2], dim2];
diff = 2 KroneckerProduct[uni, uni] - IdentityMatrix[dim2];
grover[k_] := Module[{psi = N[uni]},
   Do[psi = diff.(marked.psi), {k}];
   Total[Abs[psi[[opt2]]]^2]];
gsweep = Table[{k, grover[k]}, {k, 0, 4}];
bestK = First @ MaximalBy[gsweep, Last];
Print["Grover (2-antenna slice): optimum cost ", min2, "  tilts = ", tilts[First[opt2] - 1][[1 ;; 2]],
  ", best k = ", bestK[[1]], "  P(opt) = ", bestK[[2]],
  "  (random-baseline P = ", N[Length[opt2]/dim2], ")"];

(* ---- export ---- *)
result = <|
  "schema" -> "hackton-wolfram-realdataset-algorithms/1.0.0",
  "generated" -> DateString["ISODateTime"],
  "engine" -> "Wolfram statevector (plain algebra; conventions per verified wolfram_qaoa_sim.wl)",
  "instance" -> "opencellid_il2 (OpenCelliD MCC 425, real towers, Tel Aviv bbox)",
  "n_antennas" -> n, "n_qubits" -> nQ, "tilt_levels_sim" -> levels,
  "lambda" -> lambda, "mu" -> mu,
  "classical_optimum_cost" -> minCost,
  "classical_optimum_tilts" -> tilts[First[optIdx] - 1],
  "qaoa_p1" -> p1res, "qaoa_p2" -> p2res, "vqe" -> vqeres,
  "grover_slice2_popt_by_iterations" -> gsweep, (* list of {iterations, P(opt)} pairs *)
  "grover_slice2_optimum_cost" -> min2 |>;
Export[outJS, result];
Print["written: ", outJS];
