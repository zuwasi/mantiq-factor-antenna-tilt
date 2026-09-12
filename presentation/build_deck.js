// Builds MantiQ_Factor_Antenna_Tilt.pptx: how the MantiQ Factor workflow took the QUBIT 2026
// antenna-tilt challenge from a PDF brief to a verified Classiq program.
// Run: powershell -ExecutionPolicy Bypass -File "$HOME\.agents\skills\working-with-pptx\scripts\run-pptx-node.ps1" C:\Projects\mantiq-factor-antenna-tilt\presentation\build_deck.js
const pptxgen = require('pptxgenjs');
const path = require('path');

const R = 'C:/Projects/mantiq-factor-antenna-tilt/';
const img = (p) => path.join(R, p);

const C = {
  bg: '070B1C', panel: '0D1330', panel2: '131A3D', ink: 'F4F6FB', muted: '9AA3BD',
  gold: 'F2B632', cyan: '2FD4D4', red: 'FF5C7A', green: '5BE39A',
};
const FONT = 'Calibri';

const pptx = new pptxgen();
pptx.layout = 'LAYOUT_WIDE'; // 13.33 x 7.5 in
pptx.author = 'Daniel Liezrowice';
pptx.title = 'MantiQ Factor: antenna tilt with QAOA';

const TOTAL = 16;
let slideNo = 0;
function numberSlide(s) {
  slideNo += 1;
  s.addShape(pptx.ShapeType.roundRect, { x: 11.35, y: 6.6, w: 1.75, h: 0.7, fill: { color: C.gold }, line: { color: C.gold }, rectRadius: 0.1 });
  s.addText(slideNo + ' / ' + TOTAL, { x: 11.35, y: 6.6, w: 1.75, h: 0.7, fontFace: FONT, fontSize: 28, bold: true, color: C.bg, align: 'center', valign: 'middle', margin: 0 });
}
function base(title, kicker) {
  const s = pptx.addSlide();
  numberSlide(s);
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 0.18, h: 7.5, fill: { color: C.gold } });
  if (kicker) s.addText('SLIDE ' + slideNo + ' / ' + TOTAL + '   |   ' + kicker.toUpperCase(), { x: 0.6, y: 0.35, w: 12, h: 0.3, fontFace: FONT, fontSize: 11, color: C.cyan, bold: true, charSpacing: 2, margin: 0 });
  s.addText(title, { x: 0.6, y: 0.65, w: 12.1, h: 0.75, fontFace: FONT, fontSize: 30, bold: true, color: C.ink, margin: 0 });
  s.addText('MantiQ Factor  |  Antenna tilt with QAOA  |  QUBIT 2026 case study', { x: 0.6, y: 7.05, w: 8, h: 0.3, fontFace: FONT, fontSize: 10, color: C.muted, margin: 0 });
  return s;
}
function bullets(s, items, o) {
  s.addText(items.map((t) => ({ text: t, options: { bullet: { code: '25B8' }, breakLine: true, paraSpaceAfter: 6 } })),
    { fontFace: FONT, fontSize: o.fontSize || 15, color: C.ink, valign: 'top', margin: 0.05, ...o });
}
function panel(s, x, y, w, h, color) {
  s.addShape(pptx.ShapeType.roundRect, { x, y, w, h, fill: { color: color || C.panel }, line: { color: color || C.panel }, rectRadius: 0.08 });
}
function stat(s, x, y, w, big, small, color) {
  panel(s, x, y, w, 1.35);
  s.addText(big, { x, y: y + 0.12, w, h: 0.7, fontFace: FONT, fontSize: 28, bold: true, color: color || C.cyan, align: 'center', margin: 0 });
  s.addText(small, { x: x + 0.1, y: y + 0.8, w: w - 0.2, h: 0.5, fontFace: FONT, fontSize: 11, color: C.muted, align: 'center', margin: 0 });
}
function caption(s, text, x, y, w) {
  s.addText(text, { x, y, w, h: 0.4, fontFace: FONT, fontSize: 10.5, color: C.muted, italic: true, margin: 0 });
}
function code(s, lines, x, y, w, h, fs) {
  panel(s, x, y, w, h, '05081A');
  s.addText(lines.map((t) => ({ text: t, options: { breakLine: true } })),
    { x: x + 0.1, y: y + 0.08, w: w - 0.2, h: h - 0.16, fontFace: 'Consolas', fontSize: fs || 11, color: C.green, valign: 'top', margin: 0.02 });
}
function stageTag(s, n, name) {
  s.addShape(pptx.ShapeType.roundRect, { x: 8.75, y: 6.68, w: 2.45, h: 0.55, fill: { color: C.panel2 }, line: { color: C.gold, width: 1 }, rectRadius: 0.1 });
  s.addText([
    { text: 'STAGE ' + n + '  ', options: { color: C.gold, bold: true } },
    { text: name, options: { color: C.ink } },
  ], { x: 8.75, y: 6.68, w: 2.45, h: 0.55, fontFace: FONT, fontSize: 13, align: 'center', valign: 'middle', margin: 0 });
}
const tblHead = { bold: true, color: C.gold, fill: { color: C.panel2 }, fontFace: FONT, fontSize: 12 };
const tblCell = { color: C.ink, fill: { color: C.panel }, fontFace: FONT, fontSize: 12 };

// ---------- 1. Title ----------
{
  const s = pptx.addSlide();
  numberSlide(s);
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.25, fill: { color: C.gold } });
  s.addText('MANTIQ FACTOR  |  CASE STUDY', { x: 0.8, y: 1.3, w: 11.5, h: 0.4, fontFace: FONT, fontSize: 14, color: C.cyan, bold: true, charSpacing: 3, margin: 0 });
  s.addText('From a PDF brief to a verified quantum program', { x: 0.8, y: 1.7, w: 11.8, h: 1.6, fontFace: FONT, fontSize: 44, bold: true, color: C.ink, margin: 0 });
  s.addText('Antenna tilt optimization with QAOA on real Tel Aviv cell-tower data, computed in Wolfram, proved in Lean 4, engineered and run on Classiq', { x: 0.8, y: 3.35, w: 6.6, h: 1.2, fontFace: FONT, fontSize: 18, color: C.muted, margin: 0 });
  s.addImage({ path: img('docs/MantiQ-v2.png'), x: 7.6, y: 3.3, w: 4.8, h: 3.2 });
  s.addText('Daniel Liezrowice', { x: 0.8, y: 5.2, w: 6, h: 0.5, fontFace: FONT, fontSize: 20, bold: true, color: C.ink, margin: 0 });
  s.addText('Team Quantum Headache, QUBIT 2026 hackathon  |  September 2026', { x: 0.8, y: 5.65, w: 6.4, h: 0.4, fontFace: FONT, fontSize: 14, color: C.muted, margin: 0 });
  s.addText('github.com/zuwasi/mantiq-factor-antenna-tilt', { x: 0.8, y: 6.1, w: 6.4, h: 0.4, fontFace: FONT, fontSize: 13, color: C.cyan, margin: 0 });
  s.addNotes('MantiQ Factor is the production line: input, conversion, understand, compute, verify, engineer, output. This deck walks the antenna-tilt challenge through all seven stages and shows the numbers that came out at each one.');
}

// ---------- 2. MantiQ Factor overview ----------
{
  const s = base('MantiQ Factor: a seven-stage production line', 'What it is');
  s.addImage({ path: img('docs/MantiQ-v2.png'), x: 0.6, y: 1.5, w: 7.2, h: 4.8 });
  caption(s, 'The pipeline: Input, Conversion, Understand, Compute, Verify, Engineer, Output. Tools: Amp (agentic orchestration), Wolfram Mathematica, Lean 4, converters, skills, knowledge bases.', 0.6, 6.35, 7.4);
  bullets(s, [
    'Every stage leaves an artifact on disk (Markdown, JSON, .nb, .lean, .qmod) so the next stage consumes a file, not a memory',
    'Compute and Engineer are separated: the exact simulation picks the angles, the SDK builds the circuit',
    'Verify is a formal step, not a code review: Lean 4 theorems about the cost function and the circuit',
    'One agent (Amp) drives the tools; humans decide the model and read the numbers',
    'Result: every claim in the final program traces back to a proof, a simulation or a dataset',
  ], { x: 8.1, y: 1.55, w: 4.8, h: 4.9, fontSize: 14 });
  s.addNotes('The picture is the one we animated. The key property is that stages hand over files, so the workflow is reproducible and each number can be re-derived.');
}

// ---------- 3. The problem and the inputs ----------
{
  const s = base('Stage 1, Input: the challenge and what the team handed over', 'Input');
  stageTag(s, 1, 'Input');
  s.addImage({ path: img('charts/map_small.jpg'), x: 0.6, y: 1.55, w: 5.2, h: 3.6 });
  caption(s, 'Six real sector antennas from OpenCelliD, Tel Aviv (data/opencellid_il2.csv). Interference matrix from pairwise distances and azimuths.', 0.6, 5.2, 5.3);
  bullets(s, [
    'Challenge (QUBIT 2026): choose the electrical down-tilt of every sector antenna. Tilting down cuts interference on neighbours but shrinks coverage',
    'Inputs received as documents, not code: the challenge brief (PDF), the team Hamiltonian note (Markdown with LaTeX), the k-means hierarchy concept (PDF), the group deck (Google Slides)',
    'Team utility: U(t) = alpha Q(t) - beta I(t) - gamma D(t); quality, interference, unmet demand',
    'Team proposal: 27 three-sector configurations packed into 5 qubits, groups by k-means with k = 5',
    'Constraint: Classiq student edition, 15 parallel jobs, simulator only',
  ], { x: 6.1, y: 1.55, w: 6.8, h: 4.9, fontSize: 14 });
  s.addNotes('Stage 1 is deliberately about what arrives, in whatever format it arrives. Real data was pulled from OpenCelliD (CC BY-SA) rather than a toy grid.');
}

// ---------- 4. Conversion ----------
{
  const s = base('Stage 2, Conversion: documents become machine-readable facts', 'Conversion');
  stageTag(s, 2, 'Conversion');
  const box = (x, y, w, head, body, color) => {
    panel(s, x, y, w, 1.5);
    s.addText([
      { text: head, options: { bold: true, color: color || C.gold, fontSize: 13, breakLine: true } },
      { text: body, options: { color: C.ink, fontSize: 11.5 } },
    ], { x: x + 0.1, y, w: w - 0.2, h: 1.5, fontFace: FONT, valign: 'middle', margin: 0.03 });
  };
  box(0.6, 1.6, 3.9, 'PDF brief, team PDF', 'Read with a PDF converter into Markdown; formulas kept as LaTeX. Output: docs/qaoa_antenna_hamiltonian_explanation.md');
  box(4.7, 1.6, 3.9, 'Google Slides deck', 'Exported to PDF, read slide by slide, merged into one PPTX built from code (build_deck.js), so the deck is reproducible too');
  box(8.8, 1.6, 4.1, 'OpenCelliD CSV', 'Pipeline data/opencellid_pipeline.py: filter Tel Aviv sectors, compute distances, azimuth overlap, interference matrix I and coverage vector c');
  s.addText('What conversion decided (and recorded in the Markdown):', { x: 0.6, y: 3.35, w: 12, h: 0.4, fontFace: FONT, fontSize: 15, bold: true, color: C.cyan, margin: 0 });
  bullets(s, [
    'Keep the team utility form; maximize U is the same as minimize Cost = -U (later proved as theorem maximize_utility_iff_minimize_negative)',
    'Fix the weights for the real dataset: beta = 1 (interference t^T I t), alpha = 1.5 (coverage c.t), gamma = 0.3 (tilt penalty sum t)',
    'Four discrete tilt levels per antenna (0, 2, 4, 6 degrees) instead of continuous angles: the register is exactly 2 qubits',
    'Six antennas give 4^6 = 4096 plans: small enough to enumerate exactly, so every quantum number can be checked against the truth',
  ], { x: 0.6, y: 3.8, w: 12.3, h: 2.6, fontSize: 14 });
  s.addNotes('Conversion is where formats stop mattering. Every later stage reads the Markdown, the CSV and the JSON, never the original PDF.');
}

// ---------- 5. Understand: model decision ----------
{
  const s = base('Stage 3, Understand: 2 qubits per antenna, not a 5-qubit pack', 'Understand');
  stageTag(s, 3, 'Understand');
  s.addTable([
    [{ text: '', options: tblHead }, { text: 'Team proposal: 27 configs in 5 qubits', options: tblHead }, { text: 'Chosen: 2 qubits per antenna (QNum[2])', options: tblHead }],
    [{ text: 'Encoding', options: tblCell }, { text: '3 tilts x 3 sectors = 27 states of 32; 5 states invalid', options: tblCell }, { text: '4 tilts per antenna; all 4096 states valid', options: tblCell }],
    [{ text: 'Cost Hamiltonian', options: tblCell }, { text: 'Arbitrary 5-qubit diagonal: terms up to ZZZZZ', options: tblCell }, { text: '2-local Ising: 12 Z + 60 ZZ + offset (73 terms)', options: tblCell }],
    [{ text: 'Invalid-state mass (team numbers)', options: tblCell }, { text: '15.6% at start, 3% after training', options: tblCell }, { text: '0%, by construction', options: tblCell }],
    [{ text: 'P(optimum) / uniform (team numbers)', options: tblCell }, { text: '0.5x to 1.2x', options: tblCell }, { text: '27x (Wolfram), 27x to 29x (Classiq)', options: tblCell }],
    [{ text: 'Scales to more antennas', options: tblCell }, { text: 'No: 3 sectors fixed per pack', options: tblCell }, { text: 'Yes: 2n qubits, still 2-local', options: tblCell }],
    [{ text: 'Provable', options: tblCell }, { text: 'Hard: decode is a lookup table', options: tblCell }, { text: 'decodeTilt is a bijection (Lean theorem)', options: tblCell }],
  ], { x: 0.6, y: 1.6, w: 12.2, colW: [2.6, 4.8, 4.8], rowH: 0.48, border: { type: 'solid', color: C.bg, pt: 1 } });
  bullets(s, [
    'This is the decision the whole pipeline depends on. It was made here, with the exact enumeration in hand, before any circuit existed',
    'The team hierarchy idea (k-means groups, one QAOA per group, recursive refinement) was kept: our 12-qubit problem is one leaf of that tree',
  ], { x: 0.6, y: 5.45, w: 12.3, h: 1.1, fontSize: 14 });
  s.addNotes('The 5-qubit pack looked cheaper but its Hamiltonian is dense and not scalable, and the team measured almost no quantum gain from it. The 2-qubit register gives a 2-local Ising model that Classiq synthesizes efficiently.');
}

// ---------- 6. Hamiltonian ----------
{
  const s = base('Stage 3, Understand: the cost function and its Pauli decomposition', 'Understand');
  stageTag(s, 3, 'Understand');
  panel(s, 0.6, 1.6, 6.3, 1.7);
  s.addText([
    { text: 'Cost(t) = t^T I t  -  1.5 c . t  +  0.3 sum(t)', options: { fontSize: 22, bold: true, color: C.cyan, breakLine: true } },
    { text: 't in {0,1,2,3}^6 (tilt levels), I = 6x6 interference matrix from the map, c = coverage per antenna', options: { fontSize: 12.5, color: C.ink, breakLine: true } },
    { text: 'tilt_i = 2 q_{2i} + q_{2i+1}, so t_i is linear in its two qubits and t_i t_j gives only ZZ terms', options: { fontSize: 12.5, color: C.muted } },
  ], { x: 0.75, y: 1.65, w: 6.0, h: 1.6, fontFace: FONT, valign: 'middle', margin: 0.05 });
  s.addTable([
    [{ text: 'Pauli weight', options: tblHead }, { text: 'terms', options: tblHead }, { text: 'meaning', options: tblHead }],
    [{ text: '0', options: tblCell }, { text: '1', options: tblCell }, { text: 'offset 35.499 (global phase, dropped)', options: tblCell }],
    [{ text: '1 (Z)', options: tblCell }, { text: '12', options: tblCell }, { text: 'coverage gain and tilt penalty, 2 per antenna', options: tblCell }],
    [{ text: '2 (ZZ)', options: tblCell }, { text: '60', options: tblCell }, { text: '15 interfering pairs x 4 qubit pairs', options: tblCell }],
    [{ text: '3, 4, 5', options: tblCell }, { text: '0', options: tblCell }, { text: 'none: the model is 2-local', options: tblCell }],
  ], { x: 0.6, y: 3.5, w: 6.3, colW: [1.4, 0.9, 4.0], rowH: 0.42, border: { type: 'solid', color: C.bg, pt: 1 } });
  caption(s, 'gates/pauli_terms.json: Walsh-Hadamard transform of the 4096-entry cost table, checked to 1e-9 against every entry.', 0.6, 5.7, 6.3);
  stat(s, 7.2, 1.6, 2.75, '4096', 'plans enumerated exactly', C.gold);
  stat(s, 10.15, 1.6, 2.75, '-2.844', 'unique minimum at (0,3,0,0,0,0)', C.gold);
  stat(s, 7.2, 3.1, 2.75, '73', 'Pauli terms, all weight <= 2');
  stat(s, 10.15, 3.1, 2.75, '12', 'qubits: 6 antennas x QNum[2]');
  bullets(s, [
    'Only antenna 1 tilts (level 3); the other five stay flat. That is physically sensible: it is the antenna with the most overlap',
    'Naive layer cost: 72 RZ + 120 CX; Classiq synthesis merges parity ladders down to 92 CX',
  ], { x: 7.2, y: 4.65, w: 5.7, h: 1.8, fontSize: 13.5 });
  s.addNotes('The classical truth is cheap here on purpose. It is what lets Wolfram, Lean and Classiq be compared number by number.');
}

// ---------- 7. Compute: Wolfram landscape ----------
{
  const s = base('Stage 4, Compute: Wolfram exact simulation picks the angles', 'Compute');
  stageTag(s, 4, 'Compute');
  s.addImage({ path: img('wolfram/img/landscape.png'), x: 0.6, y: 1.55, w: 4.6, h: 4.4 });
  caption(s, 'Expected cost over (gamma, beta) for p = 1, evaluated exactly on the 4096-dimensional state. Minimum marked.', 0.6, 6.0, 4.7);
  bullets(s, [
    'wolfram/wolfram_realdataset_algorithms.wl builds H_C from the same JSON, applies exp(-i gamma H_C) and the RX mixer as dense matrices, no sampling noise',
    'p = 1 optimum: gamma = 0.0654, beta = 1.1293, giving <Cost> = 1.9985, P(cost < 0) = 0.53, P(optimum) = 0.0066 (27x uniform)',
    'p = 2 optimum: <Cost> = -0.3825, P(cost < 0) = 0.67',
    'Also compared: VQE, Grover-style amplification and plain uniform sampling on the same cost table',
    'The angles are written to wolfram_realdataset_algorithms.json: this is the hot start the Classiq circuit later uses',
  ], { x: 5.5, y: 1.55, w: 7.4, h: 3.4, fontSize: 14 });
  stat(s, 5.5, 5.05, 2.35, '1.9985', 'predicted <Cost>, p=1');
  stat(s, 8.0, 5.05, 2.35, '0.53', 'P(cost < 0), p=1');
  stat(s, 10.5, 5.05, 2.4, '27x', 'P(optimum) vs uniform', C.gold);
  s.addNotes('Compute means the numbers are known before any SDK is opened. The Classiq run then becomes a test of the engineering, not an exploration.');
}

// ---------- 8. Compute: gain and shots ----------
{
  const s = base('Stage 4, Compute: what the quantum gain is worth in shots', 'Compute');
  stageTag(s, 4, 'Compute');
  s.addImage({ path: img('charts/quantum_gain.png'), x: 0.6, y: 1.55, w: 6.6, h: 3.7 });
  caption(s, 'charts/quantum_gain.png: probability of the optimum and of a negative-cost plan, uniform vs QAOA p=1 and p=2.', 0.6, 5.3, 6.7);
  s.addImage({ path: img('wolfram/img/shots.png'), x: 7.4, y: 1.55, w: 5.5, h: 2.65 });
  caption(s, 'Shots needed for a 95% chance of sampling the optimum at least once.', 7.4, 4.25, 5.5);
  s.addTable([
    [{ text: 'sampler', options: tblHead }, { text: 'P(opt)', options: tblHead }, { text: 'shots for 95%', options: tblHead }],
    [{ text: 'uniform', options: tblCell }, { text: '1/4096', options: tblCell }, { text: '12,270', options: tblCell }],
    [{ text: 'QAOA p = 1', options: tblCell }, { text: '0.0066', options: tblCell }, { text: 'about 450', options: tblCell }],
    [{ text: 'QAOA p = 2', options: tblCell }, { text: '0.0098', options: tblCell }, { text: 'about 300', options: tblCell }],
  ], { x: 7.4, y: 4.7, w: 5.5, colW: [2.1, 1.5, 1.9], rowH: 0.4, border: { type: 'solid', color: C.bg, pt: 1 } });
  bullets(s, ['Honest framing: at 12 qubits a laptop enumerates 4096 plans instantly. The gain is a property of the algorithm we can measure exactly here and carry to sizes where enumeration stops (slide 13).'],
    { x: 0.6, y: 5.75, w: 6.7, h: 0.8, fontSize: 13 });
  s.addNotes('27x at p=1 and about 40x at p=2. The shots table is the operational meaning of that gain.');
}

// ---------- 9. Verify: Lean 4 ----------
{
  const s = base('Stage 5, Verify: Lean 4 theorems, zero sorry', 'Verify');
  stageTag(s, 5, 'Verify');
  code(s, [
    'def decodeTilt (q0 q1 : Fin 2) : Fin 4 := ...',
    'theorem decodeTilt_bijective :',
    '  Function.Bijective (fun q : Fin 2 x Fin 2 => decodeTilt q.1 q.2)',
    '',
    'def costS (t : Fin 6 -> Fin 4) : Int := ...   -- scaled x 10^4',
    'def optTilt : Fin 6 -> Fin 4 := ![0, 3, 0, 0, 0, 0]',
    'theorem costS_optTilt : costS optTilt = -28440',
    'theorem costS_lower_bound : forall t, -28440 <= costS t',
    'theorem costS_unique : forall t, costS t = -28440 -> t = optTilt',
    '',
    'theorem cost_phase_norm : forall gamma c : Real,',
    '  norm (Complex.exp ((gamma * c : Real) * Complex.I)) = 1',
    'theorem cost_phase_preserves_probability : ...',
    'theorem two_smul_P0 : (2 : Rat) * P0 = 1 + Z   -- Z decomposition',
  ], 0.6, 1.55, 7.0, 4.6, 11.5);
  caption(s, 'lean/TiltQAOA.lean, 109 lines, Mathlib. Build log: lean/tilt_qaoa_lean_build.log. Cost scaled by 10^4 so the theorems are over integers and decide by computation.', 0.6, 6.2, 7.2);
  bullets(s, [
    'Encoding: the 2-qubit register maps one-to-one onto the four tilt levels, so no state is invalid or double-counted',
    'Classical truth: -2.844 is the minimum, it is attained at (0,3,0,0,0,0), and nowhere else',
    'Circuit: the cost layer exp(i gamma Cost) has unit norm, so it changes phases only and keeps every measurement probability of a basis state',
    'Bridge to the gate set: 2 P0 = 1 + Z and 2 P1 = 1 - Z justify the Z-only decomposition of the Hamiltonian',
    'These are the statements the Wolfram numbers and the Classiq samples are later checked against',
  ], { x: 7.9, y: 1.55, w: 5.0, h: 4.9, fontSize: 13.5 });
  s.addNotes('Verify does not prove the whole QAOA algorithm. It proves the parts that engineering can get wrong silently: encoding, the classical optimum, and that the phase layer is unitary and diagonal.');
}

// ---------- 10. Engineer: Classiq Qmod ----------
{
  const s = base('Stage 6, Engineer: the cost becomes a Qmod phase() statement', 'Engineer');
  stageTag(s, 6, 'Engineer');
  code(s, [
    'class Tilts(QStruct):',
    '    tilts: QArray[QNum[2], 6]        # 6 antennas x 2 qubits',
    '',
    'def cost(t: Tilts) -> CReal:',
    '    interference = sum(I[i][j] * t.tilts[i] * t.tilts[j] ...)',
    '    coverage     = sum(c[i] * t.tilts[i] ...)',
    '    return interference - 1.5 * coverage + 0.3 * sum(t.tilts)',
    '',
    '@qfunc',
    'def main(gammas: CArray[CReal, P], betas: CArray[CReal, P],',
    '         t: Output[Tilts]):',
    '    allocate(t)',
    '    hadamard_transform(t)',
    '    repeat(P, lambda k: [phase(cost(t), gammas[k]),',
    '                        apply_to_all(lambda q: RX(2*betas[k], q), t)])',
    '',
    'qprog = synthesize(qmod)   # width 12, depth 59, 92 CX',
    'res = execute(qprog, gammas=[0.0654], betas=[1.1293])  # hot start',
  ], 0.6, 1.55, 7.0, 4.75, 11);
  s.addImage({ path: img('charts/circuit_stats.png'), x: 7.9, y: 1.55, w: 5.0, h: 2.6 });
  caption(s, 'charts/circuit_stats.png: synthesized circuit sizes for p = 1 and p = 2.', 7.9, 4.15, 5.0);
  bullets(s, [
    'No hand-built CX ladders: phase() takes the arithmetic cost expression and Classiq synthesizes the diagonal unitary',
    'The Pauli decomposition (gates/) exists only to predict gate counts and to feed Wolfram; the SDK never sees it',
    'Deliverables: antenna_tilt_optimization.ipynb, .qmod, .synthesis_options.json, .metadata.json (classiq-library format)',
    'classiq/qaoa_tilt_classiq.py is the standalone script with COBYLA on the simulator',
  ], { x: 7.9, y: 4.6, w: 5.0, h: 2.0, fontSize: 12.5 });
  s.addNotes('Engineer is the only stage that touches the SDK. Everything it needs, the cost, the angles, the expected numbers, arrives as files from the earlier stages.');
}

// ---------- 11. Output: Classiq results ----------
{
  const s = base('Stage 7, Output: Classiq reproduces the Wolfram prediction', 'Output');
  stageTag(s, 7, 'Output');
  s.addImage({ path: img('charts/wolfram_vs_classiq.png'), x: 0.6, y: 1.55, w: 7.4, h: 3.05 });
  caption(s, 'charts/wolfram_vs_classiq.png: exact statevector (Wolfram) against 4096-shot samples on the Classiq simulator at the same angles.', 0.6, 4.62, 7.4);
  s.addImage({ path: img('charts/classiq_convergence.png'), x: 8.2, y: 1.55, w: 4.7, h: 2.5 });
  caption(s, 'COBYLA on Classiq starting from the Wolfram angles: 8 iterations, no improvement over the hot start, angles stay at (0.065, 1.149).', 8.2, 4.07, 4.7);
  stat(s, 0.6, 5.15, 2.35, '2.06', 'Classiq <Cost> p=1 (pred. 2.00)');
  stat(s, 3.1, 5.15, 2.35, '0.525', 'P(cost<0) (pred. 0.53)');
  stat(s, 5.6, 5.15, 2.4, '29x', 'P(optimum) vs uniform (pred. 27x)', C.gold);
  stat(s, 8.2, 5.15, 2.25, '-0.39', 'Classiq <Cost> p=2 (pred. -0.38)');
  stat(s, 10.6, 5.15, 2.3, '(0,3,0,0,0,0)', 'best sampled plan = proven optimum', C.gold);
  s.addNotes('Differences are within shot noise at 4096 shots. The best sampled plan is exactly the plan Lean proved optimal.');
}

// ---------- 12. Cross-check table ----------
{
  const s = base('Three independent engines, one set of numbers', 'Cross-check');
  s.addTable([
    [{ text: 'quantity', options: tblHead }, { text: 'Lean 4 (proof)', options: tblHead }, { text: 'Wolfram (exact state)', options: tblHead }, { text: 'Classiq (4096 shots)', options: tblHead }, { text: 'agree', options: tblHead }],
    [{ text: 'minimum cost', options: tblCell }, { text: '-2.8440 (theorem)', options: tblCell }, { text: '-2.8440', options: tblCell }, { text: '-2.8440 (best sample)', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: 'argmin', options: tblCell }, { text: '(0,3,0,0,0,0), unique', options: tblCell }, { text: '(0,3,0,0,0,0)', options: tblCell }, { text: '(0,3,0,0,0,0)', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: 'encoding valid', options: tblCell }, { text: 'bijection', options: tblCell }, { text: '4096 states, all decode', options: tblCell }, { text: 'all samples decode', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: '<Cost> p=1 at hot start', options: tblCell }, { text: '', options: tblCell }, { text: '1.9985 (Qiskit statevector of the exported QASM: 1.9985)', options: tblCell }, { text: '2.02 to 2.06 (4096 shots), 1.99 after COBYLA', options: tblCell }, { text: 'shot noise', options: { ...tblCell, color: C.cyan } }],
    [{ text: 'P(cost < 0) p=1', options: tblCell }, { text: '', options: tblCell }, { text: '0.53', options: tblCell }, { text: '0.525', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: 'P(optimum) p=1', options: tblCell }, { text: '', options: tblCell }, { text: '0.0066 (27x)', options: tblCell }, { text: '0.0066 to 0.0071 (27x to 29x)', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: '<Cost> p=2', options: tblCell }, { text: '', options: tblCell }, { text: '-0.3825', options: tblCell }, { text: '-0.39', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
    [{ text: 'phase layer diagonal, unit norm', options: tblCell }, { text: 'theorem', options: tblCell }, { text: 'matrix check', options: tblCell }, { text: 'synthesized as RZ ladders only', options: tblCell }, { text: 'yes', options: { ...tblCell, color: C.green, bold: true } }],
  ], { x: 0.6, y: 1.6, w: 12.2, colW: [2.7, 2.4, 2.4, 3.3, 1.4], rowH: 0.46, border: { type: 'solid', color: C.bg, pt: 1 } });
  bullets(s, [
    'The value of MantiQ Factor is this table: no number in the demo rests on a single tool',
    'Blind COBYLA starts on Classiq (hackathon runs): start (0.20, 0.50) stuck at <Cost> 35.5, start (0.02, 0.60) reached only 7.0 after 20 jobs. From the Wolfram angles: 2.0 in the first job, and 8 more iterations found nothing better',
  ], { x: 0.6, y: 5.85, w: 12.3, h: 0.9, fontSize: 13.5 });
  s.addNotes('If any row disagreed, the pipeline would tell you which stage to reopen: a proof failure means the model, a Wolfram mismatch means the Hamiltonian, a Classiq mismatch means the circuit.');
}

// ---------- 13. Scaling ----------
{
  const s = base('Where this leaf sits: k-means hierarchy and the road to 1000 qubits', 'Scaling');
  stat(s, 0.6, 1.5, 3.95, '10^301', 'plans for 500 antennas x 4 tilts (today: 4096)', C.gold);
  stat(s, 4.7, 1.5, 3.95, 'about 45 qubits', 'ceiling of exact statevector simulation (50 q = 18 PB)', C.gold);
  stat(s, 8.8, 1.5, 4.1, 'about 13,000 CX', 'one QAOA layer at 1000 qubits, still 2-local', C.gold);
  s.addImage({ path: img('charts/group_benchmark_depth.png'), x: 0.6, y: 3.05, w: 4.9, h: 2.82 });
  caption(s, 'Team benchmark, 48-region toy network: refinement 5 -> 21 groups. Cycle 3 (13 groups, 13 QAOA jobs) reaches 1.75 = 95% of the per-region ceiling 1.838 (48 jobs); one plan for all gives 1.379.', 0.6, 5.95, 5.4);
  bullets(s, [
    'Network -> 5 groups -> 25 -> 125: k-means on region feature vectors, one QAOA job per group, refine where the utility gain is worth it. Our 12-qubit problem is one job in that tree',
    'Best non-quantum tools at 1000 qubits: brute force 10^283 s at exascale; exact QUBO solvers run hours to days without certifying; annealing and tabu give a good plan in minutes with no guarantee (1.833 vs 1.838 on the toy benchmark). Nobody can simulate QAOA past about 48 qubits',
    'A real 1000-qubit gate-based machine: physical qubits exist (IBM Condor 1121, Atom Computing 1200), but 13,000 CX at 99.9% fidelity means about 13 errors per shot, so the run must be error-corrected (2,000 to 100,000 physical qubits; roadmaps 2028 to 2030)',
    'Once available: depth ~10^2 per layer, 10^4 shots x 20 iterations = seconds to minutes; the Wolfram hot start cuts the iterations. Same Qmod, Classiq synthesizes for the target; only the backend changes',
    'What carries over unchanged: the encoding proof, the 2-locality, the hot-start habit (train angles on a small exact instance, transfer to the large one)',
  ], { x: 6.2, y: 3.05, w: 6.7, h: 3.5, fontSize: 12 });
  s.addNotes('This slide keeps the team contribution visible: the hierarchy is theirs, the verified leaf is ours, and they compose. The 1000-qubit numbers come from the hackathon deck (slide 13 there).');
}

// ---------- 14. Deliverables ----------
{
  const s = base('Deliverables: everything is public and reproducible', 'Output');
  s.addImage({ path: img('animation/mantiq_pipeline_final_frame.png'), x: 0.6, y: 1.55, w: 6.2, h: 3.49 });
  caption(s, 'animation/mantiq_pipeline.mp4 (41 s): the MantiQ Factor pipeline animated with the real numbers of this case, built with matplotlib.', 0.6, 5.05, 6.3);
  s.addTable([
    [{ text: 'artifact', options: tblHead }, { text: 'where', options: tblHead }],
    [{ text: 'Concluded solution (MIT)', options: tblCell }, { text: 'github.com/zuwasi/mantiq-factor-antenna-tilt', options: { ...tblCell, color: C.cyan } }],
    [{ text: 'Classiq library demo (PR)', options: tblCell }, { text: 'applications/telecom/antenna_tilt_optimization in Classiq/classiq-library', options: { ...tblCell, color: C.cyan } }],
    [{ text: 'Hackathon repo and 5-min video', options: tblCell }, { text: 'github.com/zuwasi/quantum-headache-antenna-tilt, youtu.be/OSEtTWnRQhc', options: { ...tblCell, color: C.cyan } }],
    [{ text: 'Data', options: tblCell }, { text: 'data/opencellid_il2*.csv (OpenCelliD, CC BY-SA 4.0)', options: tblCell }],
    [{ text: 'Wolfram', options: tblCell }, { text: 'wolfram/*.wl, .nb, .pdf, .json (angles, probabilities)', options: tblCell }],
    [{ text: 'Lean 4', options: tblCell }, { text: 'lean/TiltQAOA.lean + build log', options: tblCell }],
    [{ text: 'Classiq', options: tblCell }, { text: 'notebook/*.ipynb, .qmod; classiq/results/*.json, *.qasm', options: tblCell }],
    [{ text: 'This deck', options: tblCell }, { text: 'presentation/build_deck.js (pptxgenjs) and the PPTX/PDF it builds', options: tblCell }],
  ], { x: 7.1, y: 1.55, w: 5.8, colW: [2.1, 3.7], rowH: 0.46, border: { type: 'solid', color: C.bg, pt: 1 }, fontSize: 11 });
  s.addNotes('Every row is a folder in the repo. The notebook is the classiq-library contribution; the rest is the evidence behind it.');
}

// ---------- 15. Lessons ----------
{
  const s = base('What the MantiQ Factor workflow bought us', 'Lessons');
  const lesson = (x, y, head, body) => {
    panel(s, x, y, 5.95, 1.5);
    s.addText([
      { text: head, options: { bold: true, color: C.gold, fontSize: 14, breakLine: true } },
      { text: body, options: { color: C.ink, fontSize: 12.5 } },
    ], { x: x + 0.12, y, w: 5.7, h: 1.5, fontFace: FONT, valign: 'middle', margin: 0.03 });
  };
  lesson(0.6, 1.6, 'Compute before you engineer', 'Wolfram found the angles exactly; the Classiq run confirmed them in one shot and COBYLA had nothing left to do. Blind starts on the simulator got stuck at 35.5 or reached only 7.0 after 20 jobs: shot noise hides the gradient.');
  lesson(6.9, 1.6, 'Prove the parts that fail silently', 'Encoding bijection, the true optimum, and the diagonal phase layer are where a QAOA demo can be wrong while still producing plausible histograms.');
  lesson(0.6, 3.3, 'Make the model decision explicit', 'The 2-qubit vs 5-qubit choice was argued with numbers (invalid mass, Pauli weight, team gain) and written down before code, so the team could veto it.');
  lesson(6.9, 3.3, 'Files between stages, not memory', 'JSON angles, Markdown Hamiltonian, Lean source and Qmod are the interfaces. Any stage can be rerun alone, and this deck was rebuilt from them.');
  lesson(0.6, 5.0, 'Real data raises the bar cheaply', 'Six OpenCelliD antennas cost nothing more than a toy grid to model, and the result (only the most overlapping antenna tilts) reads as physics, not as a puzzle.');
  lesson(6.9, 5.0, 'Agentic orchestration is the glue', 'Amp drove the converters, Mathematica kernel, Lean build and Classiq SDK from one thread with skills and knowledge bases; humans read numbers and decided.');
  s.addNotes('Close with the point that the workflow, not the 12-qubit result, is what transfers to the next problem.');
}

// ---------- 16. Thank you ----------
{
  const s = pptx.addSlide();
  numberSlide(s);
  s.background = { color: C.bg };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 7.25, w: 13.33, h: 0.25, fill: { color: C.gold } });
  s.addText('Thank you', { x: 0.8, y: 1.6, w: 11.5, h: 1.2, fontFace: FONT, fontSize: 54, bold: true, color: C.ink, margin: 0 });
  s.addText('MantiQ Factor: input, conversion, understand, compute, verify, engineer, output', { x: 0.8, y: 2.8, w: 11.5, h: 0.6, fontFace: FONT, fontSize: 20, color: C.muted, margin: 0 });
  s.addText([
    { text: 'Repository (MIT)   ', options: { color: C.muted } }, { text: 'github.com/zuwasi/mantiq-factor-antenna-tilt', options: { color: C.cyan, breakLine: true } },
    { text: 'Classiq library demo   ', options: { color: C.muted } }, { text: 'applications/telecom/antenna_tilt_optimization', options: { color: C.cyan, breakLine: true } },
    { text: 'Hackathon repo   ', options: { color: C.muted } }, { text: 'github.com/zuwasi/quantum-headache-antenna-tilt', options: { color: C.cyan, breakLine: true } },
    { text: 'Video   ', options: { color: C.muted } }, { text: 'youtu.be/OSEtTWnRQhc', options: { color: C.cyan, breakLine: true } },
    { text: 'Data   ', options: { color: C.muted } }, { text: 'OpenCelliD, CC BY-SA 4.0', options: { color: C.ink } },
  ], { x: 0.8, y: 3.7, w: 11.5, h: 2.3, fontFace: FONT, fontSize: 17, valign: 'top', margin: 0 });
  s.addText('Daniel Liezrowice  |  Team Quantum Headache  |  QUBIT 2026', { x: 0.8, y: 6.3, w: 9, h: 0.5, fontFace: FONT, fontSize: 15, color: C.muted, margin: 0 });
}

const out = path.join(R, 'presentation', 'MantiQ_Factor_Antenna_Tilt.pptx');
pptx.writeFile({ fileName: out }).then(() => console.log('wrote ' + out));
