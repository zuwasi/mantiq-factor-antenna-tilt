"""MantiQ Factor production line, animated on the antenna-tilt QAOA project.

Recreates the MantiQ Factor infographic (docs/MantiQ-v2.png) as a matplotlib scene and
animates a work token travelling through the seven stages. When a stage lights up, the
panel below shows what that stage produced in this project (real numbers from the
Wolfram, Lean 4 and Classiq runs).

Run:  py -3.12 mantiq_pipeline_animation.py            -> mantiq_pipeline.mp4 (+ .gif, + last frame .png)
      py -3.12 mantiq_pipeline_animation.py --preview  -> only writes mantiq_pipeline_preview.png (frames 0, mid, end)
"""
import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter
from matplotlib.patches import Circle, FancyArrow, FancyBboxPatch, Rectangle

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
FPS = 24
W, H = 16, 9  # inches at 120 dpi -> 1920 x 1080

BG = "#070b1c"
PANEL = "#0d1330"
GOLD = "#f2b632"
WHITE = "#f4f6fb"
GREY = "#9aa3bd"
STAGES = [
    ("1", "INPUT", "Research &\nDocuments", "#3b8bff"),
    ("2", "CONVERSION", "Structure &\nStandardize", "#2fd4d4"),
    ("3", "UNDERSTAND", "Reason & Extract\nKnowledge", "#7ed957"),
    ("4", "COMPUTE", "Model & Analyze", "#f2a13a"),
    ("5", "VERIFY", "Prove & Ensure\nCorrectness", "#a86bff"),
    ("6", "ENGINEER", "Synthesize &\nGenerate", "#6f7bff"),
    ("7", "OUTPUT", "Executable\nSystems", "#2fd4c4"),
]
TOOLS = [
    ("Amp", "AI reasoning &\norchestration"),
    ("Wolfram Mathematica", "computation &\nsymbolic intelligence"),
    ("Lean 4", "formal verification\n& proof"),
    ("Converters", "PDF, DOCX, LaTeX,\nMarkdown"),
    ("Skills", "domain expertise\n& agent skills"),
    ("Knowledge bases", "curated data\n& ontologies"),
]
# what each stage did in THIS project: (headline, bullet lines, thumbnail file or None)
DETAILS = [
    ("Hackathon brief + team write-ups",
     ["QUBIT 2026 challenge: antenna down-tilt for a cellular network",
      "team Hamiltonian PDF (16 pp), k-means / QAOA concept deck",
      "real tower positions: OpenCelliD, Tel Aviv, MCC 425 (CC BY-SA 4.0)"],
     "map_small.jpg"),
    ("PDF / PPTX / Google Slides  ->  Markdown + LaTeX",
     ["PDF text and figures extracted, formulas rewritten as LaTeX",
      "U(t) = alpha Q(t) - beta I(t) - gamma D(t)   ->   Cost(t) = -U(t)",
      "6 antennas x 4 tilt levels: coverage vector c, coupling matrix I"],
     None),
    ("Choose the model: 2 qubits per antenna, no penalties",
     ["tilt_i in {0,1,2,3} = QNum[2]  ->  12 qubits, 4096 plans, all valid",
      "Cost(t) = t^T I t - 1.5 c.t + 0.3 sum(t)  =  73 Pauli terms (1 I + 12 Z + 60 ZZ)",
      "rejected: 27 configs in 5 qubits (5 dead states, penalties, P(opt) ~ 1x uniform)"],
     None),
    ("Wolfram Mathematica: exact statevector, hot-start angles",
     ["classical optimum -2.844 at (0,3,0,0,0,0), unique",
      "QAOA p=1 (gamma, beta) = (0.0654, 1.1293):  <C> = 1.9985,  P(opt) = 27x uniform",
      "QAOA p=2:  <C> = -0.383,  P(cost<0) = 0.67;  shots for 95%: 12270 -> 453 -> 342"],
     "landscape.png"),
    ("Lean 4 + Mathlib certificates, 0 sorry",
     ["costS optTilt = -2.844   and   forall t, -2.844 <= costS t",
      "costS t = -2.844  ->  t = optTilt   (uniqueness)",
      "decodeTilt bijective;  |exp(i gamma C)| = 1 (phase layer preserves probability)"],
     None),
    ("Classiq Qmod: phase(Cost, gamma) + RX mixer",
     ["class TiltVars(QStruct): tilts: QArray[QNum[2], 6]",
      "phase(tilt_cost(t), gamma); apply_to_all(RX(beta))   x p layers",
      "synthesised p=1: depth 59, 92 CX, 72 RZ;  p=2: depth 114, 184 CX"],
     "circuit_stats.png"),
    ("Executable notebook + Classiq run, matches the prediction",
     ["Classiq simulator, 4096 shots:  <C> = 2.020 vs 1.9985 predicted,  P(cost<0) = 0.529 vs 0.53",
      "best sample = exact optimum;  COBYLA refinement inside an ExecutionSession",
      "deliverables: classiq-library notebook, MIT repo, deck, demo video"],
     "wolfram_vs_classiq.png"),
]
LANGS = ["C / C++", "Python", "Rust", "VHDL", "Verilog", "SystemVerilog", "QASM", "Classiq"]

# ------------------------------------------------------------------ timeline (seconds)
T_INTRO = 2.0          # header + tool bar fade in
T_STAGE = 5.0          # per stage
T_OUTRO = 4.0
TOTAL = T_INTRO + 7 * T_STAGE + T_OUTRO
N_FRAMES = int(TOTAL * FPS)


def stage_progress(t):
    """-> (active stage index or None, progress 0..1 inside the stage)."""
    if t < T_INTRO:
        return None, 0.0
    k = int((t - T_INTRO) // T_STAGE)
    if k >= 7:
        return 7, min(1.0, (t - T_INTRO - 7 * T_STAGE) / T_OUTRO)
    return k, ((t - T_INTRO) % T_STAGE) / T_STAGE


def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


# ------------------------------------------------------------------ static scene
def build_scene(ax):
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0), W, H, color=BG, zorder=0))
    # header
    ax.add_patch(FancyBboxPatch((0.55, 7.75), 0.75, 0.9, boxstyle="round,pad=0.02", fc="none", ec=GOLD, lw=4, zorder=2))
    ax.text(0.925, 8.2, "Q", ha="center", va="center", fontsize=30, color=WHITE, weight="bold", zorder=3)
    ax.text(1.55, 8.42, "MantiQ", fontsize=34, color=WHITE, weight="bold", va="center")
    ax.text(3.6, 8.42, "Factor", fontsize=34, color=GOLD, weight="bold", va="center")
    ax.text(1.57, 7.9, "From research knowledge to formally verified executable systems", fontsize=13, color=GREY, va="center")
    ax.plot([0.55, 15.45], [7.55, 7.55], color=GOLD, lw=1, alpha=0.6)
    # tools bar
    ax.add_patch(FancyBboxPatch((0.55, 6.55), 14.9, 0.85, boxstyle="round,pad=0.02", fc=PANEL, ec="#243055", lw=1.2, zorder=1))
    xs = [0.75, 3.2, 5.75, 8.05, 10.55, 12.95]
    for (name, sub), x in zip(TOOLS, xs):
        ax.text(x, 7.2, name, fontsize=12, color=WHITE, weight="bold", va="center")
        ax.text(x, 6.83, sub, fontsize=8.5, color=GREY, va="center", linespacing=1.1)
    # footer: three pillars
    ax.add_patch(FancyBboxPatch((0.55, 0.95), 14.9, 0.95, boxstyle="round,pad=0.02", fc=PANEL, ec="#243055", lw=1.2, zorder=1))
    pillars = [("Intelligent orchestration", "Amp agents coordinate the pipeline, pick tools,\nkeep context across steps"),
               ("Knowledge & skills layer", "domain skills (Classiq, Wolfram, Lean 4, pptx)\naccelerate understanding and quality"),
               ("Trust & traceability", "every number below is reproducible from the repo\nand cross-checked between two engines")]
    for (h, s), x in zip(pillars, [0.85, 5.9, 10.95]):
        ax.text(x, 1.62, h, fontsize=12, color=WHITE, weight="bold", va="center")
        ax.text(x, 1.22, s, fontsize=8.5, color=GREY, va="center", linespacing=1.15)
    # footer: languages
    ax.text(0.85, 0.45, "FORMALLY VERIFIED EXECUTABLE SYSTEMS", fontsize=11, color="#2fd4d4", weight="bold", va="center")
    for i, lang in enumerate(LANGS):
        ax.text(5.5 + i * 1.2, 0.45, lang, fontsize=9.5, color=WHITE, va="center", ha="center")
    ax.text(15.35, 0.45, "...and more", fontsize=8.5, color=GREY, va="center", ha="right")


class Scene:
    def __init__(self):
        self.fig = plt.figure(figsize=(W, H), dpi=120)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        build_scene(self.ax)
        self.thumbs = {}
        for _, _, f in DETAILS:
            if f and (ASSETS / f).exists():
                self.thumbs[f] = mpimg.imread(ASSETS / f)
        # stage boxes
        self.box_w, self.gap, self.box_y, self.box_h = 1.85, 0.32, 3.75, 2.4
        self.x0 = (W - (7 * self.box_w + 6 * self.gap)) / 2
        self.boxes, self.circles, self.titles, self.subs, self.arrows = [], [], [], [], []
        for i, (num, title, sub, col) in enumerate(STAGES):
            x = self.x0 + i * (self.box_w + self.gap)
            b = FancyBboxPatch((x, self.box_y), self.box_w, self.box_h, boxstyle="round,pad=0.02",
                               fc=PANEL, ec=matplotlib.colors.to_rgba(col, 0.55), lw=1.5, zorder=2)
            self.ax.add_patch(b)
            c = Circle((x + self.box_w / 2, self.box_y + self.box_h + 0.02), 0.28, fc=BG, ec=col, lw=2.5, zorder=4, alpha=0.55)
            self.ax.add_patch(c)
            self.ax.text(x + self.box_w / 2, self.box_y + self.box_h + 0.02, num, ha="center", va="center", fontsize=15, color=WHITE, weight="bold", zorder=5)
            t = self.ax.text(x + self.box_w / 2, self.box_y + self.box_h - 0.45, title, ha="center", va="center", fontsize=12.5, color=WHITE, weight="bold", alpha=0.55, zorder=3)
            s = self.ax.text(x + self.box_w / 2, self.box_y + 0.55, sub, ha="center", va="center", fontsize=10, color=GREY, alpha=0.55, zorder=3, linespacing=1.15)
            self.ax.plot([x + 0.55, x + self.box_w - 0.55], [self.box_y + 0.2, self.box_y + 0.2], color=col, lw=2.5, alpha=0.5)
            self.boxes.append(b); self.circles.append(c); self.titles.append(t); self.subs.append(s)
            if i < 6:
                a = FancyArrow(x + self.box_w + 0.05, self.box_y + self.box_h / 2 + 0.3, 0.18, 0, width=0.12, head_width=0.3, head_length=0.1, color="#3a4670", zorder=3)
                self.ax.add_patch(a)
                self.arrows.append(a)
        # moving token
        self.token = Circle((self.x0 - 0.5, self.box_y + self.box_h / 2 + 0.3), 0.14, fc=GOLD, ec=WHITE, lw=1.5, zorder=8)
        self.glow = Circle((self.x0 - 0.5, self.box_y + self.box_h / 2 + 0.3), 0.3, fc=GOLD, alpha=0.25, zorder=7)
        self.ax.add_patch(self.glow); self.ax.add_patch(self.token)
        # detail panel
        self.panel = FancyBboxPatch((0.55, 2.05), 14.9, 1.28, boxstyle="round,pad=0.02", fc="#0a1028", ec="#243055", lw=1.2, zorder=1)
        self.ax.add_patch(self.panel)
        self.d_head = self.ax.text(0.8, 3.1, "", fontsize=13.5, color=GOLD, weight="bold", va="center", zorder=3)
        self.d_lines = [self.ax.text(0.8, 2.78 - k * 0.3, "", fontsize=10.5, color=WHITE, va="center", family="monospace", zorder=3) for k in range(3)]
        self.thumb_ax = self.fig.add_axes([0.745, 0.235, 0.20, 0.135])
        self.thumb_ax.axis("off")
        self.thumb_img = None
        self.label = self.ax.text(W / 2, 3.52, "The MantiQ Factor production line, applied to: QAOA antenna-tilt optimisation (12 qubits, real Tel Aviv towers)",
                                  ha="center", va="center", fontsize=11.5, color=GOLD, zorder=3)
        self.progress = Rectangle((0.55, 0.02), 0.0, 0.06, color=GOLD, zorder=9)
        self.ax.add_patch(self.progress)
        self.clock = self.ax.text(15.45, 0.13, "", ha="right", va="bottom", fontsize=8, color=GREY, zorder=9)

    def set_stage_alpha(self, i, a):
        col = STAGES[i][3]
        self.boxes[i].set_linewidth(1.5 + 2.5 * a)
        self.boxes[i].set_edgecolor(matplotlib.colors.to_rgba(col, 0.55 + 0.45 * a))
        base = matplotlib.colors.to_rgba(PANEL)
        tint = matplotlib.colors.to_rgba(col)
        self.boxes[i].set_facecolor(tuple(base[j] * (1 - 0.22 * a) + tint[j] * 0.22 * a for j in range(3)) + (1.0,))
        self.subs[i].set_color(WHITE if a > 0.5 else GREY)
        self.circles[i].set_alpha(0.55 + 0.45 * a)
        self.titles[i].set_alpha(0.55 + 0.45 * a)
        self.subs[i].set_alpha(0.55 + 0.45 * a)

    def show_detail(self, i, prog):
        head, lines, thumb = DETAILS[i]
        self.d_head.set_text(head)
        self.d_head.set_color(STAGES[i][3])
        # type the three lines in one after the other
        for k, tx in enumerate(self.d_lines):
            start, span = 0.08 + k * 0.22, 0.22
            frac = ease((prog - start) / span)
            tx.set_text(lines[k][: int(len(lines[k]) * frac)])
        if thumb and thumb in self.thumbs:
            if self.thumb_img is None or self.thumb_img.get_label() != thumb:
                self.thumb_ax.clear(); self.thumb_ax.axis("off")
                self.thumb_img = self.thumb_ax.imshow(self.thumbs[thumb], aspect="auto", label=thumb)
            self.thumb_img.set_alpha(ease((prog - 0.05) / 0.3))
        else:
            if self.thumb_img is not None:
                self.thumb_ax.clear(); self.thumb_ax.axis("off"); self.thumb_img = None

    def update(self, frame):
        t = frame / FPS
        k, prog = stage_progress(t)
        self.progress.set_width(14.9 * t / TOTAL)
        self.clock.set_text(f"{t:4.1f} s")
        cy = self.box_y + self.box_h / 2 + 0.3
        if k is None:  # intro: token waits at the left
            for i in range(7):
                self.set_stage_alpha(i, 0.0)
            self.token.center = (self.x0 - 0.5, cy); self.glow.center = self.token.center
            self.d_head.set_text("")
            for tx in self.d_lines:
                tx.set_text("")
            return
        if k == 7:  # outro: everything lit, summary
            for i in range(7):
                self.set_stage_alpha(i, 1.0)
            self.token.center = (self.x0 + 7 * self.box_w + 6 * self.gap + 0.3, cy); self.glow.center = self.token.center
            self.d_head.set_text("Result: one traceable chain from the brief to a verified, running quantum program")
            self.d_head.set_color(GOLD)
            summary = ["Wolfram prediction  <C> = 1.9985 | P(cost<0) = 0.53 | P(opt) = 27x uniform      Classiq 4096 shots  2.020 | 0.529 | best sample = optimum",
                       "Lean 4: optimum value, lower bound, uniqueness, encoding bijection, phase unitarity  (0 sorry)   |   circuit p=1 depth 59, 92 CX",
                       "github.com/zuwasi/mantiq-factor-antenna-tilt   |   Classiq library: applications/telecom/antenna_tilt_optimization"]
            for k2, tx in enumerate(self.d_lines):
                frac = ease((prog - 0.1 * k2) / 0.35)
                tx.set_text(summary[k2][: int(len(summary[k2]) * frac)])
            if self.thumb_img is not None:
                self.thumb_ax.clear(); self.thumb_ax.axis("off"); self.thumb_img = None
            return
        # normal stage: earlier stages fully lit, current one fades in, token slides in during first 20 %
        for i in range(7):
            self.set_stage_alpha(i, 1.0 if i < k else (ease(prog / 0.2) if i == k else 0.0))
        x_prev = self.x0 - 0.5 if k == 0 else self.x0 + (k - 1) * (self.box_w + self.gap) + self.box_w / 2
        x_cur = self.x0 + k * (self.box_w + self.gap) + self.box_w / 2
        x = x_prev + (x_cur - x_prev) * ease(prog / 0.2)
        bob = 0.05 * __import__("math").sin(t * 6)
        self.token.center = (x, cy + bob); self.glow.center = self.token.center
        self.glow.set_radius(0.28 + 0.06 * __import__("math").sin(t * 8))
        self.show_detail(k, prog)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", action="store_true")
    ap.add_argument("--no-gif", action="store_true")
    args = ap.parse_args()
    sc = Scene()
    if args.preview:
        for name, fr in [("intro", int(1.0 * FPS)), ("stage4", int((T_INTRO + 3.7 * T_STAGE) * FPS)), ("end", N_FRAMES - 1)]:
            sc.update(fr)
            sc.fig.savefig(HERE / f"mantiq_pipeline_preview_{name}.png")
        print("previews written")
        return
    anim = FuncAnimation(sc.fig, sc.update, frames=N_FRAMES, interval=1000 / FPS)
    mp4 = HERE / "mantiq_pipeline.mp4"
    anim.save(mp4, writer=FFMpegWriter(fps=FPS, bitrate=4000, codec="libx264", extra_args=["-pix_fmt", "yuv420p"]))
    print("written", mp4, f"{TOTAL:.0f} s, {N_FRAMES} frames")
    sc.update(N_FRAMES - 1)
    sc.fig.savefig(HERE / "mantiq_pipeline_final_frame.png")
    if not args.no_gif:
        sc2 = Scene()
        sc2.fig.set_dpi(60)
        anim2 = FuncAnimation(sc2.fig, sc2.update, frames=range(0, N_FRAMES, 3), interval=3000 / FPS)
        gif = HERE / "mantiq_pipeline.gif"
        anim2.save(gif, writer=PillowWriter(fps=FPS // 3))
        print("written", gif)


if __name__ == "__main__":
    main()
