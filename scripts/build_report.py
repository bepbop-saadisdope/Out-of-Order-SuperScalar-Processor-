#!/usr/bin/env python3
"""build_report.py - build the Word report (report/Project_Report_G13.docx) from data/all_stats.csv and graphs/*.png.
All numbers in the text are read from the CSV, so the report always matches the raw outputs.
Group 13: benchmarks anagram and go.   Usage: python3 scripts/build_report.py
"""
import csv, json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from report_lib import *
from docx.shared import Cm

load_data()
OUTDIR = os.path.join(ROOT, "report"); os.makedirs(OUTDIR, exist_ok=True)
B = ["anagram", "go"]
GROUP = 13

def f2(x): return f"{x:.2f}"
def f3(x): return f"{x:.3f}"
def f1(x): return f"{x:.1f}"
def p1(x): return f"{x:.1f}%"
def p2(x): return f"{x:.2f}%"
def n0(x): return f"{x:,.0f}"

# ============================================================================ cover + setup
def cover(d):
    para(d, "FAST – National University of Computer and Emerging Sciences, Lahore", bold=True, size=13, align="center", after=2)
    para(d, "Computer Architecture – BCS-5F (Fall 2026)", size=12, align="center", after=18)
    para(d, "Project Report", bold=True, size=24, align="center", after=4, color="1F3864")
    para(d, "Design-Space Exploration of an Out-of-Order Superscalar Processor using sim-outorder", size=14, align="center", after=22)
    t = table(d, ["Item", "Details"], [
        ["Group number", str(GROUP)],
        ["Assigned benchmarks", f"anagram and go   [({GROUP} − 1) mod 6 = 0]"],
        ["Simulator", "SimpleScalar 3.0, PISA target, sim-outorder"],
        ["Instruction cap", "100 million instructions per run in Parts 2 to 6 (Part 1 runs to completion)"],
    ], [4.2, 12.2], align_right_from=9, font=10.5)
    para(d, "")
    para(d, "Group members", bold=True, size=12, after=3)
    m = table(d, ["No.", "Name", "Roll number"], [["1", "", ""], ["2", "", ""], ["3", "", ""]], [1.6, 9.6, 5.2], align_right_from=9, font=11)
    for row in m.rows[1:]:
        row.height = Cm(1.0)
    para(d, "")
    para(d, "How to read this report", bold=True, size=12, after=3)
    para(d, "Every part has the same layout: what we ran, a table or graph of the results, and a short interpretation. "
            "In every graph the two benchmarks have the same look: anagram is a blue circle and go is an orange square. "
            "A dotted vertical line marks the default configuration. All numbers come from the raw output files in the "
            "results folder of our submission. We change one hardware setting at a time and keep everything else at the default.")

def setup_section(d):
    d.add_heading("Setup used for all experiments", 1)
    para(d, "We built SimpleScalar 3.0 for the PISA target and used the little-endian SPEC95 binaries from the "
            "BenchMarks_Little folder. Every run starts from a copy of the Input folder with an empty environment (env -i) so that the "
            "simulator does not stop with the environment overflow error. The default hardware (from -dumpconfig) is: "
            "4-wide fetch/decode/issue/commit, 4 integer ALUs, 2 memory ports, 16-entry RUU, 8-entry LSQ, 16 KB direct-mapped "
            "L1 instruction cache, 16 KB 4-way L1 data cache, 256 KB 4-way unified L2, memory latency 18 cycles, and a "
            "2048-entry bimodal branch predictor.")
    code(d, "env -i $SIM -max:inst 100000000 [options] -redir:sim <bench>.<part>.<label>.txt ../Programs/anagram.ss words < anagram.in > anagram.out\n"
            "env -i $SIM -max:inst 100000000 [options] -redir:sim <bench>.<part>.<label>.txt ../Programs/go.ss 50 9 2stone9.in < /dev/null")
    para(d, "The batch scripts, the .cfg file of every run, the raw output files and the CSV with all statistics are in the "
            "submission zip. The two benchmarks behave differently, which is why we use them: **anagram** is a small dictionary "
            "search with simple loops, and **go** is a game-playing program with a large amount of code and many hard-to-predict branches.")

# ============================================================================ Part 1
def part1(d):
    d.add_heading("Part 1: Baseline and verification", 1)
    d.add_heading("(a) Correct output", 2)
    para(d, "We ran both benchmarks to completion with the default configuration (no -max:inst) and compared the program output "
            "with the files in Expected_Output. Both diff commands printed nothing, so the outputs are identical.")
    code(d, "$ diff anagram.out ../Expected_Output/anagram.out\n(no output: identical)\n"
            "$ diff go.out ../Expected_Output/go.out\n(no output: identical)")
    para(d, f"anagram committed {n0(v('anagram','P1','default','sim_num_insn'))} instructions (about 18 million) and go committed "
            f"{n0(v('go','P1','default','sim_num_insn'))} (about 548 million). go is therefore about {v('go','P1','default','sim_num_insn')/v('anagram','P1','default','sim_num_insn'):.0f} times longer than anagram.")

    d.add_heading("(b) Baseline statistics", 2)
    rows = []
    def r(label, fn):
        rows.append([label] + [fn(b) for b in B])
    g = lambda b, k: v(b, "P1", "default", k)
    r("Instructions committed (sim_num_insn)", lambda b: n0(g(b, "sim_num_insn")))
    r("Cycles (sim_cycle)", lambda b: n0(g(b, "sim_cycle")))
    r("IPC (sim_IPC)", lambda b: f"{g(b,'sim_IPC'):.4f}")
    r("CPI (sim_CPI)", lambda b: f"{g(b,'sim_CPI'):.4f}")
    r("Loads (% of instructions)", lambda b: p1(g(b, "load_pct")))
    r("Stores (% of instructions)", lambda b: p1(g(b, "store_pct")))
    r("Branches (% of instructions)", lambda b: p1(g(b, "branch_pct")))
    r("L1 instruction-cache miss rate (il1.miss_rate)", lambda b: p2(100 * g(b, "il1.miss_rate")))
    r("L1 data-cache miss rate (dl1.miss_rate)", lambda b: p2(100 * g(b, "dl1.miss_rate")))
    r("L2 miss rate (ul2.miss_rate)", lambda b: p2(100 * g(b, "ul2.miss_rate")))
    r("Branch direction-prediction rate (bpred_bimod.bpred_dir_rate)", lambda b: p2(100 * g(b, "bpred_dir_rate")))
    table(d, ["Statistic (default configuration, full run)", "anagram", "go"], rows, [9.2, 3.6, 3.6])

    d.add_heading("(c) Instruction mix", 2)
    figure(d, "g1_instruction_mix.png", "Instruction mix of anagram and go in the default full run.", 14.5)
    a, c = (lambda k: g("anagram", k)), (lambda k: g("go", k))
    interp(d, [
        f"In both programs loads, stores and branches make up a large part of the instructions "
        f"({p1(a('load_pct')+a('store_pct')+a('branch_pct'))} for anagram and {p1(c('load_pct')+c('store_pct')+c('branch_pct'))} for go), "
        f"so only about {100-(a('load_pct')+a('store_pct')+a('branch_pct')):.0f}% (anagram) and {100-(c('load_pct')+c('store_pct')+c('branch_pct')):.0f}% (go) are plain ALU instructions. "
        f"The two mixes are close for memory ({p1(a('load_pct')+a('store_pct'))} loads and stores in anagram, {p1(c('load_pct')+c('store_pct'))} in go), "
        f"but they differ for branches: anagram has {p1(a('branch_pct'))} branches (one every {f1(100/a('branch_pct'))} instructions) and go only {p1(c('branch_pct'))} (one every {f1(100/c('branch_pct'))}). "
        f"The mix alone does not explain speed: anagram has more than twice the IPC of go ({f2(a('sim_IPC'))} against {f2(c('sim_IPC'))}) even with more branches. "
        f"The difference comes from the instruction cache (il1 miss rate {p2(100*a('il1.miss_rate'))} against {p2(100*c('il1.miss_rate'))}) "
        f"and from branch accuracy ({p1(100*a('bpred_dir_rate'))} against {p1(100*c('bpred_dir_rate'))})."])
    d.add_heading("Predictions for Parts 4 and 5", 2)
    para(d, f"**(i) Cache changes:** we expect **go** to be the more sensitive benchmark. Its L1 instruction cache already misses {p2(100*c('il1.miss_rate'))} of the fetches (anagram {p2(100*a('il1.miss_rate'))}), "
            f"and its data cache misses {p2(100*c('dl1.miss_rate'))} against {p2(100*a('dl1.miss_rate'))} for anagram, so it spends much more time in the memory system and a change there should move its IPC more. "
            f"anagram has tiny miss rates, so there is little to gain from bigger caches and little to lose from smaller ones. "
            f"**(ii) Branch prediction:** we also expect **go** to be the more sensitive one, because its default predictor is right only "
            f"{p1(100*c('bpred_dir_rate'))} of the time ({f1(c('mpki'))} mispredictions per 1000 instructions) against {p1(100*a('bpred_dir_rate'))} for anagram "
            f"({f1(a('mpki'))} per 1000). We are less sure about (ii), because anagram has many more branches and a higher IPC, "
            f"so each lost cycle is a bigger share of its run time. We check both predictions in Parts 4 and 5.")

# ============================================================================ Part 2
def part2(d):
    d.add_heading("Part 2: Superscalar width and in-order vs out-of-order issue", 1)
    para(d, "We ran W = 1, 2, 4 and 8 (fetch, decode, issue, commit and integer ALUs all equal to W; memory ports 1, 1, 2, 4), "
            "each with out-of-order issue (the default) and with -issue:inorder true. In all 16 runs the RUU is 64 entries and the LSQ is 32 entries.")
    W = [1, 2, 4, 8]
    rows = []
    for w in W:
        row = [str(w)]
        for b in B:
            o, i = v(b, "P2", f"w{w}.ooo", "sim_IPC"), v(b, "P2", f"w{w}.inorder", "sim_IPC")
            row += [f2(o), f2(i), f2(v(b, "P2", f"w{w}.inorder", "sim_cycle") / v(b, "P2", f"w{w}.ooo", "sim_cycle")) + "×"]
        rows.append(row)
    table(d, ["W", "anagram OoO IPC", "anagram in-order IPC", "anagram speedup", "go OoO IPC", "go in-order IPC", "go speedup"],
          rows, [1.2, 2.6, 2.9, 2.6, 2.4, 2.9, 2.2], font=9)
    d.add_heading("Graph (i): IPC vs width", 2)
    figure(d, "g2a_ipc_vs_width.png", "IPC against machine width W for anagram and go, with out-of-order (solid) and in-order issue (dashed). Peak IPC equals W.", 14.5)
    ao = {w: v("anagram", "P2", f"w{w}.ooo", "sim_IPC") for w in W}
    co = {w: v("go", "P2", f"w{w}.ooo", "sim_IPC") for w in W}
    ai = {w: v("anagram", "P2", f"w{w}.inorder", "sim_IPC") for w in W}
    ci = {w: v("go", "P2", f"w{w}.inorder", "sim_IPC") for w in W}
    interp(d, [
        f"With out-of-order issue, anagram rises from IPC {f2(ao[1])} at W = 1 to {f2(ao[8])} at W = 8, and go rises from {f2(co[1])} to {f2(co[8])}. "
        f"The peak IPC doubles every time W doubles, but the measured IPC does not: anagram grows {f2(ao[2]/ao[1])}×, then {f2(ao[4]/ao[2])}×, then only {f2(ao[8]/ao[4])}×, "
        f"and go grows {f2(co[2]/co[1])}×, {f2(co[4]/co[2])}× and {f2(co[8]/co[4])}×. At W = 8 anagram uses only {100*ao[8]/8:.0f}% of the peak and go only {100*co[8]/8:.0f}%. "
        f"The curves flatten because the program itself cannot give the machine more independent instructions: data dependencies make an instruction wait for the result of another one, "
        f"and branches limit how far ahead the machine can fetch. go has two more limits. It mispredicts {f1(v('go','P2','w8.ooo','mpki'))} branches per 1000 instructions "
        f"(anagram {f1(v('anagram','P2','w8.ooo','mpki'))}), and its instruction cache misses {p1(100*v('go','P2','w8.ooo','il1.miss_rate'))} of fetches, so the front end often has nothing to give the wide machine."])
    d.add_heading("Graph (ii): speedup of out-of-order over in-order", 2)
    figure(d, "g2b_speedup.png", "Speedup of out-of-order issue over in-order issue (cycles in-order divided by cycles out-of-order) against W.", 14.0)
    sa = {w: v("anagram", "P2", f"w{w}.inorder", "sim_cycle") / v("anagram", "P2", f"w{w}.ooo", "sim_cycle") for w in W}
    sc = {w: v("go", "P2", f"w{w}.inorder", "sim_cycle") / v("go", "P2", f"w{w}.ooo", "sim_cycle") for w in W}
    interp(d, [
        f"Out-of-order issue gives anagram a speedup of {f2(sa[1])}× at W = 1 but {f2(sa[8])}× at W = 8, and gives go {f2(sc[1])}× at W = 1 and {f2(sc[8])}× at W = 8. "
        f"The in-order machine hardly gains from width: its IPC only moves from {f2(ai[1])} to {f2(ai[8])} for anagram and from {f2(ci[1])} to {f2(ci[8])} for go. "
        f"The reason is that in-order issue stops at the first instruction that is not ready (for example one that waits for a load), so the extra issue slots stay empty. "
        f"The statistic ruu_occupancy shows this: with in-order issue anagram has only {f1(v('anagram','P2','w8.inorder','ruu_occupancy'))} instructions in the RUU on average at W = 8, "
        f"but with out-of-order issue it has {f1(v('anagram','P2','w8.ooo','ruu_occupancy'))}, so the machine can look much further ahead and find independent work. "
        f"For go the numbers are {f1(v('go','P2','w8.inorder','ruu_occupancy'))} and {f1(v('go','P2','w8.ooo','ruu_occupancy'))}. "
        f"From W = 2 on, the out-of-order gain of go is smaller than that of anagram, because go has less independent work to find. "
        f"At W = 1 only one instruction can issue per cycle anyway, so there is almost nothing for out-of-order issue to gain."])
    d.add_heading("Discussion", 2)
    para(d, f"**(a) Does IPC double when W doubles?** No. The best case is anagram going from W = 1 to W = 2 ({f2(ao[2]/ao[1])}×), and every later step is smaller. "
            f"The curves flatten for the reasons given above: dependencies, branch mispredictions and, for go, instruction-cache misses. "
            f"Functional units are not the main limit here, because we gave the machine W integer ALUs and W/2 memory ports.")
    para(d, f"**(b) Why does out-of-order gain more at large W?** A wide machine needs many ready instructions in the same cycle. "
            f"Only out-of-order issue can pick them from different places in the window. "
            f"In-order issue can use at most the instructions that sit together before the first stalled one, so at W = 8 it is almost as slow as at W = 2 ({f2(ai[8])} against {f2(ai[2])} for anagram).")
    para(d, f"**(c) Which benchmark has more ILP?** anagram. With out-of-order issue at W = 8 it reaches IPC {f2(ao[8])} against {f2(co[8])} for go, "
            f"and its average RUU occupancy is {f1(v('anagram','P2','w8.ooo','ruu_occupancy'))} entries against {f1(v('go','P2','w8.ooo','ruu_occupancy'))}. "
            f"anagram has a very low instruction-cache miss rate ({p2(100*v('anagram','P2','w8.ooo','il1.miss_rate'))}) and predicts {p1(100*v('anagram','P2','w8.ooo','bpred_dir_rate'))} of branches correctly, "
            f"so its window stays full of useful instructions. go predicts only {p1(100*v('go','P2','w8.ooo','bpred_dir_rate'))} correctly and has {p1(100*v('go','P2','w8.ooo','il1.miss_rate'))} instruction-cache misses, so its window is mostly empty.")

# ============================================================================ Part 3
def part3(d):
    d.add_heading("Part 3: Instruction window (RUU) size", 1)
    para(d, "The width stays at the default of 4. We ran RUU sizes of 4, 8, 16, 32, 64 and 128 entries, with the LSQ always half of the RUU (2 to 64 entries). The default is RUU 16 with LSQ 8.")
    R = [4, 8, 16, 32, 64, 128]
    rows = []
    for r_ in R:
        row = [str(r_), str(r_ // 2)]
        for b in B:
            row += [f2(v(b, "P3", f"ruu{r_}", "sim_IPC")), f1(v(b, "P3", f"ruu{r_}", "ruu_occupancy")), p1(100 * v(b, "P3", f"ruu{r_}", "ruu_full"))]
        rows.append(row)
    table(d, ["RUU", "LSQ", "anagram IPC", "anagram occupancy", "anagram RUU full", "go IPC", "go occupancy", "go RUU full"],
          rows, [1.3, 1.3, 2.0, 2.6, 2.4, 2.0, 2.4, 2.4], font=9, bold_rows=(2,))
    d.add_heading("Graph (i): IPC vs RUU size", 2)
    figure(d, "g3a_ipc_vs_ruu.png", "IPC against RUU size (log₂ axis) for anagram and go. The default RUU size is 16.", 14.0)
    a = {r_: v("anagram", "P3", f"ruu{r_}", "sim_IPC") for r_ in R}
    c = {r_: v("go", "P3", f"ruu{r_}", "sim_IPC") for r_ in R}
    interp(d, [
        f"Going from a 4-entry to a 128-entry RUU raises the IPC of anagram from {f2(a[4])} to {f2(a[128])} (+{pct_change(a[4], a[128]):.0f}%) and the IPC of go from {f2(c[4])} to {f2(c[128])} (+{pct_change(c[4], c[128]):.0f}%). "
        f"Almost all of the gain comes early: with 32 entries anagram already has {100*a[32]/a[128]:.1f}% and go {100*c[32]/c[128]:.1f}% of their best IPC, so the curves are flat from 32 entries on. "
        f"A small window can only look a few instructions ahead, so one slow instruction (a load or a long operation) blocks the whole machine. "
        f"anagram gains much more than go because it has more independent instructions to find. go is held back by other problems that a bigger window cannot fix, "
        f"mainly instruction-cache misses and {f1(v('go','P3','ruu128','mpki'))} branch mispredictions per 1000 instructions. "
        f"Doubling the window beyond about 32 entries costs hardware but gives almost nothing."])
    d.add_heading("Graph (ii): RUU occupancy and how often the RUU is full", 2)
    figure(d, "g3b_ruu_occupancy.png", "Average RUU occupancy (left) and fraction of cycles with a full RUU (right) against RUU size.", 15.5)
    interp(d, [
        f"The occupancy graph explains the saturation. For anagram the average occupancy grows from {f1(v('anagram','P3','ruu4','ruu_occupancy'))} to {f1(v('anagram','P3','ruu128','ruu_occupancy'))} entries, "
        f"but the RUU is full {p1(100*v('anagram','P3','ruu4','ruu_full'))} of the time at 4 entries, {p1(100*v('anagram','P3','ruu16','ruu_full'))} at 16 entries, {p1(100*v('anagram','P3','ruu32','ruu_full'))} at 32 and only {p1(100*v('anagram','P3','ruu128','ruu_full'))} at 128. "
        f"When the RUU is full the machine must stop fetching, which loses IPC; when it is almost never full, a bigger RUU has nothing left to fix. "
        f"For go the occupancy never goes above {f1(v('go','P3','ruu128','ruu_occupancy'))} entries even with 128 available, and the RUU is full only {p1(100*v('go','P3','ruu32','ruu_full'))} of the time at 32 entries, "
        f"so go saturates at a smaller window. The window never fills because a mispredicted branch throws away all younger instructions, "
        f"and anagram mispredicts one branch every {1000/v('anagram','P3','ruu128','mpki'):.0f} instructions and go one every {1000/v('go','P3','ruu128','mpki'):.0f}."])
    d.add_heading("Discussion", 2)
    para(d, f"**(a) Where does a bigger window stop paying off?** For anagram it stops at about 32 entries (IPC {f3(a[32])} against {f3(a[64])} at 64 and {f3(a[128])} at 128), and at 64 entries the RUU is full only {p1(100*v('anagram','P3','ruu64','ruu_full'))} of the time. "
            f"For go it stops at about 32 entries too (IPC {f3(c[32])} against {f3(c[64])} at 64 and {f3(c[128])} at 128) with the RUU full {p1(100*v('go','P3','ruu32','ruu_full'))} of the time. "
            f"In both programs the point of saturation is where the RUU is rarely full.")
    para(d, "**(b) How does a larger window help hide a cache miss, and why is it limited by branch mispredictions?** "
            "When a load misses in the cache, the instructions after it can keep executing if they do not need its data, but only if they fit in the window. "
            "A bigger RUU keeps more of these independent instructions, so the miss delay is overlapped with useful work. "
            "A branch misprediction is different: the instructions fetched after the wrong branch are on the wrong path and are thrown away, "
            "so a bigger window just holds more wrong-path instructions. The machine must wait for the branch to resolve and then start again, and nothing can hide that delay.")
    x = {b: v(b, "P3x", "w8_ruu16", "sim_IPC") for b in B}
    w4 = {b: v(b, "P2", "w4.ooo", "sim_IPC") for b in B}
    gx, g4 = (x["anagram"] * x["go"]) ** 0.5, (w4["anagram"] * w4["go"]) ** 0.5
    table(d, ["Configuration", "anagram IPC", "go IPC", "Geometric mean", "Hardware cost (Part 6 cost model)"],
          [["W = 4, RUU 64, LSQ 32 (Part 2 run)", f3(w4["anagram"]), f3(w4["go"]), f3(g4), "16 + 16 = 32 units"],
           ["W = 8, RUU 16, LSQ 8 (extra run)", f3(x["anagram"]), f3(x["go"]), f3(gx), "32 + 4 = 36 units"]],
          [5.6, 2.4, 2.2, 2.6, 4.0], font=9.5)
    gap = 100 * (gx / g4 - 1)
    assert 0 < gap < 5, gap
    para(d, f"**(c) W = 8 with a 16-entry RUU, or W = 4 with a 64-entry RUU?** We ran the missing configuration (W = 8, RUU 16, LSQ 8, 4 memory ports) and used the Part 2 run for W = 4 with RUU 64. "
            f"The result is close: anagram gets {f3(w4['anagram'])} against {f3(x['anagram'])} and go gets {f3(w4['go'])} against {f3(x['go'])}, so the wide machine is only {gap:.1f}% faster on the geometric mean. "
            f"We would still choose **W = 4 with a 64-entry RUU**. It is {100*(1-32/36):.0f}% cheaper in the cost model of Part 6 (32 against 36 units), and a 4-wide machine needs half the decoders, ALUs and ports of an 8-wide one, which costs more in real hardware than the model shows. "
            f"The results also show that a wide machine does not need a big window here: anagram and go keep on average only {f1(v('anagram','P3x','w8_ruu16','ruu_occupancy'))} and {f1(v('go','P3x','w8_ruu16','ruu_occupancy'))} entries busy in the 16-entry RUU, "
            f"because branch mispredictions and cache misses limit both programs before the window does.")

# ============================================================================ Part 4
def part4(d):
    d.add_heading("Part 4: Memory hierarchy", 1)
    para(d, "All Part 4 runs use the default width of 4 and RUU of 16. We changed (a) the size of the L1 data cache, (b) its block size, and (c) the main-memory latency with and without the L2 cache.")
    caps = [1, 4, 16, 64]
    A = lambda b, c, k: v(b, "P4a", f"dl1_{c}KB", k)
    d.add_heading("(a) L1 data-cache capacity", 2)
    rows = [[f"{c} KB" + (" (default)" if c == 16 else "")] + sum([[p2(100 * A(b, c, "dl1.miss_rate")), f"{A(b, c, 'sim_IPC'):.4f}"] for b in B], []) for c in caps]
    table(d, ["dl1 capacity", "anagram miss rate", "anagram IPC", "go miss rate", "go IPC"], rows, [3.4, 3.2, 3.0, 3.0, 3.0], font=9.5, bold_rows=(2,))
    figure(d, "g4a_dl1_capacity.png", "L1 data-cache miss rate (left) and IPC (right) against L1 data-cache capacity. The cache is 4-way with 32-byte blocks.", 15.5)
    ga = {b: 100 * (A(b, 64, "sim_IPC") / A(b, 1, "sim_IPC") - 1) for b in B}
    assert ga["go"] > ga["anagram"]
    interp(d, [
        f"When the L1 data cache grows from 1 KB to 64 KB, the miss rate of anagram falls from {p2(100*A('anagram',1,'dl1.miss_rate'))} to {p2(100*A('anagram',64,'dl1.miss_rate'))} and its IPC rises from {f2(A('anagram',1,'sim_IPC'))} to {f2(A('anagram',64,'sim_IPC'))} (+{ga['anagram']:.1f}%). "
        f"For go the miss rate falls from {p2(100*A('go',1,'dl1.miss_rate'))} to {p2(100*A('go',64,'dl1.miss_rate'))} and the IPC rises from {f2(A('go',1,'sim_IPC'))} to {f2(A('go',64,'sim_IPC'))} (+{ga['go']:.1f}%). "
        f"The miss rate drops fast at the beginning and then flattens, so the IPC curve has a knee. For anagram the knee is at 16 KB: going from 16 KB to 64 KB removes only {100*(1-A('anagram',64,'dl1.misses')/A('anagram',16,'dl1.misses')):.1f}% of the misses. "
        f"go keeps improving up to 64 KB ({int(A('go',16,'dl1.misses')):,} misses at 16 KB against {int(A('go',64,'dl1.misses')):,} at 64 KB, {100*(1-A('go',64,'dl1.misses')/A('go',16,'dl1.misses')):.0f}% fewer), so its data working set is bigger. "
        f"go is also the more sensitive program: its miss rate changes by about {A('go',1,'dl1.miss_rate')/A('go',64,'dl1.miss_rate'):.0f} times between 1 KB and 64 KB (anagram {A('anagram',1,'dl1.miss_rate')/A('anagram',64,'dl1.miss_rate'):.0f} times), and its IPC gain is larger. "
        f"At 1 KB the data cache of go misses {p1(100*A('go',1,'dl1.miss_rate'))} of the accesses, so a quarter of all its loads and stores wait for the L2."])
    d.add_heading("(b) L1 data-cache block size", 2)
    blks = [8, 16, 32, 64]
    Bk = lambda b, x, k: v(b, "P4b", f"blk{x}", k)
    rows = [[f"{x} B" + (" (default)" if x == 32 else "")] + sum([[p2(100 * Bk(b, x, "dl1.miss_rate")), f"{Bk(b, x, 'sim_IPC'):.4f}"] for b in B], []) for x in blks]
    table(d, ["Block size", "anagram miss rate", "anagram IPC", "go miss rate", "go IPC"], rows, [3.4, 3.2, 3.0, 3.0, 3.0], font=9.5, bold_rows=(2,))
    figure(d, "g4b_dl1_block.png", "L1 data-cache miss rate (left) and IPC (right) against block size. The cache is 16 KB and 4-way.", 15.5)
    bestblk = {b: min(blks, key=lambda x: Bk(b, x, "dl1.miss_rate")) for b in B}
    bestipc = {b: max(blks, key=lambda x: Bk(b, x, "sim_IPC")) for b in B}
    assert bestblk == bestipc == {"anagram": 64, "go": 32}, (bestblk, bestipc)
    interp(d, [
        f"Doubling the block size cuts the miss rate of anagram almost exactly in half each time ({p2(100*Bk('anagram',8,'dl1.miss_rate'))}, {p2(100*Bk('anagram',16,'dl1.miss_rate'))}, {p2(100*Bk('anagram',32,'dl1.miss_rate'))}, {p2(100*Bk('anagram',64,'dl1.miss_rate'))}). "
        f"This is strong spatial locality: anagram reads its data one element after the other, so each block that is brought in is used by the next accesses. "
        f"go behaves differently: its miss rate goes {p2(100*Bk('go',8,'dl1.miss_rate'))}, {p2(100*Bk('go',16,'dl1.miss_rate'))}, {p2(100*Bk('go',32,'dl1.miss_rate'))} and then **rises** to {p2(100*Bk('go',64,'dl1.miss_rate'))} at 64 B. "
        f"The first steps help, but with a fixed 16 KB cache a 64-byte block leaves only 256 blocks, and a program whose accesses jump around (go searches many board positions and tables) uses only a small part of each large block, "
        f"so the block takes space that other data needs. The best block is 64 B for anagram and 32 B (the default) for go, and in both cases it is also the block with the highest IPC. "
        f"The IPC effect is small: {100*(Bk('anagram',64,'sim_IPC')/Bk('anagram',8,'sim_IPC')-1):.1f}% for anagram from 8 B to 64 B, and only {100*(max(Bk('go',x,'sim_IPC') for x in blks)/min(Bk('go',x,'sim_IPC') for x in blks)-1):.2f}% for go between its worst and best block. "
        f"In this simulator an L1 miss that hits in the L2 always takes the same 6 cycles, so a bigger block has no extra miss penalty. "
        f"In a real processor a bigger block takes longer to transfer, so the best block size would not be the largest."])
    d.add_heading("(c) Main-memory latency, with and without an L2", 2)
    lat = [25, 50, 100, 200]
    M = lambda b, l, w, k: v(b, "P4c", f"mem{l}_{w}", k)
    rows = [[str(l)] + sum([[f"{M(b, l, 'L2', 'sim_CPI'):.3f}", f"{M(b, l, 'noL2', 'sim_CPI'):.3f}"] for b in B], []) for l in lat]
    table(d, ["Memory latency (cycles)", "anagram CPI, with L2", "anagram CPI, no L2", "go CPI, with L2", "go CPI, no L2"], rows, [3.6, 3.2, 3.2, 3.0, 3.0], font=9.5)
    figure(d, "g4c_cpi_vs_memlat.png", "CPI against main-memory latency, with the default 256 KB L2 (solid) and without an L2 (dashed). The default latency is 18 cycles. The go curve without an L2 is far above the others.", 14.5)
    sl = lambda b, w: (M(b, 200, w, "sim_CPI") - M(b, 100, w, "sim_CPI"))
    interp(d, [
        f"Memory latency makes CPI grow in a straight line, but the slope is very different with and without an L2. Between 100 and 200 cycles the CPI of anagram grows by {f3(sl('anagram','L2'))} with the L2 and by {f3(sl('anagram','noL2'))} without it, "
        f"and for go it grows by {f3(sl('go','L2'))} with the L2 and by {f3(sl('go','noL2'))} without it. So each extra 100 cycles of memory latency costs about {sl('anagram','noL2')/sl('anagram','L2'):.0f} times more for anagram and {sl('go','noL2')/sl('go','L2'):.0f} times more for go when there is no L2. "
        f"The reason is the number of accesses that reach main memory. With the L2, only {int(M('anagram',100,'L2','ul2.misses')):,} accesses go to memory for anagram and {int(M('go',100,'L2','ul2.misses')):,} for go; "
        f"without it every L1 miss goes there ({int(M('anagram',100,'noL2','il1.misses')+M('anagram',100,'noL2','dl1.misses')):,} for anagram and {int(M('go',100,'noL2','il1.misses')+M('go',100,'noL2','dl1.misses')):,} for go). "
        f"At 200 cycles the IPC of anagram is {f2(M('anagram',200,'L2','sim_IPC'))} with the L2 and {f2(M('anagram',200,'noL2','sim_IPC'))} without it, and for go it is {f2(M('go',200,'L2','sim_IPC'))} against {f2(M('go',200,'noL2','sim_IPC'))}. "
        f"The L2 is therefore worth much more when memory is slow, which is why real processors keep adding cache levels as memory gets slower compared with the CPU."])
    d.add_heading("Discussion", 2)
    a16, a64 = A("anagram", 16, "dl1.misses"), A("anagram", 64, "dl1.misses")
    para(d, f"**(a) Compulsory, capacity or conflict?** The steep part of the capacity graph is made of **capacity misses**: the data does not fit in a 1 KB or 4 KB cache, so blocks are thrown out and fetched again. "
            f"For anagram the number of misses hardly changes between 16 KB ({int(a16):,}) and 64 KB ({int(a64):,}), so the misses that remain are mostly **compulsory** (the first touch of each block), and conflict misses are small because the cache is 4-way. "
            f"go still has capacity misses at 16 KB: its count falls from {int(A('go',16,'dl1.misses')):,} to {int(A('go',64,'dl1.misses')):,} at 64 KB, because its data working set is larger than 16 KB. "
            f"What is left at 64 KB is compulsory and conflict misses. "
            f"This explains the knee: once the cache holds the working set, only compulsory misses are left and a bigger cache cannot remove them. (We did not run a fully associative cache, so the split between compulsory and conflict misses is our estimate from the shape of the graph.)")
    para(d, f"**(b) Block size and spatial locality.** A bigger block brings in neighbouring data together with the data that was missed, so it helps programs that read data in order. This is why the anagram miss rate halves each time the block doubles. "
            f"For go the benefit stops at 32 B, and a 64 B block makes the miss rate worse ({p2(100*Bk('go',32,'dl1.miss_rate'))} to {p2(100*Bk('go',64,'dl1.miss_rate'))}), which shows that its spatial locality is limited. "
            f"The IPC changes much less than the miss rate because most L1 misses hit in the L2 (6 cycles), and the out-of-order core hides a large part of those 6 cycles. "
            f"Also, a bigger block has no extra transfer cost in this simulator, so the largest block looks better here than it would in real hardware.")
    ci, cd = M("go", 25, "noL2", "il1.misses"), M("go", 25, "noL2", "dl1.misses")
    ai_, ad = M("anagram", 25, "noL2", "il1.misses"), M("anagram", 25, "noL2", "dl1.misses")
    para(d, f"**(c) What an extra 100 cycles of latency costs.** From graph (iii) the CPI of anagram grows by about {f2(sl('anagram','L2'))} CPI per extra 100 cycles with the L2 and by {f2(sl('anagram','noL2'))} without it; "
            f"for go it is {f2(sl('go','L2'))} with the L2 and {f2(sl('go','noL2'))} without it. The L2 catches most L1 misses, so it makes the processor much less sensitive to slow memory. "
            f"The L2 is worth the most for go: at 25 cycles of memory latency, removing it lowers the IPC of go from {f2(M('go',25,'L2','sim_IPC'))} to {f2(M('go',25,'noL2','sim_IPC'))} ({100*(M('go',25,'noL2','sim_IPC')/M('go',25,'L2','sim_IPC')-1):.0f}%) and the IPC of anagram from {f2(M('anagram',25,'L2','sim_IPC'))} to {f2(M('anagram',25,'noL2','sim_IPC'))} ({100*(M('anagram',25,'noL2','sim_IPC')/M('anagram',25,'L2','sim_IPC')-1):.0f}%).")
    para(d, f"**(d) Why removing the L2 hurts go so much more.** go has {int(ci):,} L1 instruction misses and only {int(cd):,} data misses, so {100*ci/(ci+cd):.0f}% of its L1 misses are instruction-fetch misses (il1 miss rate {p2(100*A('go',16,'il1.miss_rate'))}, dl1 miss rate {p2(100*A('go',16,'dl1.miss_rate'))}). "
            f"The code of go is larger than the 16 KB instruction cache but fits easily in the 256 KB L2, so with the L2 these misses cost only a few cycles, and without it each one goes to main memory. "
            f"An instruction miss is very bad for an out-of-order processor: while the fetch unit waits, no new instructions enter the window, and the machine soon runs out of work. "
            f"anagram has only {int(ai_):,} instruction misses and {int(ad):,} data misses (il1 miss rate {p2(100*A('anagram',16,'il1.miss_rate'))}, dl1 miss rate {p2(100*A('anagram',16,'dl1.miss_rate'))}), "
            f"which is about {(ci+cd)/(ai_+ad):.0f} times fewer L1 misses than go, and its data misses can be partly hidden by other instructions in the window.")
    # (e) check of the Part 1 prediction
    sens = {b: 100 * (max(A(b, c, "sim_IPC") for c in caps) / min(A(b, c, "sim_IPC") for c in caps) - 1) for b in B}
    sensb = {b: 100 * (max(Bk(b, x, "sim_IPC") for x in blks) / min(Bk(b, x, "sim_IPC") for x in blks) - 1) for b in B}
    loss = {b: 100 * (1 - M(b, 100, "noL2", "sim_IPC") / M(b, 100, "L2", "sim_IPC")) for b in B}
    assert sens["go"] > sens["anagram"] and sensb["go"] < sensb["anagram"] and loss["go"] > loss["anagram"]
    para(d, f"**(e) Was our Part 1 prediction about cache sensitivity correct?** Mostly. We predicted that go would be the more sensitive benchmark, because it has much higher miss rates. "
            f"That was **correct for the L1 data-cache capacity**: changing it moves the IPC of go by {sens['go']:.1f}% against {sens['anagram']:.1f}% for anagram. "
            f"It was **correct for the L2**: removing the L2 at 100 cycles costs go {loss['go']:.0f}% of its IPC and anagram {loss['anagram']:.0f}%. "
            f"It was **wrong for the block size**: changing the block moves the IPC of go by only {sensb['go']:.2f}% against {sensb['anagram']:.1f}% for anagram, because the data misses of go are a small part of its stall time. "
            f"go loses most of its cycles in the instruction cache, and Part 4 never changes the L1 instruction cache. So the data-cache block size says little about the main cache problem of go.")

# ============================================================================ Part 5
def part5(d):
    d.add_heading("Part 5: Branch prediction", 1)
    para(d, "We ran six predictors on both benchmarks with everything else at the default (width 4, RUU 16). "
            "The perfect predictor is an upper bound. The static not-taken predictor needs no hardware. "
            "The other four are real predictors: bimodal with 512 and with 2048 entries, a two-level predictor with global history (GAg: 1 history register of 8 bits, 1024 counters), and the combined (bimodal + two-level) predictor.")
    names = [("perfect", "Perfect"), ("nottaken", "Not-taken"), ("bimod512", "Bimodal 512"), ("bimod2048", "Bimodal 2048"), ("2lev", "Two-level"), ("comb", "Combined")]
    G = lambda b, l, k: v(b, "P5", l, k)
    rows = []
    for l, nm in names:
        row = [nm]
        for b in B:
            ipc = G(b, l, "sim_IPC")
            if l == "perfect":
                row += ["100.0%", "0.0", f"{ipc:.4f}", "1.000"]
            else:
                row += [p1(100 * G(b, l, "bpred_dir_rate")), f1(G(b, l, "mpki")), f"{ipc:.4f}", f"{ipc / G(b, 'perfect', 'sim_IPC'):.3f}"]
        rows.append(row)
    table(d, ["Predictor", "anagram accuracy", "anagram MPKI", "anagram IPC", "anagram IPC / perfect", "go accuracy", "go MPKI", "go IPC", "go IPC / perfect"],
          rows, [2.6, 1.9, 1.7, 1.8, 2.0, 1.9, 1.5, 1.6, 1.9], font=8.5, bold_rows=(3,))
    para(d, "MPKI = mispredictions per 1000 instructions = bpred_X.misses ÷ sim_num_insn × 1000. Accuracy is bpred_X.bpred_dir_rate.", size=9.5, italic=True)
    d.add_heading("Graph (i): direction-prediction accuracy", 2)
    figure(d, "g5a_bpred_accuracy.png", "Direction-prediction accuracy of each predictor for anagram and go. The default predictor is bimodal with 2048 entries.", 14.5)
    acc = lambda b, l: 100 * G(b, l, "bpred_dir_rate")
    real = ['bimod512', 'bimod2048', '2lev', 'comb']
    assert all(acc(b, "comb") >= max(acc(b, l) for l in real) for b in B)
    assert all(acc(b, "2lev") < acc(b, "bimod2048") for b in B)
    assert all(acc("go", l) < acc("anagram", l) for l in real)
    interp(d, [
        f"The static not-taken predictor is right only {p1(acc('anagram','nottaken'))} of the time for anagram and {p1(acc('go','nottaken'))} for go, because most branches in loops are taken. "
        f"The dynamic predictors are much better, between {p1(min(acc(b, l) for b in B for l in real))} and {p1(max(acc(b, l) for b in B for l in real))}. "
        f"Going from 512 to 2048 bimodal entries changes anagram from {p1(acc('anagram','bimod512'))} to {p1(acc('anagram','bimod2048'))} and improves go from {p1(acc('go','bimod512'))} to {p1(acc('go','bimod2048'))}. "
        f"The combined predictor is the best on both benchmarks ({p1(acc('anagram','comb'))} and {p1(acc('go','comb'))}), but for go its advantage over the default is only {acc('go','comb')-acc('go','bimod2048'):.1f} points, against {acc('anagram','comb')-acc('anagram','bimod2048'):.1f} points for anagram. "
        f"The two-level predictor is not better than the simple bimodal one here: it gets {p1(acc('anagram','2lev'))} against {p1(acc('anagram','bimod2048'))} on anagram and {p1(acc('go','2lev'))} against {p1(acc('go','bimod2048'))} on go. "
        f"The accuracy of go is always lower than that of anagram, which agrees with its many hard-to-predict, data-dependent branches (decisions in a game search depend on the board, not on loop counters)."])
    d.add_heading("Graph (ii): IPC relative to the perfect predictor", 2)
    figure(d, "g5b_ipc_normalised.png", "IPC of each predictor divided by the IPC with the perfect predictor.", 14.5)
    rel = lambda b, l: G(b, l, "sim_IPC") / G(b, "perfect", "sim_IPC")
    interp(d, [
        f"Branch prediction has a very large effect on speed. With not-taken the IPC falls to {rel('anagram','nottaken'):.2f} of perfect for anagram and {rel('go','nottaken'):.2f} for go, "
        f"and the default bimodal predictor reaches {rel('anagram','bimod2048'):.2f} and {rel('go','bimod2048'):.2f}. "
        f"The best real predictor (combined) gives {rel('anagram','comb'):.2f} for anagram and {rel('go','comb'):.2f} for go, so even the best one still loses {100*(1-rel('anagram','comb')):.1f}% and {100*(1-rel('go','comb')):.1f}%. "
        f"The IPC follows the accuracy: a predictor with fewer mispredictions per 1000 instructions always has the higher IPC, because each misprediction throws away the instructions fetched after the branch and wastes the fetch cycles. "
        f"Going from the default to the combined predictor raises IPC by {100*(G('anagram','comb','sim_IPC')/G('anagram','bimod2048','sim_IPC')-1):.1f}% for anagram but only {100*(G('go','comb','sim_IPC')/G('go','bimod2048','sim_IPC')-1):.1f}% for go."])
    d.add_heading("Discussion", 2)
    para(d, f"**(a) Static not-taken is free, how much IPC does it lose?** Compared with the perfect predictor it loses {100*(1-rel('anagram','nottaken')):.0f}% of the IPC for anagram and {100*(1-rel('go','nottaken')):.0f}% for go. "
            f"It is so bad on anagram because {p1(v('anagram','P1','default','branch_pct'))} of its instructions are branches, and not-taken is wrong for about {100-acc('anagram','nottaken'):.0f}% of them "
            f"({f1(G('anagram','nottaken','mpki'))} mispredictions per 1000 instructions). go has fewer branches ({p1(v('go','P1','default','branch_pct'))}), so it has {f1(G('go','nottaken','mpki'))} per 1000 and loses less. "
            f"Every wrong guess wastes about 4 instruction slots per lost cycle on this 4-wide machine, so the machine loses most of its width.")
    da = acc('anagram','bimod2048') - acc('anagram','bimod512'); dc = acc('go','bimod2048') - acc('go','bimod512')
    assert abs(da) < 0.1 and dc > 1.0
    para(d, f"**(b) Bimodal 512 against 2048 and aliasing.** For go the bigger table is clearly better (accuracy {p2(acc('go','bimod512'))} to {p2(acc('go','bimod2048'))}, MPKI {f1(G('go','bimod512','mpki'))} to {f1(G('go','bimod2048','mpki'))}). "
            f"For anagram it makes almost no difference ({p2(acc('anagram','bimod512'))} to {p2(acc('anagram','bimod2048'))}, a change of {da:.2f} points). "
            f"The bimodal predictor picks a 2-bit counter using the address of the branch. With only 512 counters, several different branches have to share the same counter (this is called aliasing), "
            f"so one branch changes the counter that another branch is using and both are predicted worse. A bigger table has fewer collisions. "
            f"go is a big program with many different branches (its instruction cache misses {p1(100*v('go','P1','default','il1.miss_rate'))}, so its code is large), so 512 counters are not enough and aliasing is common ({dc:.2f} points lost). anagram is a small program with few branches, so even 512 counters hold them without collisions and aliasing is almost zero.")
    best = {b: min(["bimod512", "bimod2048", "2lev", "comb"], key=lambda l: G(b, l, "mpki")) for b in B}
    assert best["anagram"] == best["go"] == "comb"
    para(d, f"**(c) MPKI and the best predictor.** MPKI for the default predictor is {f1(G('anagram','bimod2048','mpki'))} for anagram and {f1(G('go','bimod2048','mpki'))} for go; for the combined predictor it is {f1(G('anagram','comb','mpki'))} and {f1(G('go','comb','mpki'))} (full table above). "
            f"The best real predictor is the **combined** predictor for both benchmarks. "
            f"A two-level predictor can do worse than a simple bimodal table because the GAg version chooses its counter only from the last 8 branch results and ignores the address of the branch. "
            f"Different branches that happen to see the same recent history use the same counter and disturb each other, and the counters need time to learn all 256 history patterns. "
            f"A branch that is almost always taken is predicted very well by a per-address bimodal counter, but not by a global history. "
            f"The combined predictor fixes this by keeping both predictors and a small table (the chooser) that learns, for each branch, which of the two has been right more often. It then uses the better one, so it is at least as good as the best part for most branches. "
            f"For go the gain is small because many of its branches depend on the data and neither part can predict them.")
    para(d, f"**(d) How much is lost against perfect, and why does a wide machine lose more?** The best real predictor still loses {100*(1-rel('anagram','comb')):.1f}% of the IPC on anagram and {100*(1-rel('go','comb')):.1f}% on go compared with the perfect predictor. "
            f"A wider and deeper out-of-order machine loses more because it keeps more instructions in flight: when a branch is mispredicted, all the younger instructions in the window and in the fetch queue are wrong and must be thrown away, "
            f"and the longer the pipeline and the wider the fetch, the more slots are wasted per misprediction. For example, one wasted fetch cycle costs 4 instruction slots at W = 4 but 8 slots at W = 8, so the same misprediction penalty hurts a wider machine about twice as much in lost instructions.")
    span = {b: 100 * (max(G(b, l, "sim_IPC") for l in real) / min(G(b, l, "sim_IPC") for l in real) - 1) for b in B}
    sens = {b: 100 * (1 - G(b, "nottaken", "sim_IPC") / G(b, "perfect", "sim_IPC")) for b in B}
    gap = {b: 100 * (1 - rel(b, "bimod2048")) for b in B}
    assert sens["anagram"] > sens["go"] and span["anagram"] > span["go"] and gap["go"] > gap["anagram"]
    para(d, f"**(e) Was our Part 1 prediction about branch prediction correct?** We predicted that go would be more sensitive because its default accuracy is lower. The answer is **mixed, and overall wrong**. "
            f"With the default predictor go does lose slightly more of its perfect IPC ({gap['go']:.1f}% against {gap['anagram']:.1f}% for anagram), as predicted. "
            f"But when the predictor is changed, anagram reacts much more: not-taken costs anagram {sens['anagram']:.0f}% of its IPC and go {sens['go']:.0f}%, and among the four real predictors the best is {span['anagram']:.0f}% faster than the worst for anagram and only {span['go']:.0f}% for go. "
            f"The reason is that anagram is fast ({f2(G('anagram','perfect','sim_IPC'))} IPC with perfect prediction) and has {p1(v('anagram','P1','default','branch_pct'))} branches, so every branch matters, "
            f"while go ({f2(G('go','perfect','sim_IPC'))} IPC) is also slowed by instruction-cache misses that no predictor can fix, and even the best of these predictors is wrong for about {100-acc('go','comb'):.0f}% of its branches. "
            f"Sensitivity to the predictor depends on the branch share and on the speed of the machine, and not only on the accuracy.")

# ============================================================================ Part 6
def dname(des):
    W, R, il1, dl1, l2, bp = des
    return f"W{W}, RUU {R}, L1-I {il1[0]}K/{il1[1]}B/{il1[2]}-way, L1-D {dl1[0]}K/{dl1[1]}B/{dl1[2]}-way, L2 {l2[0]}K, {bp}"

def part6(d):
    d.add_heading("Part 6: Design-space exploration under a cost budget", 1)
    des = json.load(open(os.path.join(ROOT, "data", "part6_designs.json")))
    summ = json.load(open(os.path.join(ROOT, "data", "part6_search_summary.json")))
    cand = {r["name"]: r for r in csv.DictReader(open(os.path.join(ROOT, "data", "part6_candidates.csv")))}
    G = lambda b, l, k: v(b, "P6", l, k)
    gens = summ["generations"]
    para(d, "In this part we had to find the fastest processor that costs at most 100 units, using the cost model of the project (width 4 per way, RUU 0.25 per entry, L1 caches 1 per KB, L2 0.125 per KB, "
            "branch predictor 0 for not-taken, 1 per 1024 entries for bimodal, 3 for the two-level predictor and 6 for the combined one). The score of a design is the geometric mean of the IPC of anagram and go.")
    d.add_heading("How we searched: a genetic algorithm", 2)
    para(d, f"Trying every combination is impossible (there are more than a million), so we used a **genetic algorithm** (script part6_search.py). A design is a chromosome of 6 genes: width (2, 4 or 8), RUU size (16 to 128), "
            "L1 instruction cache, L1 data cache (size 4 to 64 KB, block size and associativity), L2 (none or 64 to 512 KB) and branch predictor (not-taken, bimodal 512 to 4096, two-level, combined). "
            "The fitness of a design is its geometric-mean IPC. The algorithm works like this:")
    for t in ["Generation 0 is the default design plus 13 random designs that cost between 70 and 100 units.",
              "Parents are chosen by tournament selection (the best of 3 random designs is picked).",
              "A child takes each gene from one of the two parents (uniform crossover), and each gene is then changed at random with probability 0.25 (mutation).",
              "A child that costs more than 100 units is thrown away and a new one is made, so every design that is simulated is inside the budget.",
              "The 2 best designs of each generation go into the next one unchanged (elitism). The population is 14 designs and we ran 10 generations (random seed 13)."]:
        bullet(d, t)
    para(d, f"In total {gens[-1]['evaluated_so_far']} different designs were simulated, each on both benchmarks. To save time the search runs used the first 30 million instructions of each program. "
            "The designs that were the best of their generation and the best designs of the last generation were then run again with the full 100 million instructions, and all the IPC numbers in the tables below come from these full runs. "
            "Because the cap is different, the IPC in the search log is a little different from the IPC of the full run (for example the search score of the final design is "
            f"{gens[-1]['best']:.3f} and its full-run score is {float(cand['final']['geomean_ipc']):.3f}).")
    rows = [[str(g_["generation"]), f"{g_['best']:.3f}", f"{g_['mean']:.3f}", str(g_["evaluated_so_far"]), g_["best_design"]] for g_ in gens]
    table(d, ["Generation", "Best score (30M)", "Population mean", "Designs run so far", "Best design so far"], rows, [1.9, 2.3, 2.4, 2.4, 7.6], align_right_from=1, font=8)
    para(d, "Score = geometric-mean IPC with the 30-million-instruction cap. The design name reads W = width, R = RUU, I = L1-I (size, block, ways), D = L1-D, L2 = L2 size, then the predictor.", size=9.5, italic=True)
    d.add_heading("Candidate designs", 2)
    rows = []
    desc = {"default": "Default design", "g1_best": "Best of generation 0", "g2_best": "Best of generation 1",
            "g3_best": "Best of generation 4", "alt1": "Runner-up from the last generation (2-way L1-I)", "alt2": "Runner-up (bimodal 1024)",
            "final": "FINAL: best full-run score"}
    for c in des:
        l = c["label"]; r = cand[l]
        rows.append([l, desc.get(l, l) + ": " + dname(c["design"]), f"{c['cost']:.0f}", f"{float(r['anagram_ipc']):.3f}", f"{float(r['go_ipc']):.3f}", f"{float(r['geomean_ipc']):.3f}"])
    table(d, ["Name", "What it is", "Cost", "anagram IPC", "go IPC", "Geomean IPC"], rows, [1.9, 7.6, 1.1, 1.9, 1.6, 2.1], align_right_from=2, font=8.5, bold_rows=(len(rows) - 1,))
    para(d, "Each design is a full run of both benchmarks with 100 million instructions (raw outputs: results/*.P6.*.txt; configurations: configs/*.P6.*.cfg). The L2 block size is 64 bytes and 4-way in all designs.", size=9.5, italic=True)
    d.add_heading("Graph: cost against performance", 2)
    figure(d, "g6_cost_vs_ipc.png", "Cost and geometric-mean IPC of the candidate designs. The default design is the orange square, the final design is the star. The dashed line is the budget of 100 units.", 14.5)
    g = {l: float(cand[l]["geomean_ipc"]) for l in cand}
    interp(d, [
        f"The default design costs 86 units and has a geometric-mean IPC of {g['default']:.3f}. Our final design costs 98 units and reaches {g['final']:.3f}, which is {100*(g['final']/g['default']-1):.0f}% more performance for 12 more units. "
        f"The picture shows that the algorithm found most of the gain in two steps. The first is the width: g1_best has the same cost as the default (86) but IPC {g['g1_best']:.3f}, because it moves money from both L1 caches to a width of 8 and a 32-entry RUU; "
        f"this agrees with Parts 2 and 3, where a wide machine with a 32-entry window was the useful combination. "
        f"The second step is the L1 instruction cache: g2_best and g3_best use a 16 KB, 64-byte-block, 4-way L1-I cache, which is what the go benchmark needs "
        f"(its L1-I miss rate falls from {100*G('go','default','il1.miss_rate'):.1f}% in the default design to {100*G('go','final','il1.miss_rate'):.1f}% in the final one). "
        f"After that the changes are small: the three designs at 97 to 98 units are within {100*(g['final']/min(g['g3_best'], g['alt1'], g['alt2'])-1):.1f}% of each other, so we are close to the best that this budget can buy. "
        f"Note that g2_best costs only 77 units and already reaches {g['g2_best']:.3f}, {100*g['g2_best']/g['final']:.0f}% of the final score; the last 21 units give the remaining {100*(1-g['g2_best']/g['final']):.0f}%."])
    d.add_heading("Final design and its cost", 2)
    fd = [c for c in des if c["label"] == "final"][0]["design"]
    W, R, il1, dl1, l2, bp = fd
    dflt = [c for c in des if c["label"] == "default"][0]["design"]
    def costlines(x):
        W, R, il1, dl1, l2, bp = x
        bpc = {"bimod2048": 2, "comb": 6}[bp]
        return [("Width (4 x W)", 4 * W), ("RUU (0.25 x entries)", 0.25 * R), ("L1 instruction cache (1 per KB)", il1[0]), ("L1 data cache (1 per KB)", dl1[0]),
                ("L2 cache (0.125 per KB)", 0.125 * l2[0]), ("Branch predictor", bpc)]
    cd, cf = costlines(dflt), costlines(fd)
    rows = [[a, f"{x:g}", f"{y:g}"] for (a, x), (_, y) in zip(cd, cf)] + [["Total", f"{sum(x for _, x in cd):g}", f"{sum(y for _, y in cf):g}"]]
    assert sum(y for _, y in cf) == 98 and sum(x for _, x in cd) == 86
    table(d, ["Component", "Default cost", "Final cost"], rows, [8.0, 3.4, 3.4], font=9.5, bold_rows=(len(rows) - 1,))
    para(d, f"Final configuration: width {W} (fetch queue, decode, issue, commit and integer ALUs all {W}, {max(1, W//2)} memory ports), RUU {R}, LSQ {R//2}, L1-I {il1[0]} KB {il1[1]}-byte blocks {il1[2]}-way, "
            f"L1-D {dl1[0]} KB {dl1[1]}-byte blocks {dl1[2]}-way, L2 {l2[0]} KB {l2[1]}-byte blocks {l2[2]}-way, combined branch predictor (-bpred:comb 1024). "
            "The dumped configuration is configs/anagram.P6.final.cfg (the go file is the same).")
    d.add_heading("Why we chose it", 2)
    il = lambda b, l: 100 * G(b, l, "il1.miss_rate"); dm = lambda b, l: 100 * G(b, l, "dl1.miss_rate")
    acc = lambda b, l: 100 * G(b, l, "bpred_dir_rate")
    para(d, f"We chose the final design because it has the highest geometric-mean IPC among the designs that fit in 100 units and were run for the full 100 million instructions (anagram {G('anagram','final','sim_IPC'):.3f}, go {G('go','final','sim_IPC'):.3f}, against {G('anagram','default','sim_IPC'):.3f} and {G('go','default','sim_IPC'):.3f} for the default). "
            f"It follows what Parts 2 to 5 taught us. From Part 2 it uses width 8, and from Part 3 we know that a bigger RUU does not help after about 32 entries, so it stops at 32 (cost 8) and does not waste money on 64 or 128. "
            f"From Part 4 it keeps the L2 at 256 KB, because removing it is a disaster for go (its IPC falls by {100*(1-v('go','P4c','mem100_noL2','sim_IPC')/v('go','P4c','mem100_L2','sim_IPC')):.0f}% at 100 cycles of memory latency), and it takes money from the L1-D instead: "
            f"4 KB with 16-byte blocks and 8 ways is enough because the L2 catches the extra misses in 6 cycles (data miss rate of go {dm('go','final'):.2f}% against {dm('go','default'):.2f}%). "
            f"The L1-I cache of go was the real problem, and the 16 KB, 64-byte-block, 4-way instruction cache brings its miss rate from {il('go','default'):.2f}% down to {il('go','final'):.2f}%. "
            f"From Part 5 it spends 4 more units on the combined predictor (accuracy {acc('anagram','final'):.1f}% for anagram and {acc('go','final'):.1f}% for go against {acc('anagram','default'):.1f}% and {acc('go','default'):.1f}%). "
            f"Compared with alt2, which differs only in an 8 KB 4-way L1-D and a 1024-entry bimodal predictor, the final design is {100*(g['final']/g['alt2']-1):.1f}% better: anagram gains ({G('anagram','alt2','sim_IPC'):.3f} to {G('anagram','final','sim_IPC'):.3f}) and go does not ({G('go','alt2','sim_IPC'):.3f} against {G('go','final','sim_IPC'):.3f}). "
            f"(The accuracy of the same predictor is a little different from Part 5 because the machine is now 8-wide with a 32-entry RUU, so the order of lookups and updates in the predictor changes.)")
    para(d, "Limits of our method: a genetic algorithm is random and can end in a local optimum, and we used only a limited set of values for each gene (sizes that are powers of two, a fixed L2 block size of 64 bytes, and 118 simulated designs out of more than a million), so a better design may exist. "
            "The ranking is also for these two benchmarks only, and the search used a 30-million-instruction cap, so the best design of the search and the best design of the full run are not exactly the same. "
            "The final design costs 98 units, so 2 units remain unused.")
    d.add_heading("Bonus", 2)
    para(d, "For the optional bonus (top three designs of the class) our final design is the one above. The best designs of the search and their IPC are listed in data/part6_search_summary.json and data/part6_candidates.csv.")

# ============================================================================ main
def main(parts):
    d = new_document()
    cover(d); page_break(d)
    setup_section(d)
    for name in parts:
        globals()[name](d)
    page_numbers(d, f"Computer Architecture BCS-5F  |  Project report  |  Group {GROUP}")
    path = os.path.join(OUTDIR, f"Project_Report_G{GROUP}.docx")
    d.save(path); print("saved", path)

if __name__ == "__main__":
    main([a for a in sys.argv[1:]] or ["part1", "part2", "part3", "part4", "part5", "part6"])
