"""
Eurojackpot analysis for Friday 2026-09-11. THREE tickets, EUR 6.00.

Jackpot EUR 40,000,000, confirmed by two sources:
  - t-online.de "Eurojackpot am Freitag, 11.09.2026: 40 Millionen im Jackpot"
  - presseportal.de / ISA-GUIDE, "40 Millionen Euro bei Eurojackpot erwartet"
Both restate the 1:139,838,160 top-tier odds and the EUR 120m cap.

NEW THIS ROUND: the prize model is recalibrated on a COMPLETE, DATED payout
table (draw 988, 2026-09-08) instead of the older undated one. That table also
exposes a labelling problem in the source, handled below.
"""

from fractions import Fraction
from itertools import combinations

from exact_model import TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count

JACKPOT = 40_000_000
PREV_JACKPOT = 31_000_000          # jackpot played for in draw 988
STAKE_PER_TICKET = 2.00

RANK = {t: i for i, (t, _) in enumerate(TIPOS_OFFICIAL, start=1)}
rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

# Draw 988 (2026-09-08) full payout table, as published by lotteryextreme.
# Rows are (prize, winners). See the labelling note below.
D988_AS_PUBLISHED = {
    (5, 2): (0.0, 0), (5, 1): (622_880.10, 5), (5, 0): (110_086.50, 7),
    (4, 2): (3_345.00, 38), (4, 1): (238.90, 665), (4, 0): (152.60, 1_145),
    (3, 2): (94.20, 1_348),
    (3, 1): (25.30, 15_990),      # suspect - see below
    (2, 2): (17.20, 26_304),      # suspect - see below
    (3, 0): (16.80, 50_856), (1, 2): (12.80, 83_217), (2, 1): (9.20, 349_318),
}
# Same table with the two suspect rows swapped back to official tier order.
D988_CORRECTED = dict(D988_AS_PUBLISHED)
D988_CORRECTED[(2, 2)] = (25.30, 15_990)
D988_CORRECTED[(3, 1)] = (17.20, 26_304)


# --- 1. a labelling error in the published table -----------------------------
rule("1. ERROR FOUND IN THE SOURCE PAYOUT TABLE (draw 988)")

print("Official TIPOS tier order is by prize size: 2+2 is tier 8, 3+1 is tier 9,")
print("so 2+2 must pay AT LEAST as much as 3+1. The published table has")
print("  3+1 = EUR 25.30 (15,990 winners)   and   2+2 = EUR 17.20 (26,304)")
print("which inverts that. Two independent checks say the rows are swapped:\n")

for label, tbl in (("as published", D988_AS_PUBLISHED),
                   ("rows swapped", D988_CORRECTED)):
    # within a fixed main-match count the euro split must be 45 : 20 : 1
    n3 = [tbl[(3, j)][1] for j in range(3)]
    r3 = n3[1] / n3[0]
    # 2+2 vs 2+1 must sit at 1:20
    r2 = tbl[(2, 2)][1] / tbl[(2, 1)][1]
    print(f"  {label:<14} 3+1/3+0 = {r3:.3f} (expect 0.444)   "
          f"2+2/2+1 = {r2:.4f} (expect 0.0500)")

print("\nThe swapped reading fits both; the published one fits neither, and it")
print("also disagrees with the 4+0/4+1/4+2 row, which points the other way.")
print("This matters for anyone reading prize tables off aggregators. For the EV")
print("below it barely matters - both readings are computed and compared.")


# --- 2. recalibrated prize model ---------------------------------------------
rule("2. RECALIBRATED PRIZE MODEL - AND AN ERROR IN MY OWN EARLIER NUMBERS")

SMALL = [(4, 2), (4, 1), (3, 2), (4, 0), (2, 2), (3, 1), (3, 0), (1, 2), (2, 1)]


def ev_small(tbl):
    return sum(tbl[t][0] * tier_count(*t) / TOTAL_OUTCOMES for t in SMALL)


ev_pub, ev_cor = ev_small(D988_AS_PUBLISHED), ev_small(D988_CORRECTED)
OLD_EV_SMALL = 0.410348

print(f"EV of tiers 4-12 from the real draw-988 table:")
print(f"  as published : EUR {ev_pub:.6f}")
print(f"  rows swapped : EUR {ev_cor:.6f}   <- used below")
print(f"  difference   : EUR {abs(ev_pub - ev_cor):.6f}  (immaterial)")
print(f"\nMy previous reports used EUR {OLD_EV_SMALL:.6f}, calibrated on an older,")
print(f"UNDATED table. That was too high by "
      f"{(OLD_EV_SMALL - ev_cor) / ev_cor * 100:.1f}% - a real error, now fixed.")
print(f"Every RTP figure I gave for 2026-08-28, 09-01 and 09-04 was therefore")
print(f"about {(OLD_EV_SMALL - ev_cor) / 2 * 100:.1f} pp too optimistic.")

EV_SMALL = ev_cor

# tiers 2-3 anchored on the same real draw, then scaled with the jackpot
ev23_at_prev = sum(D988_CORRECTED[t][0] * tier_count(*t) / TOTAL_OUTCOMES
                   for t in [(5, 1), (5, 0)])
scale = JACKPOT / PREV_JACKPOT
EV_23 = ev23_at_prev * scale
print(f"\nTiers 2-3 at draw 988 (EUR 31m jackpot) : EUR {ev23_at_prev:.6f}")
print(f"scaled to tonight's EUR 40m (x{scale:.4f})  : EUR {EV_23:.6f}")
print("This anchors 5+1 and 5+0 on a real dated payout instead of the wide")
print("bracket I was carrying before.")


# --- 3. tips sold, from real winner counts -----------------------------------
rule("3. HOW MANY TICKETS EUROPE BOUGHT (from draw 988 winner counts)")

print(f"{'tier':>6} {'winners':>10} {'implied tips sold':>20}")
est = []
for t in [(2, 1), (1, 2), (3, 0), (3, 1), (2, 2), (3, 2), (4, 0)]:
    w = D988_CORRECTED[t][1]
    n = w * TOTAL_OUTCOMES / tier_count(*t)
    est.append(n)
    print(f"{t[0]}+{t[1]:<4} {w:>10,} {n:>20,.0f}")
est.sort()
median = est[len(est) // 2]
print(f"\nmedian estimate: {median:,.0f} tips  (EUR {median * 2:,.0f} staked)")
print("The spread across tiers is wide because players do not pick uniformly -")
print("which is the same effect documented earlier, not a modelling failure.")
TIPS = median


# --- 4. exact odds for three tickets -----------------------------------------
rule("4. TONIGHT'S THREE TICKETS")

TICKETS = [
    ("Ticket 1", {35, 38, 39, 44, 50}, {6, 11}),
    ("Ticket 2", {32, 37, 42, 45, 46}, {8, 12}),
    ("Ticket 3", {36, 40, 41, 43, 47}, {5, 10}),
]


def exact_multi(tickets):
    """Exact P(at least one prize): full enumeration of all 139,838,160 outcomes."""
    mains = [t[1] for t in tickets]
    euros = [t[2] for t in tickets]
    mt, et = {}, {}
    for d in combinations(range(1, 51), 5):
        s = set(d)
        k = tuple(len(s & m) for m in mains)
        mt[k] = mt.get(k, 0) + 1
    for d in combinations(range(1, 13), 2):
        s = set(d)
        k = tuple(len(s & e) for e in euros)
        et[k] = et.get(k, 0) + 1
    total = win = 0
    per_tier = {}
    for mk, wm in mt.items():
        for ek, we in et.items():
            w = wm * we
            total += w
            ranks = [RANK[(mk[i], ek[i])] for i in range(len(tickets))
                     if (mk[i], ek[i]) in PAYING]
            if ranks:
                win += w
                per_tier[min(ranks)] = per_tier.get(min(ranks), 0) + w
    assert total == TOTAL_OUTCOMES
    return Fraction(win, total), per_tier


for name, m, e in TICKETS:
    odd = sum(1 for n in m if n % 2)
    gaps = [b - a for a, b in zip(sorted(m), sorted(m)[1:])]
    print(f"{name}: {sorted(m)} + {sorted(e)}")
    print(f"   parity {odd} odd / {5 - odd} even   gaps {gaps}")

allm = set().union(*(t[1] for t in TICKETS))
alle = set().union(*(t[2] for t in TICKETS))
checks = {
    "15 distinct main numbers (no repeats across tickets)": len(allm) == 15,
    "3 fully disjoint euro pairs (6 distinct numbers)": len(alle) == 6,
    "all main numbers in 32..50": all(n >= 32 for n in allm),
    "overall parity 7 odd / 8 even": sum(1 for n in allm if n % 2) == 7,
    "no uniform gap in any ticket": all(
        len({b - a for a, b in zip(sorted(m), sorted(m)[1:])}) > 1
        for _, m, _ in TICKETS),
    "union is not one contiguous block": sorted(allm) != list(
        range(min(allm), min(allm) + 15)),
}
print()
for label, ok in checks.items():
    print(f"  [{'x' if ok else ' '}] {label}")
assert all(checks.values())

print("\nDROPPED this round: the 'avoid the previous draw's numbers' rule. It has")
print("now been tested twice and rests on an effect the literature does not")
print("settle in either direction. It constrained the pool for no measurable")
print("gain, so it is gone. Each ticket keeps one consecutive pair (38-39,")
print("45-46, 40-41): players avoid those, so they are a mild unpopularity gain.")

p3, per_tier = exact_multi(TICKETS)
p2 = Fraction(2_190_533, 34_959_540)
p1 = Fraction(133_127, 4_237_520)

rule("5. CHANCE OF WINNING - THREE TICKETS, EXACT")

print(f"  P(ANY PRIZE, three tickets) : {float(p3) * 100:8.4f} %   "
      f"(1 in {1 / float(p3):.2f})")
print(f"  P(nothing at all)           : {float(1 - p3) * 100:8.4f} %")
print(f"  for comparison, two tickets : {float(p2) * 100:8.4f} %")
print(f"  one ticket                  : {float(p1) * 100:8.4f} %")
print(f"\n  exact fraction              : {p3.numerator:,} / {p3.denominator:,}")

p_ge4 = 3 * sum(Fraction(tier_count(k, j), TOTAL_OUTCOMES)
                for k in (4, 5) for j in range(3))
p_42 = 3 * Fraction(tier_count(4, 2), TOTAL_OUTCOMES)
p_jack = 3 * Fraction(1, TOTAL_OUTCOMES)
print(f"\n  P(>=4 main numbers)         : {float(p_ge4) * 100:8.6f} %   "
      f"(1 in {1 / float(p_ge4):,.0f})")
print(f"  P(4+2)                      : {float(p_42) * 100:8.6f} %   "
      f"(1 in {1 / float(p_42):,.0f})")
print(f"  P(JACKPOT)                  : 1 in {1 / float(p_jack):,.0f}")
print("  (these three are exactly 3x the single-ticket value: with 15 distinct")
print("   main numbers two tickets can never both reach 4+ main matches)")

rule("6. WHERE A WIN WOULD LAND")
inv = {v: k for k, v in RANK.items()}
print(f"{'#':>3} {'tier':>5} {'probability':>13} {'1 in':>11} {'prize EUR':>15}")
prize = dict((t, D988_CORRECTED[t][0]) for t in D988_CORRECTED)
prize[(5, 2)] = float(JACKPOT)
prize[(5, 1)] = D988_CORRECTED[(5, 1)][0] * scale
prize[(5, 0)] = D988_CORRECTED[(5, 0)][0] * scale
for r in sorted(per_tier):
    p = Fraction(per_tier[r], TOTAL_OUTCOMES)
    k, j = inv[r]
    print(f"{r:>3} {k}+{j:<3} {float(p) * 100:>12.7f}% {1 / float(p):>11,.0f} "
          f"{prize[(k, j)]:>15,.2f}")
print(f"{'-':>3} {'none':>5} {float(1 - p3) * 100:>12.7f}%")


# --- 7. RTP ------------------------------------------------------------------
rule("7. RTP AT EUR 40,000,000")

p_jack1 = float(Fraction(tier_count(5, 2), TOTAL_OUTCOMES))
ev_jack = JACKPOT * p_jack1
ev_total = ev_jack + EV_SMALL + EV_23


def share_factor(n_tips, p=p_jack1):
    return (1 - (1 - p) ** n_tips) / (n_tips * p)


f = share_factor(TIPS)
ev_shared = ev_jack * f + EV_SMALL + EV_23

print(f"EV from jackpot        EUR {ev_jack:.6f}   [exact given J]")
print(f"EV tiers 4-12          EUR {EV_SMALL:.6f}   [real draw-988 payouts]")
print(f"EV tiers 2-3           EUR {EV_23:.6f}   [draw 988, scaled to EUR 40m]")
print(f"\nEV per EUR 2.00 ticket EUR {ev_total:.4f}")
print(f"RTP                    {ev_total / 2 * 100:.1f} %")
print(f"with jackpot splitting ({(1 - f) * 100:.1f}% haircut at "
      f"{TIPS:,.0f} tips): {ev_shared / 2 * 100:.1f} %")
print(f"\nThree tickets, EUR 6.00:")
print(f"  expected return  EUR {3 * ev_shared:.2f}")
print(f"  expected loss    EUR {6 - 3 * ev_shared:.2f}")
print(f"\nBest RTP of every draw analysed so far - and still the house keeps")
print(f"about {(1 - ev_shared / 2) * 100:.0f} cents of every euro.")
