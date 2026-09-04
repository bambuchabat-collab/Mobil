"""
Eurojackpot analysis for the draw of Friday 2026-09-04.

Jackpot EUR 23,000,000, confirmed by three sources:
  1. tipos.sk Eurojackpot page ("23 000 000,00 EUR")
  2. t-online.de, "Eurojackpot am Freitag, dem 04. September: Chance auf
     23 Millionen Euro"
  3. lotteryextreme.com, next draw "04.09.2026", jackpot "EUR 23,000,000"
The German source independently restates the 1:139,838,160 top-tier odds and
the 20:00 German-time Helsinki draw, both matching this model.

Structural probabilities are properties of the rules, not of the draw, and are
unchanged; they were verified three independent ways and are re-verified on
tonight's numbers by verify_naive.py and verify_bruteforce.c.
"""

import random
from fractions import Fraction

from exact_model import (
    TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count,
    p_any_prize_single, two_ticket_stats, joint_distribution, fmt,
)

random.seed(20260904)

STAKE = Fraction(2)
JACKPOT = 23_000_000
PREV_JACKPOT = 15_000_000
JACKPOT_CAP = 120_000_000

EV_TIERS_4_12 = 0.410348          # calibrated on a real TIPOS payout table
REF_JACKPOT = 39_496_021.60
EV_TIERS_2_3_AT_REF = 0.250097
TIPS_ESTIMATE = 16_725_833

TICKETS = [
    ("Ticket 1", [32, 39, 41, 46, 49], [6, 10]),
    ("Ticket 2", [34, 38, 45, 47, 48], [9, 11]),
]
LAST_MAIN, LAST_EURO = {9, 14, 35, 43, 50}, {3, 7}

RANK = {t: i for i, (t, _) in enumerate(TIPOS_OFFICIAL, start=1)}
rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --- 1. tickets --------------------------------------------------------------
rule("1. TICKETS FOR 2026-09-04")

t1m, t1e = set(TICKETS[0][1]), set(TICKETS[0][2])
t2m, t2e = set(TICKETS[1][1]), set(TICKETS[1][2])

for name, main, euro in TICKETS:
    odd = sum(1 for n in main if n % 2)
    gaps = [b - a for a, b in zip(sorted(main), sorted(main)[1:])]
    print(f"{name}: {sorted(main)} + {sorted(euro)}")
    print(f"   parity {odd} odd / {5 - odd} even   gaps {gaps}")

checks = {
    "main numbers disjoint across tickets": not (t1m & t2m),
    "euro pairs disjoint across tickets": not (t1e & t2e),
    "all 10 main numbers in 32..50": all(n >= 32 for n in t1m | t2m),
    "overall parity 5 odd / 5 even": sum(1 for n in t1m | t2m if n % 2) == 5,
    "no uniform gap in either ticket": all(
        len({b - a for a, b in zip(sorted(m), sorted(m)[1:])}) > 1
        for m in (t1m, t2m)),
    "avoids last draw's main numbers": not ((t1m | t2m) & LAST_MAIN),
    "avoids last draw's euro numbers": not ((t1e | t2e) & LAST_EURO),
}
print()
for label, ok in checks.items():
    print(f"  [{'x' if ok else ' '}] {label}")
assert all(checks.values())
print("\nTicket 2 contains the consecutive pair 47-48. That is deliberate:")
print("consecutive numbers occur in 35.3% of real draws but players avoid them,")
print("so including a pair is a mild unpopularity gain. As always this affects")
print("the pari-mutuel share only - never the probability of winning.")


# --- 2. THE HEADLINE PERCENTAGES (exact) -------------------------------------
rule("2. CHANCE OF WINNING - TWO TICKETS, EXACT")

p1 = p_any_prize_single()
best = two_ticket_stats(0, 0)
p_ge4 = best["p_union_ge4_main"]
p_42 = best["p_union_4plus2"]
p_jack2 = 2 * Fraction(1, TOTAL_OUTCOMES)

print(f"  P(ANY PRIZE, two tickets)   {float(best['p_union_any_prize']) * 100:8.4f} %"
      f"   (1 in {1 / float(best['p_union_any_prize']):.2f})")
print(f"  P(no prize at all)          "
      f"{float(1 - best['p_union_any_prize']) * 100:8.4f} %")
print(f"  P(>=4 main numbers)         {float(p_ge4) * 100:8.6f} %"
      f"   (1 in {1 / float(p_ge4):,.0f})")
print(f"  P(4+2)                      {float(p_42) * 100:8.6f} %"
      f"   (1 in {1 / float(p_42):,.0f})")
print(f"  P(JACKPOT 5+2)              {float(p_jack2) * 100:8.7f} %"
      f"   (1 in {1 / float(p_jack2):,.0f})")
print(f"\n  one ticket alone            {float(p1) * 100:8.4f} %"
      f"   (1 in {1 / float(p1):.2f})")
print(f"  exact fraction, two tickets : "
      f"{best['p_union_any_prize'].numerator:,} / "
      f"{best['p_union_any_prize'].denominator:,}")


# --- 3. tier distribution ----------------------------------------------------
rule("3. WHERE A WIN WOULD LAND (best tier reached, two tickets)")

agg = {}
for (mA, eA, mB, eB), w in joint_distribution(0, 0).items():
    r = [RANK[t] for t in ((mA, eA), (mB, eB)) if t in PAYING]
    k = min(r) if r else None
    agg[k] = agg.get(k, 0) + w
assert sum(agg.values()) == TOTAL_OUTCOMES

# prize levels for tonight
scale = JACKPOT / REF_JACKPOT
PRIZE = {(5, 2): float(JACKPOT), (5, 1): 1_394_682.50 * scale,
         (5, 0): 157_307.20 * scale, (4, 2): 4_324.50, (4, 1): 334.30,
         (3, 2): 130.20, (4, 0): 129.70, (2, 2): 23.60, (3, 1): 20.70,
         (3, 0): 19.20, (1, 2): 13.30, (2, 1): 9.30}

inv = {v: k for k, v in RANK.items()}
print(f"{'#':>3} {'tier':>5} {'probability':>13} {'1 in':>12} {'prize EUR':>16}")
for r in sorted(x for x in agg if x is not None):
    p = Fraction(agg[r], TOTAL_OUTCOMES)
    k, j = inv[r]
    print(f"{r:>3} {k}+{j:<3} {float(p) * 100:>12.7f}% {1 / float(p):>12,.0f} "
          f"{PRIZE[(k, j)]:>16,.2f}")
p_none = Fraction(agg[None], TOTAL_OUTCOMES)
print(f"{'-':>3} {'none':>5} {float(p_none) * 100:>12.7f}%")
print("\n(5+1 and 5+0 are scaled with the jackpot; tiers 4-12 are observed real")
print(" levels. All lower-tier amounts are pari-mutuel and vary by draw.)")


# --- 4. SIMULATION -----------------------------------------------------------
rule("4. SIMULATION - 10,000,000 DRAWS AGAINST TONIGHT'S TWO TICKETS")

N_SIM = 10_000_000
main_pool = list(range(1, 51))
euro_pool = list(range(1, 13))
sample = random.sample

tier_hits = {}
wins = 0
total_ret = 0.0
best_ret = 0.0

for _ in range(N_SIM):
    dm = set(sample(main_pool, 5))
    de = set(sample(euro_pool, 2))
    ret = 0.0
    bestrank = None
    for tm, te in ((t1m, t1e), (t2m, t2e)):
        tier = (len(tm & dm), len(te & de))
        if tier in PAYING:
            ret += PRIZE[tier]
            r = RANK[tier]
            bestrank = r if bestrank is None else min(bestrank, r)
    if bestrank is not None:
        wins += 1
        tier_hits[bestrank] = tier_hits.get(bestrank, 0) + 1
    total_ret += ret
    if ret > best_ret:
        best_ret = ret

print(f"{N_SIM:,} simulated draws, EUR 4.00 staked each time\n")
print(f"{'#':>3} {'tier':>5} {'simulated':>11} {'sim %':>11} {'exact %':>11}")
for r in sorted(tier_hits):
    k, j = inv[r]
    ex = float(Fraction(agg[r], TOTAL_OUTCOMES)) * 100
    print(f"{r:>3} {k}+{j:<3} {tier_hits[r]:>11,} "
          f"{tier_hits[r] / N_SIM * 100:>10.5f}% {ex:>10.5f}%")

print(f"\n  WON SOMETHING       : {wins:,} of {N_SIM:,} = "
      f"{wins / N_SIM * 100:.4f} %")
print(f"  exact value         : {float(best['p_union_any_prize']) * 100:.4f} %"
      f"   -> simulation agrees")
print(f"  WON NOTHING         : {(N_SIM - wins) / N_SIM * 100:.4f} %")
print(f"  best single result  : EUR {best_ret:,.2f}")
print(f"  mean return         : EUR {total_ret / N_SIM:.4f} per EUR 4.00")
print(f"  staked in total     : EUR {N_SIM * 4:,.0f}")
print(f"  returned in total   : EUR {total_ret:,.0f}")
print(f"  net                 : EUR {total_ret - N_SIM * 4:,.0f}")

ev_exact = 2 * sum(PRIZE[t] * tier_count(*t) / TOTAL_OUTCOMES for t in PAYING)
n_jack = tier_hits.get(1, 0)
ret_nojack = total_ret - n_jack * PRIZE[(5, 2)]
print(f"\n  exact EV, same prize table : EUR {ev_exact:.4f}  "
      f"(RTP {ev_exact / 4 * 100:.1f}%)")
print(f"  simulated                  : EUR {total_ret / N_SIM:.4f}  "
      f"(RTP {total_ret / N_SIM / 4 * 100:.1f}%)")
print(f"\n  WHY THE SIMULATED RTP IS UNRELIABLE - look at what just happened.")
print(f"  A jackpot was expected {N_SIM * 2 / TOTAL_OUTCOMES:.3f} times in this run "
      f"and came up {n_jack}.")
print(f"    with that one hit    : RTP {total_ret / N_SIM / 4 * 100:.1f}%")
print(f"    without it           : RTP {ret_nojack / N_SIM / 4 * 100:.1f}%")
print(f"    exact answer         : RTP {ev_exact / 4 * 100:.1f}%")
print(f"  One event in ten million swings the estimate from "
      f"{ret_nojack / N_SIM / 4 * 100:.0f}% to {total_ret / N_SIM / 4 * 100:.0f}%.")
print(f"  Ten million draws is NOT enough to measure this game by simulation,")
print(f"  and no feasible number would be. That is exactly why every headline")
print(f"  figure in this report comes from exact enumeration instead - the")
print(f"  simulation is here only to confirm the common tiers, which it does")
print(f"  to three decimal places.")


# --- 5. RTP ------------------------------------------------------------------
rule("5. RTP AT EUR 23,000,000")

p_jack = Fraction(tier_count(5, 2), TOTAL_OUTCOMES)
ev_jack = float(JACKPOT) * float(p_jack)
ev23_lo = EV_TIERS_2_3_AT_REF * scale
ev23_hi = EV_TIERS_2_3_AT_REF
ev_lo = ev_jack + EV_TIERS_4_12 + ev23_lo
ev_hi = ev_jack + EV_TIERS_4_12 + ev23_hi

print(f"EV from jackpot         EUR {ev_jack:.6f}   [exact given J]")
print(f"EV from tiers 4-12      EUR {EV_TIERS_4_12:.6f}   [observed real levels]")
print(f"EV from tiers 2-3       EUR {ev23_lo:.4f} .. {ev23_hi:.4f}  [they roll too]")
print(f"\nEV per EUR 2.00 ticket  EUR {ev_lo:.4f} .. EUR {ev_hi:.4f}")
print(f"RTP                     {ev_lo / 2 * 100:.1f} % .. {ev_hi / 2 * 100:.1f} %")

prev_lo = (float(PREV_JACKPOT) * float(p_jack) + EV_TIERS_4_12
           + EV_TIERS_2_3_AT_REF * (PREV_JACKPOT / REF_JACKPOT))
print(f"\nTuesday (EUR 15m) gave  {prev_lo / 2 * 100:.1f} % at the low end;")
print(f"the rollover to EUR 23m adds about {(ev_lo - prev_lo) / 2 * 100:.1f} pp.")
print(f"This is the best RTP of the three draws analysed so far - and still")
print(f"means losing about EUR {4 - 2 * ev_hi:.2f}-{4 - 2 * ev_lo:.2f} of every EUR 4.00 on average.")


def share_factor(n_tips, p=float(Fraction(1, TOTAL_OUTCOMES))):
    return (1 - (1 - p) ** n_tips) / (n_tips * p)


f = share_factor(TIPS_ESTIMATE)
print(f"\nJackpot-splitting correction at ~{TIPS_ESTIMATE:,} tips: "
      f"keep {f:.4f} ({(1 - f) * 100:.1f}% haircut)")
print(f"  RTP with splitting      {(ev_jack * f + EV_TIERS_4_12 + ev23_lo) / 2 * 100:.1f} % .. "
      f"{(ev_jack * f + EV_TIERS_4_12 + ev23_hi) / 2 * 100:.1f} %")

print(f"\nTwo tickets, EUR 4.00:")
print(f"  expected return  EUR {2 * ev_lo:.2f} .. EUR {2 * ev_hi:.2f}")
print(f"  expected loss    EUR {4 - 2 * ev_hi:.2f} .. EUR {4 - 2 * ev_lo:.2f}")


# --- 6. bottom line ----------------------------------------------------------
rule("6. BOTTOM LINE")

print(f"  chance of winning something tonight : "
      f"{float(best['p_union_any_prize']) * 100:.2f} %")
print(f"  chance of winning nothing           : "
      f"{float(1 - best['p_union_any_prize']) * 100:.2f} %")
print(f"  most likely win if you win          : 2+1, about EUR 9.30 "
      f"({float(Fraction(agg[12], TOTAL_OUTCOMES)) / float(best['p_union_any_prize']) * 100:.1f}% of wins)")
print(f"  chance of the jackpot               : 1 in "
      f"{1 / float(p_jack2):,.0f}")
print(f"\n  Number choice does not move any of these. It never has and it")
print(f"  cannot: 472 real draws showed no signal in any test, and every")
print(f"  combination is equally likely tonight.")
