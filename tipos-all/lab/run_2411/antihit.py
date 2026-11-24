"""VAN anti-hit walk-forward test (pre-registered in antihit_prereg.md).

Run: python3 -I antihit.py   (numpy only, fixed seeds)
"""
import json
import math
import os
import hashlib

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "run_2311", "data", "van.json")
SEED = 20261124
START = 31  # first evaluated draw, 1-indexed
NUMS = np.arange(1, 23)
EXTRA = [
    {"date": "2026-11-23", "main": [1, 5, 6, 8, 9, 10, 13, 14, 15, 18, 21], "order": None},
    {"date": "2026-11-24", "main": [1, 2, 4, 6, 7, 14, 15, 17, 20, 21, 22], "order": None},
]
PRIZE = {0: 100000.0, 1: 200.0, 2: 20.0, 3: 3.0, 8: 3.0, 9: 20.0, 10: 200.0, 11: 100000.0}
COST = 1.50
ALPHA = 0.05

# ---------- data ----------
raw = open(DATA, "rb").read()
sha = hashlib.sha256(raw).hexdigest()
draws = [{"date": d["date"], "main": d["main"], "order": d.get("order")} for d in json.loads(raw)]
assert len(draws) == 410
draws += EXTRA
T = len(draws)
for d in draws:
    assert len(set(d["main"])) == 11 and all(1 <= x <= 22 for x in d["main"])
    if d["order"] is not None:
        assert sorted(d["order"]) == sorted(d["main"])
assert [d["date"] for d in draws] == sorted(d["date"] for d in draws)
mainsets = [set(d["main"]) for d in draws]
ind = np.zeros((T, 23), dtype=int)
for i, s in enumerate(mainsets):
    ind[i, list(s)] = 1

# ---------- null distribution ----------
C22 = math.comb(22, 11)
pmf_counts = [math.comb(11, h) * math.comb(11, 11 - h) for h in range(12)]
assert sum(pmf_counts) == C22
pmf = np.array(pmf_counts, dtype=float) / C22
MU = 5.5
VAR = 11 * (11 / 22) * (11 / 22) * (11 / 21)
assert abs((pmf * np.arange(12)).sum() - MU) < 1e-12
assert abs((pmf * (np.arange(12) - MU) ** 2).sum() - VAR) < 1e-12
P_LE3 = sum(pmf_counts[:4]) / C22
P0 = 1 / C22
EV_TICKET = sum(PRIZE.get(h, 0.0) * pmf[h] for h in range(12))


def sum_pmf(n):
    out = np.array([1.0])
    for _ in range(n):
        out = np.convolve(out, pmf)
    return out


def binom_sf(x, n, p):
    """P(X >= x)."""
    return float(sum(math.comb(n, j) * p ** j * (1 - p) ** (n - j) for j in range(x, n + 1)))


def holm(pvals):
    m = len(pvals)
    idx = sorted(range(m), key=lambda i: pvals[i])
    adj = [0.0] * m
    run = 0.0
    for rank, i in enumerate(idx):
        run = max(run, min(1.0, (m - rank) * pvals[i]))
        adj[i] = run
    return adj


# ---------- rules ----------
def prio(r, t):
    """priority (lower = first) for tie-breaking, index by number 1..22."""
    perm = np.random.default_rng([SEED, r, t]).permutation(22)
    p = np.empty(23, dtype=int)
    p[0] = 10**6
    p[1:] = perm
    return p


def by_freq(t, k, r, least):
    lo = 0 if k is None else max(0, t - 1 - k)
    cnt = ind[lo:t - 1].sum(axis=0)  # draws lo..t-2 (0-idx) = draws < t
    pr = prio(r, t)
    key = sorted(NUMS.tolist(), key=lambda x: ((cnt[x] if least else -cnt[x]), pr[x]))
    return sorted(key[:11])


def complement(s):
    return sorted(set(range(1, 23)) - set(s))


def rule_ticket(r, t):
    """t is 1-indexed draw number; returns ticket or None if not evaluable."""
    prev = draws[t - 2]
    if r == 1:
        return complement(prev["main"])
    if r == 2:
        return complement(draws[t - 3]["main"])
    if r in (3, 4, 5, 6):
        return by_freq(t, {3: 5, 4: 10, 5: 30, 6: None}[r], r, least=True)
    if r in (7, 8, 9, 10):
        return by_freq(t, {7: 5, 8: 10, 9: 30, 10: None}[r], r, least=False)
    if r == 11:
        # current gap = draws since last appearance; keep the 11 smallest gaps
        gap = {}
        for x in range(1, 23):
            g = None
            for j in range(t - 2, -1, -1):
                if x in mainsets[j]:
                    g = (t - 2) - j
                    break
            gap[x] = g if g is not None else 10**6
        pr = prio(r, t)
        return sorted(sorted(range(1, 23), key=lambda x: (gap[x], pr[x]))[:11])
    if r == 12:
        if prev["order"] is None:
            return None
        late = prev["order"][5:11]  # positions 6..11
        rest = complement(prev["main"])
        fill = np.random.default_rng([SEED, 12, t]).choice(rest, size=5, replace=False).tolist()
        return sorted(late + [int(v) for v in fill])
    if r == 13:
        return sorted((np.random.default_rng([SEED, 13, t]).choice(22, size=11, replace=False) + 1).tolist())
    raise ValueError(r)


NAMES = {
    1: "complement of previous draw",
    2: "complement of draw t-2",
    3: "11 least-frequent, last 5",
    4: "11 least-frequent, last 10",
    5: "11 least-frequent, last 30",
    6: "11 least-frequent, all past",
    7: "11 most-frequent, last 5",
    8: "11 most-frequent, last 10",
    9: "11 most-frequent, last 30",
    10: "11 most-frequent, all past",
    11: "11 most recently drawn (= previous draw)",
    12: "late half of prev order (pos 6-11) + 5 random non-drawn",
    13: "random ticket (negative control)",
}

# ---------- walk-forward ----------
SUMPMF = {}
results = {}
for r in range(1, 14):
    hits, dates = [], []
    for t in range(START, T + 1):
        tk = rule_ticket(r, t)
        if tk is None:
            continue
        assert len(tk) == 11 and len(set(tk)) == 11
        hits.append(len(set(tk) & mainsets[t - 1]))
        dates.append(draws[t - 1]["date"])
    h = np.array(hits)
    n = len(h)
    if n not in SUMPMF:
        SUMPMF[n] = sum_pmf(n)
    sp = SUMPMF[n]
    assert abs(sp.sum() - 1) < 1e-9
    S = int(h.sum())
    p_low = float(min(1.0, sp[: S + 1].sum()))
    p_high = float(min(1.0, sp[S:].sum()))
    le3 = int((h <= 3).sum())
    zero = int((h == 0).sum())
    won_low = float(sum(PRIZE.get(int(x), 0.0) for x in h if x <= 3))
    won_high = float(sum(PRIZE.get(int(x), 0.0) for x in h if x >= 8))
    results[r] = {
        "rule": f"R{r}",
        "name": NAMES[r],
        "n": n,
        "first_date": dates[0],
        "last_date": dates[-1],
        "mean_hits": float(h.mean()),
        "sd_hits": float(h.std(ddof=1)),
        "z": float((h.mean() - MU) / math.sqrt(VAR / n)),
        "p_mean_lt_5_5": p_low,
        "p_mean_gt_5_5_descriptive": p_high,
        "n_hits_le3": le3,
        "expected_le3": n * P_LE3,
        "p_le3_binom": binom_sf(le3, n, P_LE3),
        "n_zero_hits": zero,
        "expected_zero": n * P0,
        "hist": [int((h == k).sum()) for k in range(12)],
        "won_low_side_eur": won_low,
        "won_high_side_eur": won_high,
        "won_total_eur": won_low + won_high,
        "cost_eur": n * COST,
        "net_eur": won_low + won_high - n * COST,
        "expected_won_eur_null": n * EV_TICKET,
        "expected_won_eur_null_ex_jackpot": n * (EV_TICKET - 2 * PRIZE[0] * P0),
        "next_ticket_2026_11_25": rule_ticket(r, T + 1) if r != 12 else None,
    }

fam = list(range(1, 13))
adj1 = holm([results[r]["p_mean_lt_5_5"] for r in fam])
adj2 = holm([results[r]["p_le3_binom"] for r in fam])
for r, a1, a2 in zip(fam, adj1, adj2):
    results[r]["holm_p_mean"] = a1
    results[r]["holm_p_le3"] = a2
    results[r]["survives_primary"] = a1 < ALPHA
    results[r]["survives_secondary"] = a2 < ALPHA
for k in ("holm_p_mean", "holm_p_le3", "survives_primary", "survives_secondary"):
    results[13][k] = None

survivors = [f"R{r}" for r in fam if results[r]["survives_primary"]]
survivors2 = [f"R{r}" for r in fam if results[r]["survives_secondary"]]
corr_r1_r11 = all(
    a + b == 11
    for a, b in zip(
        [len(set(rule_ticket(1, t)) & mainsets[t - 1]) for t in range(START, T + 1)],
        [len(set(rule_ticket(11, t)) & mainsets[t - 1]) for t in range(START, T + 1)],
    )
)

out = {
    "prereg": "antihit_prereg.md",
    "data": {"file": "run_2311/data/van.json", "sha256": sha, "n_draws": T,
             "appended": [e["date"] for e in EXTRA], "first": draws[0]["date"], "last": draws[-1]["date"]},
    "seed": SEED,
    "eval": {"start_draw": START, "n": T - START + 1},
    "null": {"mean": MU, "var": VAR, "pmf": pmf.tolist(), "P_le3": P_LE3, "P_zero": P0,
             "ev_per_ticket_eur": EV_TICKET, "cost": COST},
    "check_hits_R1_plus_R11_eq_11": corr_r1_r11,
    "survivors_primary_holm": survivors,
    "survivors_secondary_holm": survivors2,
    "rules": [results[r] for r in range(1, 14)],
}
with open(os.path.join(HERE, "antihit.json"), "w") as f:
    json.dump(out, f, indent=1)

# ---------- markdown ----------
L = []
L.append("# VAN anti-hit walk-forward test: results\n")
L.append(f"Pre-registration: `antihit_prereg.md` (written before any result). Data sha256 `{sha[:16]}…`, "
         f"{T} draws {draws[0]['date']}..{draws[-1]['date']} (2 appended). Evaluation draws t = {START}..{T} "
         f"(n = {T - START + 1}; R12 n = {results[12]['n']}). Seed {SEED}.\n")
L.append(f"Null: hits ~ hypergeometric(22, 11, 11), mean 5.5, var {VAR:.6f}; P(hits<=3) = {P_LE3:.5f}; "
         f"P(0 hits) = 1/{C22}. Expected winnings under null = {EV_TICKET:.4f} € per 1.50 € ticket.\n")
L.append("## Primary: mean hits < 5.5 (exact one-sided, Holm over R1-R12)\n")
L.append("| Rule | Description | n | mean hits | z | p (mean<5.5) | Holm p | survives |")
L.append("|---|---|---:|---:|---:|---:|---:|:---:|")
for r in range(1, 14):
    x = results[r]
    hp = "—" if x["holm_p_mean"] is None else f"{x['holm_p_mean']:.3f}"
    sv = "control" if r == 13 else ("YES" if x["survives_primary"] else "no")
    L.append(f"| R{r} | {x['name']} | {x['n']} | {x['mean_hits']:.3f} | {x['z']:+.2f} | "
             f"{x['p_mean_lt_5_5']:.3f} | {hp} | {sv} |")
L.append("")
L.append("## Secondary: draws with 0-3 hits, exact 0-hit draws\n")
L.append("| Rule | hits<=3 obs | expected | p (binom, >=) | Holm p | 0-hit draws (exp.) | hit histogram 0..11 |")
L.append("|---|---:|---:|---:|---:|---:|---|")
for r in range(1, 14):
    x = results[r]
    hp = "—" if x["holm_p_le3"] is None else f"{x['holm_p_le3']:.3f}"
    L.append(f"| R{r} | {x['n_hits_le3']} | {x['expected_le3']:.1f} | {x['p_le3_binom']:.3f} | {hp} | "
             f"{x['n_zero_hits']} ({x['expected_zero']:.4f}) | {' '.join(map(str, x['hist']))} |")
L.append("")
L.append("## Money (1 ticket per draw, nominal prize table, top prize counted at full 100 000 €)\n")
L.append(f"Expected under null includes the jackpot EV (2 x 100 000 €/{C22} = {2 * PRIZE[0] * P0:.4f} € per ticket); "
         f"no rule hit 0 or 11, so the comparable figure without jackpot is {results[1]['expected_won_eur_null_ex_jackpot']:.0f} € "
         f"for n = 382.\n")
L.append("| Rule | won 0-3 side € | won 8-11 side € | total won € | expected under null € | cost € | net € |")
L.append("|---|---:|---:|---:|---:|---:|---:|")
for r in range(1, 14):
    x = results[r]
    L.append(f"| R{r} | {x['won_low_side_eur']:.0f} | {x['won_high_side_eur']:.0f} | {x['won_total_eur']:.0f} | "
             f"{x['expected_won_eur_null']:.0f} | {x['cost_eur']:.0f} | {x['net_eur']:+.0f} |")
L.append("")
L.append("## Conclusion\n")
L.append(f"- Rules surviving Holm (primary, mean hits < 5.5): {', '.join(survivors) if survivors else 'none'}.")
L.append(f"- Rules surviving Holm (secondary, excess of 0-3 hit draws): {', '.join(survivors2) if survivors2 else 'none'}.")
L.append(f"- Check: hits(R1) + hits(R11) = 11 on every draw: {corr_r1_r11} (R11 is the previous draw itself).")
L.append("- The p-value of the negative control R13 shows the spread expected by chance alone.")
with open(os.path.join(HERE, "antihit.md"), "w") as f:
    f.write("\n".join(L) + "\n")

for r in range(1, 14):
    x = results[r]
    print(f"R{r:<2} n={x['n']} mean={x['mean_hits']:.3f} z={x['z']:+.2f} p={x['p_mean_lt_5_5']:.4f} "
          f"holm={x['holm_p_mean']} le3={x['n_hits_le3']}/{x['expected_le3']:.1f} p3={x['p_le3_binom']:.3f} "
          f"zero={x['n_zero_hits']} won={x['won_total_eur']:.0f} cost={x['cost_eur']:.0f}")
print("survivors:", survivors, survivors2, "R1+R11==11:", corr_r1_r11)
