"""Shared data loading and helpers for the Loto 5z35 lab. numpy only."""
import json, datetime, math
import numpy as np

DATA = "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/data/all/l535.json"
LAB = "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab"
N = 35
K = 5
TRAIN_END = "2023-12-31"
HOLD_START = "2024-01-01"
SEG7 = {0: 6, 1: 2, 2: 5, 3: 5, 4: 4, 5: 5, 6: 6, 7: 3, 8: 7, 9: 6}


def eur(s):
    s = s.strip()
    if s.replace("€", "").strip() == "":
        return float("nan")
    return float(s.replace("€", "").replace("\xa0", "").replace(" ", "").replace(",", "."))


def load(split="all"):
    raw = json.load(open(DATA))
    rows = []
    for x in raw:
        if split == "train" and x["date"] > TRAIN_END:
            continue
        if split == "holdout" and x["date"] < HOLD_START:
            continue
        r = x["raw"]
        lot = r["TabulkaVyhier"]["Loteria"]
        rows.append(dict(
            date=datetime.date.fromisoformat(x["date"]),
            balls=[int(v) for v in r["Zrebovanie"]],
            joker=[int(v) for v in r["ZrebovanieJoker"]],
            wd=datetime.date.fromisoformat(x["date"]).weekday(),
            deposits=eur(r["SumOfDeposits"]),
            jackpot=eur(r["Jackpot"]),
            w5=int(lot[0]["PocetVyhier"]), w4=int(lot[1]["PocetVyhier"]), w3=int(lot[2]["PocetVyhier"]),
            p4=eur(lot[1]["VyskaVyhry"]), p5=eur(lot[0]["VyskaVyhry"]),
        ))
    return rows


def ordered(rows):
    """(ndraw,5) int array of balls in drawn order (1..35)."""
    return np.array([r["balls"] for r in rows], dtype=int)


def indicator(B):
    """(ndraw,35) 0/1 inclusion matrix from (ndraw,5) balls."""
    X = np.zeros((B.shape[0], N), dtype=float)
    X[np.arange(B.shape[0])[:, None], B - 1] = 1
    return X


def shuffle_within(B, rng):
    """Random permutation of order inside each draw (exact null for order effects)."""
    idx = np.argsort(rng.random(B.shape), axis=1)
    return np.take_along_axis(B, idx, axis=1)


def random_draws(n, rng):
    """n uniform ordered draws (n,5) without replacement from 1..35."""
    return np.argsort(rng.random((n, N)), axis=1)[:, :K] + 1


def moon_age(d):
    ref = datetime.datetime(2000, 1, 6, 18, 14)
    t = datetime.datetime(d.year, d.month, d.day, 18, 0) - datetime.timedelta(hours=1)  # ~18:00 CET -> UTC
    days = (t - ref).total_seconds() / 86400.0
    return days % 29.530588853


def digital_root(n):
    return 0 if n == 0 else 1 + (n - 1) % 9


def date_root(d):
    s = sum(int(c) for c in d.strftime("%Y%m%d"))
    return digital_root(s)


def ink(n):
    return sum(SEG7[int(c)] for c in str(n))


def corr(a, b):
    a = np.asarray(a, float) - np.mean(a)
    b = np.asarray(b, float) - np.mean(b)
    den = math.sqrt((a * a).sum() * (b * b).sum())
    return float((a * b).sum() / den) if den > 0 else 0.0


def mc_p(obs, null, side="two"):
    null = np.asarray(null)
    if side == "greater":
        return float((1 + np.sum(null >= obs)) / (1 + len(null)))
    if side == "less":
        return float((1 + np.sum(null <= obs)) / (1 + len(null)))
    m = np.mean(null)
    return float((1 + np.sum(np.abs(null - m) >= abs(obs - m))) / (1 + len(null)))


def holm(pvals):
    p = np.asarray(pvals, float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    run = 0.0
    for i, j in enumerate(order):
        run = max(run, (m - i) * p[j])
        adj[j] = min(1.0, run)
    return adj
