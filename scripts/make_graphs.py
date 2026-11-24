#!/usr/bin/env python3
"""make_graphs.py - draw every graph of the report from data/all_stats.csv (and data/part6_candidates.csv).

Usage:  python3 scripts/extract_stats.py && python3 scripts/make_graphs.py
Output: graphs/*.png
Colour rule used everywhere: anagram = blue circle, go = orange square (same in every graph).
"""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, FixedLocator

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data", "all_stats.csv")
P6 = os.path.join(ROOT, "data", "part6_candidates.csv")
OUT = os.path.join(ROOT, "graphs")
os.makedirs(OUT, exist_ok=True)

BENCH = ["anagram", "go"]
COL = {"anagram": "#2a78d6", "go": "#eb6834"}
MK = {"anagram": "o", "go": "s"}
INK, INK2, GRID = "#0b0b0b", "#52514e", "#e4e3df"

plt.rcParams.update({
    "figure.dpi": 100, "savefig.dpi": 200, "figure.facecolor": "white", "axes.facecolor": "white",
    "font.family": "DejaVu Sans", "font.size": 10, "text.color": INK, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.edgecolor": "#bdbcb6", "axes.titlesize": 12,
    "axes.titleweight": "bold", "axes.titlelocation": "left", "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8,
    "axes.axisbelow": True, "legend.frameon": False, "legend.fontsize": 9,
})

def load():
    rows = {}
    with open(DATA) as f:
        for r in csv.DictReader(f):
            for k, v in list(r.items()):
                try:
                    r[k] = float(v)
                except (ValueError, TypeError):
                    pass
            rows[(r["bench"], r["part"], r["label"])] = r
    return rows

R = load()
def g(b, p, l, k):
    return R[(b, p, l)][k]

def save(fig, name):
    place_labels(fig)
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)
    print("saved", name)

def mark_default(ax, x, text="default", y=0.02):
    ax.axvline(x, color="#8a8983", ls=":", lw=1.2, zorder=1)
    ax.text(x, y, text + " ", transform=ax.get_xaxis_transform(), color=INK2, fontsize=8.5, va="bottom", ha="right", rotation=90,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0, alpha=0.85), zorder=2)

def log2_axis(ax, xs, fmt=lambda v: f"{v:g}"):
    ax.set_xscale("log", base=2)
    ax.xaxis.set_major_locator(FixedLocator(xs))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(v)))
    ax.minorticks_off()

def line(ax, xs, ys, b, label=None, ls="-", fmt="{:.2f}", dy=7, fill=True):
    ax.plot(xs, ys, color=COL[b], marker=MK[b], ls=ls, lw=2, ms=7, label=label or b,
            markerfacecolor=COL[b] if fill else "white", markeredgecolor=COL[b], markeredgewidth=1.8, zorder=3)
    L = ax.__dict__.setdefault("_lbls", [])
    for x, y in zip(xs, ys):
        L.append((x, y, fmt.format(y)))

def place_labels(fig):
    """Put every data label where it does not cover another label or a marker."""
    from matplotlib.transforms import Bbox
    for ax in fig.axes:                       # a little head-room so labels are never clipped
        if getattr(ax, "_lbls", None) and ax.get_yscale() == "linear":
            lo, hi = ax.get_ylim(); pad = 0.07 * (hi - lo)
            ax.set_ylim(lo if lo == 0 else lo - pad, hi + pad)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for ax in fig.axes:
        L = getattr(ax, "_lbls", [])
        if not L:
            continue
        pts = [ax.transData.transform((x, y)) for x, y, _ in L]
        marks = [Bbox.from_extents(px - 8, py - 8, px + 8, py + 8) for px, py in pts]
        placed = []
        for (x, y, t) in L:
            a = None
            for off in [(0, 9), (0, -16), (17, 3), (-17, 3), (0, 22), (0, -29), (24, -10), (-24, -10), (0, 35), (0, -42)]:
                if a is not None:
                    a.remove()
                a = ax.annotate(t, (x, y), textcoords="offset points", xytext=off, ha="center", fontsize=8, color=INK2)
                bb = a.get_window_extent(r)
                axbb = ax.get_window_extent(r)
                inside = bb.x0 >= axbb.x0 - 2 and bb.x1 <= axbb.x1 + 2 and bb.y0 >= axbb.y0 + 1 and bb.y1 <= axbb.y1 - 1
                if inside and not any(bb.overlaps(o) for o in placed) and not any(bb.overlaps(m) for m in marks):
                    break
            placed.append(a.get_window_extent(r))

# ---------------------------------------------------------------- Part 1
def part1():
    fig, ax = plt.subplots(figsize=(7.2, 3.1))
    keys = [("load_pct", "Loads", "#2a78d6"), ("store_pct", "Stores", "#eb6834"),
            ("branch_pct", "Branches", "#1baf7a"), ("other_pct", "Other (ALU etc.)", "#c9c8c2")]
    ys = list(range(len(BENCH)))[::-1]
    for b, y in zip(BENCH, ys):
        left = 0
        for k, name, c in keys:
            v = g(b, "P1", "default", k)
            ax.barh(y, v, left=left, color=c, edgecolor="white", linewidth=2, height=0.55, label=name if y == ys[0] else None)
            ax.text(left + v / 2, y, f"{v:.1f}%", ha="center", va="center", fontsize=9, color="white" if c != "#c9c8c2" else INK, fontweight="bold")
            left += v
    ax.set_yticks(ys); ax.set_yticklabels(BENCH, fontsize=11)
    ax.set_xlim(0, 100); ax.set_xlabel("Share of committed instructions (%)")
    ax.set_title("Part 1: Instruction mix of the two benchmarks")
    ax.grid(axis="y", visible=False)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.22))
    save(fig, "g1_instruction_mix.png")

# ---------------------------------------------------------------- Part 2
def part2():
    W = [1, 2, 4, 8]
    fig, ax = plt.subplots(figsize=(7.2, 5.0))
    for b in BENCH:
        line(ax, W, [g(b, "P2", f"w{w}.ooo", "sim_IPC") for w in W], b, f"{b}, out-of-order", "-", dy=7)
        line(ax, W, [g(b, "P2", f"w{w}.inorder", "sim_IPC") for w in W], b, f"{b}, in-order", "--", dy=-13, fill=False)
    log2_axis(ax, W)
    mark_default(ax, 4, "default width")
    ax.set_xlabel("Machine width W (instructions per cycle, log₂ scale)")
    ax.set_ylabel("IPC (instructions per cycle)")
    ax.set_ylim(0, None)
    ax.set_title("Part 2: IPC vs machine width, in-order vs out-of-order")
    ax.legend(loc="upper left", ncol=1)
    save(fig, "g2a_ipc_vs_width.png")

    fig, ax = plt.subplots(figsize=(7.2, 3.9))
    for b in BENCH:
        sp = [g(b, "P2", f"w{w}.inorder", "sim_cycle") / g(b, "P2", f"w{w}.ooo", "sim_cycle") for w in W]
        line(ax, W, sp, b, b, fmt="{:.2f}×", dy=8)
    ax.axhline(1, color="#8a8983", lw=1, ls=":")
    log2_axis(ax, W); mark_default(ax, 4, "default width")
    ax.set_xlabel("Machine width W (instructions per cycle, log₂ scale)")
    ax.set_ylabel("Speedup of out-of-order over in-order\n(cycles in-order ÷ cycles out-of-order)")
    ax.set_ylim(0.8, None)
    ax.set_title("Part 2: Speedup of out-of-order issue vs machine width")
    ax.legend(loc="upper left")
    save(fig, "g2b_speedup.png")

# ---------------------------------------------------------------- Part 3
def part3():
    RUU = [4, 8, 16, 32, 64, 128]
    fig, ax = plt.subplots(figsize=(7.2, 4.0))
    for b in BENCH:
        line(ax, RUU, [g(b, "P3", f"ruu{r}", "sim_IPC") for r in RUU], b, dy=8)
    log2_axis(ax, RUU); mark_default(ax, 16, "default RUU = 16")
    ax.set_xlabel("RUU size (entries, log₂ scale; LSQ = RUU ÷ 2)")
    ax.set_ylabel("IPC (instructions per cycle)")
    ax.set_ylim(0, None)
    ax.set_title("Part 3: IPC vs RUU (instruction window) size")
    ax.legend(loc="lower right")
    save(fig, "g3a_ipc_vs_ruu.png")

    fig, axs = plt.subplots(1, 2, figsize=(9.2, 4.0))
    for b in BENCH:
        line(axs[0], RUU, [g(b, "P3", f"ruu{r}", "ruu_occupancy") for r in RUU], b, fmt="{:.1f}", dy=7)
        line(axs[1], RUU, [100 * g(b, "P3", f"ruu{r}", "ruu_full") for r in RUU], b, fmt="{:.0f}%", dy=7)
    axs[0].plot(RUU, RUU, color="#8a8983", lw=1, ls=(0, (1, 3)), label="RUU size (full)")
    for ax in axs:
        log2_axis(ax, RUU); mark_default(ax, 16, "default")
        ax.set_xlabel("RUU size (entries, log₂ scale)")
    axs[0].set_ylabel("Average RUU occupancy (entries)")
    axs[0].set_yscale("log", base=2); axs[0].yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    axs[1].set_ylabel("Cycles with a full RUU (%)")
    axs[0].set_title("Average RUU occupancy"); axs[1].set_title("Fraction of time the RUU was full")
    axs[0].legend(loc="upper left")
    fig.suptitle("Part 3: RUU occupancy vs RUU size", x=0.01, ha="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    save(fig, "g3b_ruu_occupancy.png")

# ---------------------------------------------------------------- Part 4
def two_panel(name, title, xs, labels, part, xlabel, default_x, xticklabels=None):
    fig, axs = plt.subplots(1, 2, figsize=(9.2, 4.0))
    for b in BENCH:
        line(axs[0], xs, [100 * g(b, part, l, "dl1.miss_rate") for l in labels], b, fmt="{:.2f}%", dy=7)
        line(axs[1], xs, [g(b, part, l, "sim_IPC") for l in labels], b, fmt="{:.2f}", dy=7)
    for ax in axs:
        log2_axis(ax, xs, (lambda v: xticklabels[xs.index(int(round(v)))]) if xticklabels else (lambda v: f"{v:g}"))
        mark_default(ax, default_x, "default")
        ax.set_xlabel(xlabel)
    axs[0].set_ylabel("L1 data-cache miss rate (%)"); axs[0].set_ylim(0, None)
    axs[1].set_ylabel("IPC (instructions per cycle)"); axs[1].set_ylim(0, None)
    axs[0].set_title("Miss rate (dl1.miss_rate)"); axs[1].set_title("IPC")
    axs[0].legend(loc="upper right")
    fig.suptitle(title, x=0.01, ha="left", fontweight="bold", fontsize=12)
    fig.tight_layout()
    save(fig, name)

def part4():
    caps = [1, 4, 16, 64]
    two_panel("g4a_dl1_capacity.png", "Part 4(a): L1 data-cache capacity (4-way, 32 B blocks)", caps,
              [f"dl1_{c}KB" for c in caps], "P4a", "L1 data-cache capacity (KB, log₂ scale)", 16)
    blks = [8, 16, 32, 64]
    two_panel("g4b_dl1_block.png", "Part 4(b): L1 data-cache block size (16 KB, 4-way)", blks,
              [f"blk{b}" for b in blks], "P4b", "L1 block size (bytes, log₂ scale)", 32)
    lat = [25, 50, 100, 200]
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for b in BENCH:
        line(ax, lat, [g(b, "P4c", f"mem{l}_L2", "sim_CPI") for l in lat], b, f"{b}, with L2", "-", dy=7)
        line(ax, lat, [g(b, "P4c", f"mem{l}_noL2", "sim_CPI") for l in lat], b, f"{b}, without L2", "--", dy=-13, fill=False)
    log2_axis(ax, lat)
    ax.set_xlabel("Main-memory latency (cycles to first word, log₂ scale; default is 18)")
    ax.set_ylabel("CPI (cycles per instruction, log\u2082 scale)")
    ax.set_yscale("log", base=2)
    ax.yaxis.set_major_locator(FixedLocator([0.5, 1, 2, 4, 8, 16]))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:g}"))
    ax.set_ylim(0.38, 24)
    ax.set_title("Part 4(c): CPI vs main-memory latency, with and without L2")
    ax.legend(loc="upper left")
    save(fig, "g4c_cpi_vs_memlat.png")

# ---------------------------------------------------------------- Part 5
PRED = [("nottaken", "Static\nnot-taken"), ("bimod512", "Bimodal\n512"), ("bimod2048", "Bimodal 2048\n(default)"),
        ("2lev", "Two-level\n(GAg)"), ("comb", "Combined")]
def part5():
    x = list(range(len(PRED))); w = 0.36
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for i, b in enumerate(BENCH):
        vals = [100 * g(b, "P5", p, "bpred_dir_rate") for p, _ in PRED]
        bars = ax.bar([xi + (i - 0.5) * w for xi in x], vals, w - 0.03, color=COL[b], label=b, edgecolor="white", linewidth=2)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.8, f"{v:.1f}", ha="center", fontsize=8, color=INK2)
    ax.axhline(100, color="#8a8983", lw=1, ls=":"); ax.text(-0.45, 100.8, "perfect = 100%", ha="left", fontsize=8.5, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in PRED], fontsize=9)
    ax.set_ylabel("Direction-prediction accuracy (%)"); ax.set_ylim(0, 112)
    ax.set_title("Part 5: Branch-direction accuracy per predictor")
    ax.grid(axis="x", visible=False); ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.78))
    save(fig, "g5a_bpred_accuracy.png")

    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    for i, b in enumerate(BENCH):
        perf = g(b, "P5", "perfect", "sim_IPC")
        vals = [g(b, "P5", p, "sim_IPC") / perf for p, _ in PRED]
        bars = ax.bar([xi + (i - 0.5) * w for xi in x], vals, w - 0.03, color=COL[b], label=b, edgecolor="white", linewidth=2)
        for bar, v in zip(bars, vals):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 0.012, f"{v:.2f}", ha="center", fontsize=8, color=INK2)
    ax.axhline(1, color="#8a8983", lw=1, ls=":"); ax.text(len(PRED) - 0.5, 1.012, "perfect predictor = 1.00", ha="right", fontsize=8.5, color=INK2)
    ax.set_xticks(x); ax.set_xticklabels([n for _, n in PRED], fontsize=9)
    ax.set_ylabel("IPC relative to the perfect predictor"); ax.set_ylim(0, 1.12)
    ax.set_title("Part 5: IPC per predictor, normalised to perfect prediction")
    ax.grid(axis="x", visible=False); ax.legend(loc="upper left", bbox_to_anchor=(0.0, 0.8))
    save(fig, "g5b_ipc_normalised.png")

# ---------------------------------------------------------------- Part 6
def part6():
    if not os.path.exists(P6):
        print("no part6_candidates.csv yet - skipping Part 6 graph"); return
    from matplotlib.lines import Line2D
    rows = list(csv.DictReader(open(P6)))
    fig, ax = plt.subplots(figsize=(7.8, 5.0))
    xs = [float(r["cost"]) for r in rows]; ys = [float(r["geomean_ipc"]) for r in rows]
    for r, x, y in zip(rows, xs, ys):
        is_def = r["name"].lower().startswith("default"); is_best = r.get("final") == "1"
        ax.scatter([x], [y], s=70 if not is_best else 170, color="#eb6834" if is_def else "#2a78d6",
                   marker="s" if is_def else ("*" if is_best else "o"), edgecolor="white", linewidth=1.5, zorder=3)
    # labels: the three designs at cost 97-98 get a spaced label column with leader lines; the others get a normal label
    crowd = sorted([(y, r, x) for r, x, y in zip(rows, xs, ys) if x >= 97], key=lambda t: t[0])
    for i, (y, r, x) in enumerate(crowd):
        ty = 1.835 + i * 0.05
        ax.annotate("", xy=(x, y), xytext=(95.3, ty), arrowprops=dict(arrowstyle="-", color="#bdbcb6", lw=0.8), zorder=2)
        ax.text(95.2, ty, f"{r['name']}  ({y:.3f})", ha="right", va="center", fontsize=8.2, color=INK,
                fontweight="bold" if r.get("final") == "1" else "normal")
    off = {"default": (8, -14), "g1_best": (8, -4), "g2_best": (8, 8)}
    for r, x, y in zip(rows, xs, ys):
        if x >= 97: continue
        dx, dy = off.get(r["name"], (8, 8))
        ax.annotate(f"{r['name']}  ({y:.3f})", (x, y), textcoords="offset points", xytext=(dx, dy), fontsize=8.5, color=INK,
                    ha="right" if dx < 0 else "left")
    ax.axvline(100, color="#d03b3b", lw=1.2, ls="--")
    ax.set_xlim(75, 101); ax.set_ylim(1.28, 2.06)
    ax.set_xlabel("Hardware cost (cost units, budget = 100)"); ax.set_ylabel("Geometric-mean IPC (anagram, go)")
    ax.set_title("Part 6: Candidate designs, cost vs performance")
    ax.legend(handles=[Line2D([], [], marker="s", color="w", markerfacecolor="#eb6834", markersize=9, label="Default design"),
                       Line2D([], [], marker="o", color="w", markerfacecolor="#2a78d6", markersize=9, label="Candidate"),
                       Line2D([], [], marker="*", color="w", markerfacecolor="#2a78d6", markersize=15, label="Final design"),
                       Line2D([], [], color="#d03b3b", ls="--", label="Budget (100)")], loc="lower left", fontsize=8.5)
    save(fig, "g6_cost_vs_ipc.png")

if __name__ == "__main__":
    for fn in (part1, part2, part3, part4, part5, part6):
        try:
            fn()
        except KeyError as e:
            print(f"{fn.__name__}: missing data {e} - run that part first")
