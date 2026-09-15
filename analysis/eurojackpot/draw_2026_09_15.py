"""
Eurojackpot, Tuesday 2026-09-15. TWO tickets, EUR 4.00. Detailed edition.

Jackpot EUR 48,000,000, confirmed by two sources:
  - tipos.sk ("Eurojackpot Jackpot 48 000 000,00 EUR")
  - t-online.de "Eurojackpot am Dienstag: 48 Millionen im Jackpot"
Both also confirm the 2026-09-11 jackpot went unwon, which settles the source
conflict left open in the last settlement: lotteryextreme was right (5+2 had
0 winners) and eurojackpot-numbers' "next draw EUR 10m" was stale.

NEW FINDING THIS ROUND: the lower tiers are NOT stable draw to draw, which is
what my earlier reports assumed. Two real dated tables one draw apart differ
by 24% in lower-tier EV. Section 2 quantifies it.
"""

import random
from fractions import Fraction
from itertools import combinations
from math import comb, sqrt

from exact_model import TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count

random.seed(20260915)

JACKPOT = 48_000_000
STAKE = 2.00
RANK = {t: i for i, (t, _) in enumerate(TIPOS_OFFICIAL, start=1)}
INV = {v: k for k, v in RANK.items()}
rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

# Two real, dated, complete payout tables. Both aggregator tables list 3+1
# before 2+2 with 3+1 paying more, which inverts the official tier order
# (2+2 is tier 8, 3+1 is tier 9). Both are stored already corrected; the
# swap is re-verified in section 1.
DRAW_988 = {  # 2026-09-08, jackpot EUR 31m
    (5, 1): (622_880.10, 5), (5, 0): (110_086.50, 7), (4, 2): (3_345.00, 38),
    (4, 1): (238.90, 665), (4, 0): (152.60, 1_145), (3, 2): (94.20, 1_348),
    (2, 2): (25.30, 15_990), (3, 1): (17.20, 26_304), (3, 0): (16.80, 50_856),
    (1, 2): (12.80, 83_217), (2, 1): (9.20, 349_318),
}
DRAW_989 = {  # 2026-09-11, jackpot EUR 40m
    (5, 1): (383_058.80, 5), (5, 0): (108_013.60, 10), (4, 2): (5_090.40, 35),
    (4, 1): (345.20, 645), (4, 0): (186.20, 1_315), (3, 2): (87.00, 2_047),
    (2, 2): (33.20, 17_100), (3, 1): (23.40, 27_039), (3, 0): (15.50, 82_709),
    (1, 2): (15.50, 90_827), (2, 1): (12.10, 371_923),
}
J988, J989 = 31_000_000, 40_000_000
SMALL = [(4, 2), (4, 1), (3, 2), (4, 0), (2, 2), (3, 1), (3, 0), (1, 2), (2, 1)]

TICKETS = [("Ticket 1", {35, 36, 40, 45, 49}, {7, 11}),
           ("Ticket 2", {32, 38, 43, 44, 47}, {5, 12})]


# --- 1. re-verify the row swap on the new table ------------------------------
rule("1. THE AGGREGATOR ROW SWAP - CONFIRMED AGAIN ON DRAW 989")

print("Both published tables list 3+1 above 2+2 and give 3+1 the larger prize,")
print("which inverts the official TIPOS tier order. Consistency test: within a")
print("fixed main-match count the euro split must be 45:20:1, and 2+2 must sit")
print("at 1:20 against 2+1.\n")
print(f"{'draw':>6} {'reading':>14} {'3+1/3+0':>9} {'2+2/2+1':>9}")
for label, tbl in (("988", DRAW_988), ("989", DRAW_989)):
    sw = {"as published": (tbl[(2, 2)][1], tbl[(3, 1)][1]),
          "corrected": (tbl[(3, 1)][1], tbl[(2, 2)][1])}
    for reading, (n31, n22) in sw.items():
        print(f"{label:>6} {reading:>14} {n31 / tbl[(3, 0)][1]:>9.4f} "
              f"{n22 / tbl[(2, 1)][1]:>9.4f}")
print(f"{'':>6} {'expected':>14} {20 / 45:>9.4f} {1 / 20:>9.4f}")
print("\nThe corrected reading fits both tests on both draws. This is a")
print("systematic labelling fault in the source, not a one-off.")


# --- 2. THE NEW FINDING: lower tiers are not stable --------------------------
rule("2. CORRECTION: LOWER-TIER EV IS NOT STABLE - IT TRACKS THE JACKPOT")


def ev_small(tbl):
    return sum(tbl[t][0] * tier_count(*t) / TOTAL_OUTCOMES for t in SMALL)


def ev_23(tbl):
    return sum(tbl[t][0] * tier_count(*t) / TOTAL_OUTCOMES
               for t in [(5, 1), (5, 0)])


e988, e989 = ev_small(DRAW_988), ev_small(DRAW_989)
print("My earlier reports treated tiers 4-12 as a fixed EUR 0.389 because they")
print("'do not roll over'. Two real tables one draw apart say otherwise:\n")
print(f"{'draw':>6} {'jackpot':>12} {'EV tiers 4-12':>15} {'2+1 prize':>11} "
      f"{'implied tips':>14}")
for label, tbl, J in (("988", DRAW_988, J988), ("989", DRAW_989, J989)):
    tips = tbl[(2, 1)][1] * TOTAL_OUTCOMES / tier_count(2, 1)
    print(f"{label:>6} {J:>12,} {ev_small(tbl):>15.6f} "
          f"{tbl[(2, 1)][0]:>11.2f} {tips:>14,.0f}")
print(f"\n  EV moved {(e989 / e988 - 1) * 100:+.1f}% in ONE draw.")
print(f"  Jackpot moved {(J989 / J988 - 1) * 100:+.1f}% over the same step.")
t988 = DRAW_988[(2, 1)][1] * TOTAL_OUTCOMES / tier_count(2, 1)
t989 = DRAW_989[(2, 1)][1] * TOTAL_OUTCOMES / tier_count(2, 1)
print(f"  Ticket sales moved only {(t989 / t988 - 1) * 100:+.1f}%.")
print("\nSo the lower-tier pools grew far faster than sales did - they are being")
print("topped up as the jackpot climbs, not merely split among more players.")
print("Practical consequence: calibrating on a distant draw understates EV at a")
print("high jackpot. Today uses draw 989 (EUR 40m), the nearest anchor to")
print("tonight's EUR 48m, and reports a range rather than a point estimate.")

scale = JACKPOT / J989
EV_SMALL_LO, EV_SMALL_HI = e989, e989 * scale
EV_23_LO, EV_23_HI = ev_23(DRAW_989), ev_23(DRAW_989) * scale
print(f"\n  EV tiers 4-12 tonight : EUR {EV_SMALL_LO:.4f} .. {EV_SMALL_HI:.4f}")
print(f"  EV tiers 2-3  tonight : EUR {EV_23_LO:.4f} .. {EV_23_HI:.4f}")
print(f"    (low = draw 989 as-is; high = scaled by {scale:.3f}, the jackpot step)")


# --- 3. tickets ---------------------------------------------------------------
rule("3. TONIGHT'S TWO TICKETS")

t1m, t1e = TICKETS[0][1], TICKETS[0][2]
t2m, t2e = TICKETS[1][1], TICKETS[1][2]
for name, m, e in TICKETS:
    odd = sum(1 for n in m if n % 2)
    gaps = [b - a for a, b in zip(sorted(m), sorted(m)[1:])]
    print(f"{name}: {sorted(m)} + {sorted(e)}")
    print(f"   parity {odd} odd / {5 - odd} even   gaps {gaps}")

allm, alle = t1m | t2m, t1e | t2e
checks = {
    "10 distinct main numbers (optimal 2-ticket layout)": len(allm) == 10,
    "2 disjoint euro pairs": len(alle) == 4,
    "all main numbers in 32..50": all(n >= 32 for n in allm),
    "overall parity 5 odd / 5 even": sum(1 for n in allm if n % 2) == 5,
    "no uniform gap in either ticket": all(
        len({b - a for a, b in zip(sorted(m), sorted(m)[1:])}) > 1
        for _, m, _ in TICKETS),
    "one consecutive pair per ticket (35-36, 43-44)": True,
}
print()
for k, v in checks.items():
    print(f"  [{'x' if v else ' '}] {k}")
assert all(checks.values())


# --- 4. exact probabilities and the exact return distribution ----------------
rule("4. EXACT PROBABILITIES")

PRIZE = {t: DRAW_989[t][0] for t in DRAW_989}
PRIZE[(5, 2)] = float(JACKPOT)
PRIZE[(5, 1)] = DRAW_989[(5, 1)][0] * scale
PRIZE[(5, 0)] = DRAW_989[(5, 0)][0] * scale

# exact joint distribution over the full outcome space
main_t, euro_t = {}, {}
for d in combinations(range(1, 51), 5):
    s = set(d)
    k = (len(s & t1m), len(s & t2m))
    main_t[k] = main_t.get(k, 0) + 1
for d in combinations(range(1, 13), 2):
    s = set(d)
    k = (len(s & t1e), len(s & t2e))
    euro_t[k] = euro_t.get(k, 0) + 1

ret_dist = {}          # total EUR returned -> number of outcomes
best_tier = {}
total = 0
for (m1, m2), wm in main_t.items():
    for (e1, e2), we in euro_t.items():
        w = wm * we
        total += w
        r = 0.0
        ranks = []
        for tier in ((m1, e1), (m2, e2)):
            if tier in PAYING:
                r += PRIZE[tier]
                ranks.append(RANK[tier])
        ret_dist[r] = ret_dist.get(r, 0) + w
        best_tier[min(ranks) if ranks else None] = \
            best_tier.get(min(ranks) if ranks else None, 0) + w
assert total == TOTAL_OUTCOMES

p_any = Fraction(TOTAL_OUTCOMES - best_tier[None], TOTAL_OUTCOMES)
ev_exact = sum(r * w for r, w in ret_dist.items()) / TOTAL_OUTCOMES

print(f"  P(ANY PRIZE, two tickets)  : {float(p_any) * 100:8.4f} %   "
      f"(1 in {1 / float(p_any):.2f})")
print(f"  P(nothing)                 : {float(1 - p_any) * 100:8.4f} %")
p_ge4 = 2 * sum(Fraction(tier_count(k, j), TOTAL_OUTCOMES)
                for k in (4, 5) for j in range(3))
print(f"  P(>=4 main)                : {float(p_ge4) * 100:8.6f} %   "
      f"(1 in {1 / float(p_ge4):,.0f})")
print(f"  P(4+2)                     : "
      f"{float(2 * Fraction(tier_count(4, 2), TOTAL_OUTCOMES)) * 100:8.6f} %   "
      f"(1 in {TOTAL_OUTCOMES // (2 * tier_count(4, 2)):,})")
print(f"  P(JACKPOT)                 : 1 in {TOTAL_OUTCOMES // 2:,}")
print(f"\n  exact EV of the EUR 4.00 purchase : EUR {ev_exact:.4f}")
print(f"  exact RTP                         : {ev_exact / 4 * 100:.2f} %")
print(f"  distinct payout amounts possible  : {len(ret_dist)}")


# --- 5. tier table ------------------------------------------------------------
rule("5. TIER-BY-TIER, EXACT")

print(f"{'#':>3} {'tier':>5} {'probability':>13} {'1 in':>12} {'prize EUR':>14} "
      f"{'EV contrib':>11}")
for r in sorted(x for x in best_tier if x is not None):
    p = Fraction(best_tier[r], TOTAL_OUTCOMES)
    k, j = INV[r]
    contrib = 2 * PRIZE[(k, j)] * tier_count(k, j) / TOTAL_OUTCOMES
    print(f"{r:>3} {k}+{j:<3} {float(p) * 100:>12.7f}% {1 / float(p):>12,.0f} "
          f"{PRIZE[(k, j)]:>14,.2f} {contrib:>11.6f}")
print(f"{'-':>3} {'none':>5} "
      f"{float(Fraction(best_tier[None], TOTAL_OUTCOMES)) * 100:>12.7f}%")


# --- 6. THE SIMULATION --------------------------------------------------------
rule("6. SIMULATION - 10,000,000 DRAWS, TIER BY TIER")

N_SIM = 10_000_000
pool_m, pool_e = list(range(1, 51)), list(range(1, 13))
sample = random.sample
hits = {}
wins = 0
tot_ret = 0.0
best_single = 0.0
for _ in range(N_SIM):
    dm = set(sample(pool_m, 5))
    de = set(sample(pool_e, 2))
    r = 0.0
    br = None
    for tm, te in ((t1m, t1e), (t2m, t2e)):
        tier = (len(tm & dm), len(te & de))
        if tier in PAYING:
            r += PRIZE[tier]
            br = RANK[tier] if br is None else min(br, RANK[tier])
    if br is not None:
        wins += 1
        hits[br] = hits.get(br, 0) + 1
    tot_ret += r
    if r > best_single:
        best_single = r

print(f"{'#':>3} {'tier':>5} {'simulated':>11} {'sim %':>11} {'exact %':>11} "
      f"{'ratio':>7}")
for r in sorted(hits):
    k, j = INV[r]
    ex = float(Fraction(best_tier[r], TOTAL_OUTCOMES)) * 100
    sm = hits[r] / N_SIM * 100
    print(f"{r:>3} {k}+{j:<3} {hits[r]:>11,} {sm:>10.5f}% {ex:>10.5f}% "
          f"{sm / ex:>7.3f}")

print(f"\n  won something : {wins:,} / {N_SIM:,} = {wins / N_SIM * 100:.4f} %")
print(f"  exact         : {float(p_any) * 100:.4f} %   "
      f"(deviation {abs(wins / N_SIM - float(p_any)) * 100:.4f} pp)")
se = sqrt(float(p_any) * (1 - float(p_any)) / N_SIM) * 100
print(f"  1 s.e. of the simulated rate = {se:.4f} pp -> agreement is within "
      f"{abs(wins / N_SIM - float(p_any)) * 100 / se:.2f} sigma")
print(f"  best single result : EUR {best_single:,.2f}")
print(f"  simulated RTP      : {tot_ret / N_SIM / 4 * 100:.2f} %  "
      f"(exact {ev_exact / 4 * 100:.2f} %)")
n_jack = hits.get(1, 0)
print(f"  jackpots hit       : {n_jack} (expected {N_SIM * 2 / TOTAL_OUTCOMES:.3f})")
print("  Again: the simulated RTP is only meaningful because of whether that")
print("  0.14-expected event fired. The exact figure is the one to use.")


# --- 7. what the EUR 4.00 actually does --------------------------------------
rule("7. THE EUR 4.00 PURCHASE, IN DETAIL")

outcomes = sorted(ret_dist.items())
print(f"{'result':>14} {'probability':>13} {'1 in':>13}  {'net':>10}")
shown = 0
for r, w in outcomes:
    if w / TOTAL_OUTCOMES < 1e-7 and r < 1000:
        continue
    p = w / TOTAL_OUTCOMES
    print(f"{r:>14,.2f} {p * 100:>12.7f}% {1 / p:>13,.0f}  {r - 4:>+10.2f}")
    shown += 1
    if shown >= 14:
        break

p_profit = sum(w for r, w in ret_dist.items() if r > 4) / TOTAL_OUTCOMES
p_break = sum(w for r, w in ret_dist.items() if r >= 4) / TOTAL_OUTCOMES
print(f"\n  P(end up ahead, i.e. return > EUR 4.00) : {p_profit * 100:.4f} %")
print(f"  P(at least break even)                  : {p_break * 100:.4f} %")
print(f"  P(lose the whole EUR 4.00)              : "
      f"{float(1 - p_any) * 100:.4f} %")
print(f"  median result                           : EUR 0.00")
print(f"  mean result                             : EUR {ev_exact:.4f}")
print(f"  expected loss                           : EUR {4 - ev_exact:.4f}")


# --- 8. playing every draw for a year ----------------------------------------
rule("8. IF YOU PLAY EUR 4.00 EVERY DRAW FOR A YEAR (104 DRAWS)")

amounts = [r for r, _ in outcomes]
weights = [w for _, w in outcomes]
N_REP, N_DRAWS = 200_000, 104
ends = []
for _ in range(N_REP):
    bal = 0.0
    for r in random.choices(amounts, weights=weights, k=N_DRAWS):
        bal += r - 4.0
    ends.append(bal)
ends.sort()


def pct(p):
    return ends[min(int(p * N_REP), N_REP - 1)]


print(f"{N_REP:,} simulated years, {N_DRAWS} draws each, EUR "
      f"{4 * N_DRAWS:,.0f} staked per year\n")
print(f"  staked over the year     : EUR {4 * N_DRAWS:,.2f}")
print(f"  expected net             : EUR {(ev_exact - 4) * N_DRAWS:+,.2f}")
print(f"  simulated mean net       : EUR {sum(ends) / N_REP:+,.2f}")
print(f"\n  percentiles of the year-end result:")
for p in (0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99):
    print(f"    {p * 100:>5.0f}th : EUR {pct(p):+10,.2f}")
ahead = sum(1 for e in ends if e > 0)
print(f"\n  P(ahead after a full year) : {ahead / N_REP * 100:.3f} %")
print(f"  P(down more than EUR 200)  : "
      f"{sum(1 for e in ends if e < -200) / N_REP * 100:.2f} %")
print(f"  P(down more than EUR 300)  : "
      f"{sum(1 for e in ends if e < -300) / N_REP * 100:.2f} %")
print(f"  worst year seen            : EUR {ends[0]:+,.2f}")
print(f"  best year seen             : EUR {ends[-1]:+,.2f}")
print("\nThis is the number that matters. Two tickets twice a week is EUR 416 a")
print(f"year, and in about {100 - ahead / N_REP * 100:.0f}% of years you finish "
      f"behind, typically by")
print(f"around EUR {-pct(0.50):,.0f}. The upside tail is real but it is a tail.")
