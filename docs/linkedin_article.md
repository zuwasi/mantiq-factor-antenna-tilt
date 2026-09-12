# LinkedIn article draft

Publishing notes (not part of the article):

- LinkedIn article editor: Write article > paste the text below section by section. Headings are the editor's "Heading 2".
- Video: put the cursor on an empty line, paste `https://youtu.be/OSEtTWnRQhc` and press Enter; LinkedIn turns it into an embedded player. Do this at the marker `[VIDEO]`.
- Images at the `[IMAGE ...]` markers (Insert image), all from `C:\Projects\mantiq-factor-antenna-tilt\`:
  - `docs\MantiQ-v2.png` (cover image, also use it as the article header)
  - `charts\map_small.jpg`
  - `wolfram\img\landscape.png`
  - `charts\wolfram_vs_classiq.png`
  - `animation\mantiq_pipeline_final_frame.png` (the GIF will not animate inside an article; if you want the animation itself, upload `animation\mantiq_pipeline.mp4` to YouTube as a second unlisted video and paste its link the same way)
- Article length is about 1,300 words, which is a 6 to 7 minute read.

---

## Title options (pick one)

1. From a PDF brief to a verified quantum program in one weekend: my QUBIT 2026 hackathon story
2. What happens when you run a hackathon problem through a production line: Amp, Wolfram, Lean 4 and Classiq
3. Compute first, engineer second: how the MantiQ Factor workflow carried an antenna-tilt problem onto Classiq

Subtitle: Six real Tel Aviv antennas, 12 qubits, three independent engines agreeing on every number.

---

[IMAGE docs\MantiQ-v2.png]

Last weekend I took part in the QUBIT 2026 hackathon with team Quantum Headache. The challenge was a telecom one: choose the electrical down-tilt of every sector antenna in a cellular network. Tilting an antenna down reduces the interference it causes to its neighbours, but it also shrinks the area it covers. Every antenna has one setting, every setting affects the neighbours, and a city has thousands of them.

I did not join to write a QAOA circuit as fast as possible. I joined to test a workflow I have been building for a while, which I call MantiQ Factor: a seven-stage production line that takes research documents in and produces a formally verified, executable program out. The stages are Input, Conversion, Understand, Compute, Verify, Engineer and Output. The tools behind them are Amp as the agent that drives everything, document converters, Wolfram Mathematica for exact computation, Lean 4 for proofs, and, in this case, Classiq as the quantum SDK and execution platform.

Here is what happened when a real hackathon problem went through that line.

## Stage 1 and 2: everything arrived as documents

Nothing arrived as code. The challenge came as a PDF. My teammates' Hamiltonian derivation came as a Markdown note with LaTeX. The group's architecture idea, k-means clustering of network regions with one QAOA job per cluster, came as a PDF. The group deck lived in Google Slides.

The converters turned all of it into Markdown with the formulas intact, and Amp read those files rather than the originals from then on. On the data side I refused to use a toy grid: I pulled six real sector antennas from OpenCelliD in the Ayalon area of Tel Aviv, computed pairwise distances and azimuth overlap, and got an interference matrix and a coverage vector. Real data cost nothing extra to model and made the result read as physics rather than as a puzzle.

[IMAGE charts\map_small.jpg]

## Stage 3: the decision the whole weekend depended on

The team's first proposal packed the 27 configurations of a three-sector site into 5 qubits. It sounded cheap. When I enumerated the problem exactly, it stopped looking cheap: 5 of the 32 basis states are invalid, the cost Hamiltonian becomes an arbitrary 5-qubit diagonal with terms up to ZZZZZ, and the team's own runs showed the optimum being sampled between 0.5 and 1.2 times as often as uniform. In other words, no quantum gain.

The alternative was two qubits per antenna, four tilt levels each. Every one of the 4,096 basis states is a valid plan, and the cost

Cost(t) = t^T I t - 1.5 c.t + 0.3 sum(t)

is quadratic in the tilts, so the Hamiltonian is 2-local: 12 Z terms, 60 ZZ terms, one constant, nothing heavier. Six antennas, 12 qubits. Small enough to enumerate every plan and know the truth, which is exactly what you want when the point is to check the quantum result against something.

I wrote this comparison down before writing any circuit, with the numbers, so the team could veto it. They did not.

## Stage 4: Wolfram finds the angles before Classiq is opened

This is the stage that changed the shape of the weekend. Instead of letting an optimizer search for QAOA angles on the simulator, I built the 4,096-dimensional statevector in Mathematica, applied the phase and mixer layers as dense matrices, and evaluated the expected cost exactly over the whole (gamma, beta) plane.

[IMAGE wolfram\img\landscape.png]

The landscape is flat almost everywhere at an expected cost around 35, with one narrow valley. The p = 1 minimum sits at gamma = 0.0654, beta = 1.1293, with expected cost 1.9985, a 53 percent chance that a sampled plan has negative cost, and the optimum sampled 27 times more often than uniform. For p = 2 the expected cost drops to -0.38 and the negative-cost probability to 67 percent. The angles went into a JSON file. That file is the hot start.

## Stage 5: Lean 4 proves the parts that fail silently

A QAOA demo can be wrong and still produce a convincing histogram. So before engineering, I proved in Lean 4 with Mathlib the facts that engineering could break without anyone noticing: the two-qubit encoding is a bijection onto the four tilt levels; -2.844 is the minimum cost; it is attained at tilt plan (0,3,0,0,0,0) and nowhere else; the phase layer has unit norm, so it is diagonal and preserves every measurement probability; and 2 P0 = 1 + Z, 2 P1 = 1 - Z, which justifies the Z-only decomposition. 109 lines, zero sorry.

The physics of the answer is pleasing: only antenna A1, the one with the most overlap, tilts. The other five stay flat.

## Stage 6: the cost becomes one phase() statement in Qmod

Only now did I open the Classiq SDK. The register is a QStruct holding QArray[QNum[2], 6]. The cost function is written as ordinary arithmetic on the QNum values and applied with phase(cost(t), gamma). I never expanded the 73 Pauli terms by hand for the circuit; Classiq synthesized the diagonal unitary itself. The result at p = 1: width 12, depth 59, 92 CX gates. At p = 2: depth 114, 184 CX.

## Stage 7: the Classiq run reproduces the prediction

[IMAGE charts\wolfram_vs_classiq.png]

At the Wolfram angles, 4,096 shots on the Classiq simulator gave an expected cost of 2.02 to 2.06 against the predicted 1.9985, a negative-cost probability of 0.525 against 0.53, and the optimum sampled 27 to 29 times more often than uniform. The best sampled bitstring in every run decoded to (0,3,0,0,0,0), the plan Lean had proved optimal. At p = 2, -0.39 against -0.38. I also exported the circuit as OpenQASM and re-simulated it in Qiskit's statevector backend: 1.9985, identical to Mathematica.

Then I ran COBYLA on Classiq starting from the Wolfram angles. Eight iterations, nothing better. For comparison, the hackathon runs that started blind got stuck at 35.5 on the plateau, or crawled from 21.6 to 7.0 over 20 simulator jobs without reaching 2.0. Shot noise hides the gradient; exact classical pre-computation of a small instance does not have that problem.

Here is the five-minute demo we recorded, with the live Classiq runs:

[VIDEO]

## What the team's hierarchy adds

My twelve qubits are one leaf. The team's architecture clusters network regions with k-means (k = 5), solves one QAOA per cluster, and refines where the utility gain justifies it. On the 48-region toy benchmark, one plan for the whole network scores 1.379, the hierarchy with QAOA scores 1.547 with 10 jobs, and the per-region ceiling is 1.838 with 48 jobs. Three refinement cycles already reach 95 percent of that ceiling. The hierarchy is encoding-agnostic, so the verified leaf plugs straight in.

## What I take away

Compute before you engineer. The exact simulation cost eighty seconds and saved every blind optimizer job we would otherwise have burned on the simulator.

Prove the parts that fail silently. Encoding, true optimum, unitarity of the phase layer. Not the whole algorithm, just the places where a plausible-looking result can be wrong.

Make the model decision explicit and numeric. The 2-qubit versus 5-qubit argument was a table, not an opinion, and it was written down before code existed.

Files between stages, not memory. JSON angles, Markdown Hamiltonian, Lean source, Qmod. Any stage can be rerun alone. The presentation itself was built from those files by a script.

An agent is the glue. Amp drove the converters, the Mathematica kernel, the Lean build and the Classiq SDK from a single thread. I read numbers and made decisions.

## Where everything lives

Everything is public under MIT, including the data, the Wolfram notebook, the Lean proofs, the Classiq notebook, an animation of the pipeline and the full deck:

https://github.com/zuwasi/mantiq-factor-antenna-tilt

The notebook has been submitted to the Classiq library as a telecom application demo:

https://github.com/Classiq/classiq-library/pull/1736

The hackathon repository of team Quantum Headache:

https://github.com/zuwasi/quantum-headache-antenna-tilt

Antenna positions are from OpenCelliD (CC BY-SA 4.0).

Thank you to my teammates in Quantum Headache and to the QUBIT 2026 organizers and Classiq for the student-edition access that made the live runs possible.

If you are turning research documents into quantum programs and want to talk about the workflow, my inbox is open.

#QuantumComputing #QAOA #Classiq #WolframMathematica #Lean4 #FormalVerification #Telecom #Hackathon #QUBIT2026 #MantiQFactor #AgenticAI
