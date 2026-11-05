"""Apply the pre-registered pick rule and write report.json."""
import sys, json, math, itertools
sys.path.insert(0, "/tmp/claude-0/-home-user-Mobil/b5a09aa0-3ae1-547d-aca0-e9005dcfc1f6/scratchpad/agent_lab")
import numpy as np
from lab_common import load, ordered, indicator, corr, LAB, N, K
import lab_stats as S

rng = np.random.default_rng(6112026)
rows = load("all"); B = ordered(rows); X = indicator(B); nd = len(B)
years = np.array([r["date"].year for r in rows]); uy = np.unique(years)
Y = np.stack([(years == u).astype(float) for u in uy], 1)
dep = np.array([r["deposits"] for r in rows])


def ridge(Xn, y, Yd, lam=1.0):
    D = np.hstack([Xn, Yd])
    P = np.diag(np.r_[np.full(N, lam), np.full(Yd.shape[1], 1e-6)])
    c = np.linalg.solve(D.T @ D + P, D.T @ y)
    return c[:N] - c[:N].mean()


y3 = np.log(np.array([r["w3"] for r in rows]) / dep)
yp4 = np.log(np.array([r["p4"] for r in rows]))
beta = ridge(X, y3, Y)          # popularity (higher = more co-winners)
gam = ridge(X, yp4, Y)          # effect on 4-hit prize (higher = bigger prize)
tr_beta = np.array(json.load(open(LAB + "/train_results.json"))["results"]["P1"]["beta"])
hm = years >= 2024
beta_hold_only = ridge(X[hm], y3[hm], Y[hm][:, np.isin(uy, [2024, 2025, 2026])])

# enumerate all 5-subsets
combs = np.array(list(itertools.combinations(range(1, N + 1), K)))
sb = beta[combs - 1].sum(1)
d = np.diff(combs, axis=1)
consec = (d == 1).any(1)
arith = (d == d[:, :1]).all(1)
ok = ~consec & ~arith
best_idx = np.where(ok)[0][np.argmin(sb[ok])]
pick = combs[best_idx]

# bootstrap stability of the pick rule
cnt = np.zeros(N)
for _ in range(300):
    idx = rng.integers(0, nd, nd)
    bb = ridge(X[idx], y3[idx], Y[idx])
    s = bb[combs[ok] - 1].sum(1)
    cnt[combs[ok][np.argmin(s)] - 1] += 1


# multipliers relative to an average random ticket
def lse(v):
    m = v.max(); return m + math.log(np.exp(v - m).mean())


w3_mult = math.exp(sb[best_idx] - lse(sb))  # predicted co-winner density if drawn set == pick
# 4-hit prize: drawn set = pick minus one + one other number
pset = set(pick.tolist()); others = [n for n in range(1, N + 1) if n not in pset]
vals = [gam[[q - 1 for q in pick if q != drop] + [o - 1]].sum() for drop in pick for o in others]
p4_mult = math.exp(lse(np.array(vals)) - lse(gam[combs - 1].sum(1)))


# holdout calibration slope (train-fitted prediction vs year-demeaned holdout actual) used to shrink the multipliers
def calib_slope(yy):
    tm = years <= 2023
    g = ridge(X[tm], yy[tm], Y[tm][:, uy <= 2023])
    act = yy[~tm].copy()
    for u in uy[uy >= 2024]:
        m = years[~tm] == u; act[m] -= act[m].mean()
    return float(np.polyfit(X[~tm] @ g, act, 1)[0])


slope3, slope4 = calib_slope(y3), calib_slope(yp4)
w3_mult_cal = math.exp(slope3 * math.log(w3_mult))
p4_mult_cal = math.exp(slope4 * math.log(p4_mult))

ho = json.load(open(LAB + "/holdout_results.json"))
table = ho["table"]
draw_models = [t for t in table if t["id"] in ("M1", "M2")]
m1 = next(t for t in table if t["id"] == "M1"); m2 = next(t for t in table if t["id"] == "M2")
p1 = next(t for t in table if t["id"] == "P1")
w_pl = np.array(ho["M2_w_all"])

report = dict(
    protocol="prereg.json written before holdout access (timestamps in prereg_timestamp.txt); train 2018-01-03..2023-12-31 (626 draws), holdout 2024-01-01..2026-11-04 (382 draws); Holm over 29 tests on train p and separately on holdout p; survival requires both Holm p<0.05.",
    hypotheses=[dict(name=f"{t['id']} {t['name']}", train_effect=t["train_effect"], train_p=t["train_p"], train_p_holm=t["train_p_holm"],
                     holdout_effect=t["holdout_effect"], holdout_replicates=t["holdout_replicates"], holdout_p=t["holdout_p"],
                     holdout_p_holm=t["holdout_p_holm"], survives=t["survives"]) for t in table],
    best_model=dict(
        draw_prediction=dict(name="none beats random; best nominal = M1 Dirichlet exponential forgetting (half-life 3 draws, beta +0.05)",
                             holdout_mean_hits=round(float(np.mean(ho["M1_hits"])), 4), random_baseline=round(25 / 35, 4),
                             holdout_z=float(m1["holdout_effect"].split("z=")[1].split(",")[0]), holdout_p_one_sided=m1["holdout_p"],
                             runner_up=f"M2 Plackett-Luce order weights: {m2['holdout_effect']}"),
        payout=dict(name="P1 player-popularity ridge model (predicts number of co-winners, not the draw)",
                    holdout=p1["holdout_effect"], holdout_p=p1["holdout_p"],
                    fisher_z=round(math.atanh(0.594) * math.sqrt(382 - 3), 1))),
    pick_for_2026_11_06=sorted(int(v) for v in pick),
    pick_derivation=dict(
        rule="pre-registered: no draw hypothesis survived, so choose the 5-subset with the lowest predicted player popularity (sum of P1 betas, refit on all 1008 draws), excluding sets with consecutive numbers or arithmetic progressions",
        popularity_beta_by_number={int(n): round(float(beta[n - 1]), 4) for n in range(1, N + 1)},
        least_popular_10=(np.argsort(beta)[:10] + 1).tolist(), most_popular_10=(np.argsort(-beta)[:10] + 1).tolist(),
        corr_train_beta_vs_holdout_only_beta=round(corr(tr_beta, beta_hold_only), 3),
        bootstrap_inclusion_freq_top={int(n + 1): round(float(cnt[n] / 300), 2) for n in np.argsort(-cnt)[:10]},
        predicted_cowinner_density_vs_average_ticket=round(w3_mult, 3),
        predicted_4hit_prize_multiplier_vs_average_ticket=round(p4_mult, 3),
        holdout_calibration_slopes=dict(log_w3_per_deposit=round(slope3, 2), log_4hit_prize=round(slope4, 2)),
        calibrated_cowinner_density_vs_average_ticket=round(w3_mult_cal, 3),
        calibrated_4hit_prize_multiplier_vs_average_ticket=round(p4_mult_cal, 3),
        for_reference_PL_top5_all_data=sorted((np.argsort(-w_pl)[:5] + 1).tolist())),
    exploratory=ho["exploratory"],
    confidence_statement=("The pick has the same 1-in-324,632 jackpot chance and the same 0.714 expected matched numbers as any other ticket "
                          "(no draw-prediction hypothesis survived holdout plus Holm correction); its only validated advantage is that "
                          f"its numbers are less popular with other players, so if it wins, prizes are predicted to be shared with fewer people "
                          f"(after holdout-calibrated shrinkage: about {100*(1-w3_mult_cal):.0f}% fewer co-winners and about {p4_mult_cal:.2f}x the average 4-hit prize; "
                          "the 3-hit prize is fixed and unaffected)."),
)
json.dump(report, open(LAB + "/report.json", "w"), indent=1, ensure_ascii=False)
print("pick", report["pick_for_2026_11_06"], "sum beta", round(float(sb[best_idx]), 3))
print(json.dumps(report["pick_derivation"], indent=1))
print(report["confidence_statement"])
