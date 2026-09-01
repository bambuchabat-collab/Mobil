"""
Eurojackpot analysis for the draw of Tuesday 2026-09-01.

The structural results (per-tier probabilities, two-ticket configuration
optimum, P(any prize), P(>=4 main), P(4+2)) are properties of the GAME, not of
the draw, so they are unchanged from the 2026-08-28 report and were already
verified three independent ways. This script restates them, then recomputes
what actually changed - the jackpot and therefore the RTP - and adds a proper
jackpot-splitting correction.

Jackpot for this draw: EUR 15,000,000, confirmed by two sources
  1. tipos.sk, Eurojackpot page ("15 000 000,00 EUR")
  2. t-online.de, "Eurojackpot am Dienstag, den 1. September: 15 Millionen Euro
     im Topf" - and it states the jackpot rolled because 2026-08-28 was unwon,
     which matches our own settlement of that draw.
"""

from fractions import Fraction

from exact_model import (
    TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count,
    p_any_prize_single, two_ticket_stats, fmt,
)

STAKE = Fraction(2)
JACKPOT = 15_000_000
PREV_JACKPOT = 10_000_000
JACKPOT_CAP = 120_000_000

# Empirically calibrated in empirical_check.py from a real TIPOS payout table.
EV_TIERS_4_12 = 0.410348          # EUR per EUR 2.00 ticket, tiers 4..12
REF_JACKPOT = 39_496_021.60       # jackpot of the draw those prizes came from
EV_TIERS_2_3_AT_REF = 0.250097    # EUR per ticket from 5+1 and 5+0 at that jackpot

# Europe-wide tips implied by the 2026-08-28 draw (525,463 winners / P(any))
TIPS_ESTIMATE = 16_725_833

TICKETS = [
    ("Ticket 1", [33, 37, 40, 44, 50], [6, 11]),
    ("Ticket 2", [35, 41, 43, 46, 48], [9, 12]),
]

LAST_DRAW_MAIN = {23, 34, 39, 45, 49}
LAST_DRAW_EURO = {1, 4}

rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --- 1. structural results (unchanged, game properties) ----------------------
rule("1. STRUCTURAL RESULTS - UNCHANGED FROM THE 2026-08-28 REPORT")

p1 = p_any_prize_single()
best = two_ticket_stats(0, 0)      # disjoint mains + disjoint euro pairs
p_ge4_one = sum(Fraction(tier_count(k, j), TOTAL_OUTCOMES)
                for k in (4, 5) for j in range(3))

print("These depend only on the rules, not on the jackpot or the date:\n")
print(f"  total outcomes            {TOTAL_OUTCOMES:,}")
print(f"  P(any prize), 1 ticket    {fmt(p1)}")
print(f"  P(any prize), 2 tickets   {fmt(best['p_union_any_prize'])}")
print(f"  P(>=4 main), 2 tickets    {fmt(best['p_union_ge4_main'])}")
print(f"  P(4+2), 2 tickets         {fmt(best['p_union_4plus2'])}")
print(f"  P(jackpot), 2 tickets     1 in {1 / float(2 * Fraction(1, TOTAL_OUTCOMES)):,.0f}")
print(f"  P(no prize at all)        {float(1 - best['p_union_any_prize']) * 100:.6f}%")
print("\n  Optimal two-ticket configuration is still disjoint main numbers +")
print("  disjoint euro pairs; it beats identical euro pairs by 0.281 pp and")
print("  3-shared main numbers by 0.374 pp. Nothing about the draw changes it.")


# --- 2. ticket construction --------------------------------------------------
rule("2. TICKETS FOR 2026-09-01")

t1_main, t1_euro = set(TICKETS[0][1]), set(TICKETS[0][2])
t2_main, t2_euro = set(TICKETS[1][1]), set(TICKETS[1][2])

for name, main, euro in TICKETS:
    odd = sum(1 for n in main if n % 2)
    diffs = [b - a for a, b in zip(sorted(main), sorted(main)[1:])]
    print(f"{name}: {sorted(main)} + {sorted(euro)}")
    print(f"   all >= 32: {all(n >= 32 for n in main)}   "
          f"parity {odd} odd / {5 - odd} even   gaps {diffs}")

checks = {
    "main numbers disjoint across tickets": not (t1_main & t2_main),
    "euro pairs disjoint across tickets": not (t1_euro & t2_euro),
    "all 10 main numbers in 32..50": all(n >= 32 for n in t1_main | t2_main),
    "overall parity 5 odd / 5 even":
        sum(1 for n in t1_main | t2_main if n % 2) == 5,
    "no uniform gap in either ticket": all(
        len({b - a for a, b in zip(sorted(m), sorted(m)[1:])}) > 1
        for m in (t1_main, t2_main)),
    "avoids last draw's main numbers": not ((t1_main | t2_main) & LAST_DRAW_MAIN),
    "avoids last draw's euro numbers": not ((t1_euro | t2_euro) & LAST_DRAW_EURO),
}
print()
for label, ok in checks.items():
    print(f"  [{'x' if ok else ' '}] {label}")
assert all(checks.values())

print("\nOn avoiding 23/34/39/45/49 and euro 1/4 from the last draw:")
print("  This is NOT a probability argument. Those numbers are exactly as")
print("  likely as any others tonight - the draw has no memory.")
print("  It is not even a solid popularity argument: the literature finds BOTH")
print("  gambler's fallacy (players avoid recent winners) and hot-hand chasing")
print("  (players pile onto them), and the direction is not settled for this")
print("  game. Avoiding them simply declines to bet on an unknown sign; the")
print("  stable criterion doing the real work is 32-50 plus no visible pattern.")


# --- 3. RTP at the new jackpot ----------------------------------------------
rule("3. RTP FOR THIS DRAW (JACKPOT EUR 15,000,000)")

p_jack = Fraction(tier_count(5, 2), TOTAL_OUTCOMES)
ev_jack_raw = float(JACKPOT) * float(p_jack)

# tiers 2-3 roll over with the jackpot; bracket them as before
scale = JACKPOT / REF_JACKPOT
ev_23_lo = EV_TIERS_2_3_AT_REF * scale
ev_23_hi = EV_TIERS_2_3_AT_REF

ev_lo = ev_jack_raw + EV_TIERS_4_12 + ev_23_lo
ev_hi = ev_jack_raw + EV_TIERS_4_12 + ev_23_hi

print(f"P(5+2)                      {float(p_jack):.4e}  (1 in {TOTAL_OUTCOMES:,})")
print(f"EV from jackpot             EUR {ev_jack_raw:.6f}   [exact given J]")
print(f"EV from tiers 4-12          EUR {EV_TIERS_4_12:.6f}   [calibrated on real payouts]")
print(f"EV from tiers 2-3 (5+1,5+0) EUR {ev_23_lo:.4f} .. {ev_23_hi:.4f}  [they roll too]")
print(f"\nEV per EUR 2.00 ticket      EUR {ev_lo:.4f} .. EUR {ev_hi:.4f}")
print(f"RTP                         {ev_lo / 2 * 100:.1f}% .. {ev_hi / 2 * 100:.1f}%")

prev_lo = float(PREV_JACKPOT) * float(p_jack) + EV_TIERS_4_12 \
    + EV_TIERS_2_3_AT_REF * (PREV_JACKPOT / REF_JACKPOT)
print(f"\nLast Friday (EUR 10m jackpot) the same calculation gave "
      f"{prev_lo / 2 * 100:.1f}% at the low end;")
print(f"the EUR 5m rollover adds about "
      f"{(ev_lo - prev_lo) / 2 * 100:.1f} pp. Still deeply negative.")

print(f"\nTwo tickets, EUR 4.00 staked:")
print(f"  expected return  EUR {2 * ev_lo:.2f} .. EUR {2 * ev_hi:.2f}")
print(f"  expected loss    EUR {4 - 2 * ev_hi:.2f} .. EUR {4 - 2 * ev_lo:.2f}")


# --- 4. jackpot splitting, and a correction to an earlier claim --------------
rule("4. JACKPOT SPLITTING - AND A CORRECTION TO THE 2026-08-28 REPORT")


def share_factor(n_tips, p=float(Fraction(1, TOTAL_OUTCOMES))):
    """
    E[1/(1+K)] where K ~ Binomial(n_tips-1, p) is the number of OTHER jackpot
    winners. Closed form: (1 - (1-p)^N) / (N*p) with N = n_tips.
    """
    return (1 - (1 - p) ** n_tips) / (n_tips * p)


print("A jackpot win is shared with everyone else holding the same combination.")
print("With N tips sold, the expected fraction of the jackpot a winner keeps is")
print("  E[1/(1+K)] = (1 - (1-p)^N) / (N*p),  K ~ Binomial(N-1, p)\n")
print(f"{'tips sold':>14} {'share kept':>12} {'haircut':>9}")
for n in (5_000_000, TIPS_ESTIMATE, 30_000_000, 60_000_000, 100_000_000):
    f = share_factor(n)
    tag = "  <- estimated from the 2026-08-28 draw" if n == TIPS_ESTIMATE else ""
    print(f"{n:>14,} {f:>11.4f} {(1 - f) * 100:>8.1f}%{tag}")

f_now = share_factor(TIPS_ESTIMATE)
print(f"\nAt tonight's likely volume the haircut is only "
      f"{(1 - f_now) * 100:.1f}%, so RTP becomes")
print(f"  {(ev_jack_raw * f_now + EV_TIERS_4_12 + ev_23_lo) / 2 * 100:.1f}% .. "
      f"{(ev_jack_raw * f_now + EV_TIERS_4_12 + ev_23_hi) / 2 * 100:.1f}%  "
      f"- a rounding-level change.")

print("\nCORRECTION. The 2026-08-28 report stated that Eurojackpot is EV-negative")
print("'even at the EUR 120m cap'. That rested on holding the lower tiers fixed")
print("at EUR 0.55, which the real payout data later showed to be wrong: tiers")
print("4-12 are worth EUR 0.410, but tiers 2-3 GROW with the jackpot. Redoing it:")

# break-even, modelling tiers 1-3 as scaling together with the jackpot
per_eur = float(p_jack) + EV_TIERS_2_3_AT_REF / REF_JACKPOT
be_nosplit = (2 - EV_TIERS_4_12) / per_eur
print(f"\n  tiers 1-3 combined yield  EUR {per_eur:.4e} per EUR of jackpot")
print(f"  break-even jackpot, ignoring splitting : EUR {be_nosplit:,.0f}")
print(f"  jackpot cap                            : EUR {JACKPOT_CAP:,}")
print(f"  => ignoring splitting, break-even sits BELOW the cap. My earlier")
print(f"     'impossible even at the cap' was too strong.")

print("\n  But a capped jackpot draws far more tips, and splitting is then real:")
for n in (30_000_000, 60_000_000, 100_000_000):
    f = share_factor(n)
    ev_cap = JACKPOT_CAP * float(p_jack) * f \
        + EV_TIERS_2_3_AT_REF * (JACKPOT_CAP / REF_JACKPOT) + EV_TIERS_4_12
    print(f"    at cap with {n:>11,} tips: RTP = {ev_cap / 2 * 100:5.1f}%")

print("\n  So the honest statement is: at EUR 15m tonight the game is far from")
print("  break-even; a capped EUR 120m jackpot could approach break-even on")
print("  paper, but only if ticket sales stayed low - and they do not, because")
print("  a capped jackpot is exactly what drives volume up. Add tax where it")
print("  applies and the margin goes with it. Tonight none of this is close.")


# --- 5. tier distribution ----------------------------------------------------
rule("5. TIER DISTRIBUTION FOR TONIGHT")

RANK = {tier: i for i, (tier, _) in enumerate(TIPOS_OFFICIAL, start=1)}
from exact_model import joint_distribution

agg = {}
for (mA, eA, mB, eB), w in joint_distribution(0, 0).items():
    ranks = [RANK[t] for t in ((mA, eA), (mB, eB)) if t in PAYING]
    agg[min(ranks) if ranks else None] = agg.get(min(ranks) if ranks else None, 0) + w

inv = {v: k for k, v in RANK.items()}
print(f"{'#':>3} {'tier':>5} {'P(best tier), 2 tickets':>25} {'1 in':>12}")
for r in sorted(x for x in agg if x is not None):
    p = Fraction(agg[r], TOTAL_OUTCOMES)
    k, j = inv[r]
    print(f"{r:>3} {k}+{j:<3} {float(p) * 100:>24.7f}% {1 / float(p):>12,.0f}")
print(f"{'-':>3} {'none':>5} {float(Fraction(agg[None], TOTAL_OUTCOMES)) * 100:>24.7f}%")
assert sum(agg.values()) == TOTAL_OUTCOMES
