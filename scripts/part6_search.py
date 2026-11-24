#!/usr/bin/env python3
"""part6_search.py - search for the fastest processor within 100 cost units (Part 6).

Cost model (from the project PDF):
  width W:       4*W            (ifqsize = decode = issue = commit = ialu = W, memport = max(1, W/2))
  RUU:           0.25 per entry (LSQ = RUU/2)
  L1-I, L1-D:    1 per KB
  unified L2:    0.125 per KB, or none
  predictor:     nottaken 0 | bimod 1 per 1024 entries | 2lev 1 1024 8 0 = 3 | comb (default sizes) = 6
Score = geometric mean of IPC over anagram and go.

Method: genetic algorithm (population 14, 10 generations, tournament selection, uniform crossover, mutation,
2 elites, fixed random seed 13). A design is 6 genes: width, RUU, L1-I, L1-D, L2, predictor; designs that cost more
than 100 are never accepted. Fitness = geometric-mean IPC.
The search uses a shorter cap (P6_CAP, default 30M instructions) to save time; the finalists are
re-run with the full 100M cap and the final answer is chosen from those.

Usage: SIM=... BENCH=... python3 scripts/part6_search.py search|finalize
"""
import concurrent.futures as cf, json, math, os, re, shutil, subprocess, sys, tempfile, itertools

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SIM = os.environ.get("SIM", os.path.join(ROOT, "simplesim-3.0", "sim-outorder"))
BENCH = os.environ.get("BENCH", os.path.join(ROOT, "bench"))
if not os.path.isdir(os.path.join(BENCH, "Input")) and os.path.isdir(os.path.join(BENCH, "BenchMarks_Little", "Input")):
    BENCH = os.path.join(BENCH, "BenchMarks_Little")
JOBS = int(os.environ.get("JOBS", "2"))
BENCHES = ["anagram", "go"]
SDIR = os.path.join(ROOT, "search_runs")
CACHE = os.path.join(ROOT, "data", "part6_search_cache.json")
BUDGET = 100.0

BPCOST = {"nottaken": 0, "bimod512": 0.5, "bimod1024": 1, "bimod2048": 2, "bimod4096": 4, "2lev": 3, "comb": 6}
BPOPT = {"nottaken": ["-bpred", "nottaken"],
         "bimod512": ["-bpred", "bimod", "-bpred:bimod", "512"],
         "bimod1024": ["-bpred", "bimod", "-bpred:bimod", "1024"],
         "bimod2048": ["-bpred", "bimod", "-bpred:bimod", "2048"],
         "bimod4096": ["-bpred", "bimod", "-bpred:bimod", "4096"],
         "2lev": ["-bpred", "2lev", "-bpred:2lev", "1", "1024", "8", "0"],
         "comb": ["-bpred", "comb", "-bpred:comb", "1024"]}

# a design = (W, RUU, il1=(KB, block, assoc), dl1=(KB, block, assoc), l2=None|(KB, block, assoc), bpred)
DEFAULT = (4, 16, (16, 32, 1), (16, 32, 4), (256, 64, 4), "bimod2048")

W_OPT = [2, 4, 8]
R_OPT = [16, 32, 64, 128]
KB_OPT = [4, 8, 16, 32, 64]
IBS_OPT, IAS_OPT = [32, 64], [1, 2, 4]
DBS_OPT, DAS_OPT = [16, 32, 64], [2, 4, 8]
L2_OPT = [None, 64, 128, 256, 512]
BP_OPT = list(BPCOST)

def cost(d):
    W, R, il1, dl1, l2, bp = d
    return 4 * W + 0.25 * R + il1[0] + dl1[0] + (0.125 * l2[0] if l2 else 0) + BPCOST[bp]

def cache_str(name, c):
    kb, bs, a = c
    return f"{name}:{kb * 1024 // (bs * a)}:{bs}:{a}:l"

def options(d):
    W, R, il1, dl1, l2, bp = d
    o = ["-fetch:ifqsize", W, "-decode:width", W, "-issue:width", W, "-commit:width", W, "-res:ialu", W,
         "-res:memport", max(1, W // 2), "-ruu:size", R, "-lsq:size", R // 2,
         "-cache:il1", cache_str("il1", il1), "-cache:dl1", cache_str("dl1", dl1)]
    if l2:
        o += ["-cache:dl2", cache_str("ul2", l2)]
    else:
        o += ["-cache:dl2", "none", "-cache:il2", "none"]
    return [str(x) for x in o + BPOPT[bp]]

def key(d, cap):
    return json.dumps([d, cap], default=list)

# ------------------------------------------------------------------ running the simulator
def run_sim(bench, opts, cap, out):
    tmp = tempfile.mkdtemp()
    try:
        for f in ("words", "anagram.in", "1stmt.i", "2stone9.in", "compress95.in"):
            shutil.copy(os.path.join(BENCH, "Input", f), tmp)
        if bench == "anagram":
            prog, args, stdin = os.path.join(BENCH, "Programs/anagram.ss"), ["words"], "anagram.in"
        else:
            prog, args, stdin = os.path.join(BENCH, "Programs/go.ss"), ["50", "9", "2stone9.in"], "/dev/null"
        cmd = ["env", "-i", SIM, "-max:inst", str(cap)] + opts + ["-redir:sim", out, prog] + args
        with open(os.path.join(tmp, stdin) if stdin != "/dev/null" else stdin) as fin:
            subprocess.run(cmd, cwd=tmp, stdin=fin, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for line in open(out):
        m = re.match(r"sim_IPC\s+([0-9.]+)", line)
        if m:
            return float(m.group(1))
    raise RuntimeError("no sim_IPC in " + out)

def load_cache():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else {}

def save_cache(c):
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    json.dump(c, open(CACHE, "w"), indent=0)

def evaluate(designs, cap):
    """Return {design: (ipc_anagram, ipc_go, geomean)}; runs only what is not cached."""
    cache = load_cache()
    todo = [(d, b) for d in designs for b in BENCHES if f"{key(d, cap)}|{b}" not in cache]
    os.makedirs(SDIR, exist_ok=True)
    def job(t):
        d, b = t
        out = os.path.join(SDIR, f"{b}.cap{cap // 1000000}M.{abs(hash(key(d, cap))) % 10**10}.txt")
        return t, run_sim(b, options(d), cap, out)
    with cf.ThreadPoolExecutor(JOBS) as ex:
        for (d, b), ipc in ex.map(job, todo):
            cache[f"{key(d, cap)}|{b}"] = ipc
    save_cache(cache)
    res = {}
    for d in designs:
        a, c = (cache[f"{key(d, cap)}|{b}"] for b in BENCHES)
        res[d] = (a, c, math.sqrt(a * c))
    return res

# ------------------------------------------------------------------ genetic algorithm
import random
POP, GENS, ELITE, TOURN, PMUT = 14, 10, 2, 3, 0.25
SEED = 13          # our group number, so the search can be repeated exactly

def random_gene(i, d, rng):
    """A new random value for gene i of design d (caches: one field at a time)."""
    W, R, il1, dl1, l2, bp = d
    if i == 0: return rng.choice(W_OPT)
    if i == 1: return rng.choice(R_OPT)
    if i == 2:
        f = rng.randrange(3)
        return (rng.choice(KB_OPT) if f == 0 else il1[0], rng.choice(IBS_OPT) if f == 1 else il1[1], rng.choice(IAS_OPT) if f == 2 else il1[2])
    if i == 3:
        f = rng.randrange(3)
        return (rng.choice(KB_OPT) if f == 0 else dl1[0], rng.choice(DBS_OPT) if f == 1 else dl1[1], rng.choice(DAS_OPT) if f == 2 else dl1[2])
    if i == 4:
        n = rng.choice(L2_OPT)
        return (n, 64, 4) if n else None
    return rng.choice(BP_OPT)

def random_design(rng):
    while True:
        d = (rng.choice(W_OPT), rng.choice(R_OPT), (rng.choice(KB_OPT), rng.choice(IBS_OPT), rng.choice(IAS_OPT)),
             (rng.choice(KB_OPT), rng.choice(DBS_OPT), rng.choice(DAS_OPT)), random_gene(4, DEFAULT, rng), rng.choice(BP_OPT))
        if 70 <= cost(d) <= BUDGET:       # random starting designs: feasible and not trivially cheap
            return d

def child_of(p1, p2, rng):
    """Uniform crossover of the 6 genes, then mutation; only feasible children (cost <= 100) are accepted."""
    for _ in range(60):
        c = [p1[i] if rng.random() < 0.5 else p2[i] for i in range(6)]
        for i in range(6):
            if rng.random() < PMUT:
                c[i] = random_gene(i, tuple(c), rng)
        c = tuple(c)
        if cost(c) <= BUDGET:
            return c
    return p1

def search(cap):
    """Genetic algorithm. Fitness = geometric-mean IPC of the two benchmarks (30M-instruction runs).
    Population 14, 10 generations, tournament selection (size 3), uniform crossover, mutation, 2 elites."""
    rng = random.Random(SEED)
    pop = [DEFAULT]
    while len(pop) < POP:
        d = random_design(rng)
        if d not in pop: pop.append(d)
    allres, best_path, log = {}, [], []
    best_so_far = None
    for g in range(GENS + 1):
        res = evaluate(pop, cap); allres.update(res)
        ranked = sorted(pop, key=lambda d: -res[d][2])
        top = ranked[0]
        mean = sum(res[d][2] for d in pop) / len(pop)
        if best_so_far is None or res[top][2] > allres[best_so_far][2]:
            best_so_far = top; best_path.append(top)
        log.append({"generation": g, "best": res[top][2], "mean": mean, "best_design": name_of(top), "evaluated_so_far": len(allres)})
        print(f"generation {g}: best {res[top][2]:.4f} cost {cost(top):.1f} {name_of(top)}  mean {mean:.4f}  (designs run so far: {len(allres)})", flush=True)
        if g == GENS: break
        nxt = ranked[:ELITE]
        pick = lambda: max(rng.sample(pop, TOURN), key=lambda d: res[d][2])
        guard = 0
        while len(nxt) < POP and guard < 500:
            guard += 1
            c = child_of(pick(), pick(), rng)
            if c not in nxt: nxt.append(c)
        pop = nxt
    search.log = log
    return [DEFAULT] + [p for p in best_path if p != DEFAULT], allres

# ------------------------------------------------------------------ main
def name_of(d):
    W, R, il1, dl1, l2, bp = d
    l2s = f"L2{l2[0]}K" if l2 else "noL2"
    return f"W{W}_R{R}_I{il1[0]}K{il1[1]}B{il1[2]}w_D{dl1[0]}K{dl1[1]}B{dl1[2]}w_{l2s}_{bp}"

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "search"
    if mode == "search":
        cap = int(os.environ.get("P6_CAP", 30000000))
        path, allres = search(cap)
        # finalists: the path plus the 8 best feasible designs seen; re-run them with the full 100M cap
        top = sorted((d for d in allres if cost(d) <= BUDGET), key=lambda d: -allres[d][2])[:8]
        fin = list(dict.fromkeys(path + top))
        full = evaluate(fin, 100000000)
        json.dump({"method": "genetic algorithm", "generations": search.log, "path": [list(p) for p in path],
                   "finalists": [[list(d) if not isinstance(d, str) else d for d in fin]],
                   "full": {name_of(d): full[d] for d in fin}},
                  open(os.path.join(ROOT, "data", "part6_search_summary.json"), "w"), default=list, indent=1)
        for d in sorted(fin, key=lambda d: -full[d][2]):
            print(f"{full[d][2]:.4f}  cost {cost(d):6.2f}  {name_of(d)}  (anagram {full[d][0]:.3f}, go {full[d][1]:.3f})")
