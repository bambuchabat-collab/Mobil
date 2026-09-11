"""
Settlement of the tickets against the draws they were bought for.

Draw numbers are only used after confirmation by at least two DATED sources.
The undated payout table seen in an earlier screenshot belongs to a different,
older draw and is never used here.

  2026-08-28 (draw 985): TIPOS app results panel dated 28.08.2026;
                         lotteryextreme.com "Friday, 28 August 2026 (Draw 985)"
  2026-09-01 (draw 986): lotteryextreme.com "1 September 2026 Tue - Draw 986";
                         euro-jackpot.net 2026 archive;
                         eurojackpot-numbers.com dated 01/09/2026
"""

from fractions import Fraction

from exact_model import TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count
from draws import DRAWS, euro_draws

n_all = len(DRAWS)
ED = euro_draws()

RANK = {tier: i for i, (tier, _) in enumerate(TIPOS_OFFICIAL, start=1)}
STAKE_PER_TICKET = 2.00

# Reference prize levels (observed real payouts; the exact amount for a given
# draw is pari-mutuel and only known from that draw's own payout table).
# Levels from draw 988 (2026-09-08) - a real, DATED, complete payout table.
# The actual amount for any given draw is pari-mutuel and only known from that
# draw's own table; in particular the 3+0 paid on 2026-08-28 was never verified.
REFERENCE_PRIZE = {
    (5, 2): None, (5, 1): None, (5, 0): None,
    (4, 2): 3_345.00, (4, 1): 238.90, (3, 2): 94.20, (4, 0): 152.60,
    (2, 2): 25.30, (3, 1): 17.20, (3, 0): 16.80, (1, 2): 12.80, (2, 1): 9.20,
}

SETTLEMENTS = [
    {
        "date": "2026-08-28 (Friday, draw 985)",
        "jackpot": 10_000_000,
        "draw": ({23, 34, 39, 45, 49}, {1, 4}),
        "tickets": [("Ticket 1", {33, 38, 42, 47, 50}, {5, 11}),
                    ("Ticket 2", {34, 36, 43, 45, 49}, {8, 12})],
    },
    {
        "date": "2026-09-01 (Tuesday, draw 986)",
        "jackpot": 15_000_000,
        "draw": ({9, 14, 35, 43, 50}, {3, 7}),
        "tickets": [("Ticket 1", {33, 37, 40, 44, 50}, {6, 11}),
                    ("Ticket 2", {35, 41, 43, 46, 48}, {9, 12})],
    },
    {
        "date": "2026-09-04 (Friday, draw 987)",
        "jackpot": 23_000_000,
        "draw": ({5, 14, 31, 33, 43}, {3, 4}),
        "tickets": [("Ticket 1", {32, 39, 41, 46, 49}, {6, 10}),
                    ("Ticket 2", {34, 38, 45, 47, 48}, {9, 11})],
    },
    {
        # Actually purchased, per the TIPOS ticket screenshot: 3 fields, EUR 6.00.
        # These are the player's own numbers, not this analysis's recommendation
        # (no recommendation was produced for this draw).
        "date": "2026-09-08 (Tuesday, draw 988)",
        "jackpot": 31_000_000,
        "source": "player",
        "draw": ({14, 27, 34, 36, 47}, {3, 4}),
        "tickets": [("Field 1", {5, 9, 10, 40, 50}, {3, 11}),
                    ("Field 2", {4, 35, 43, 44, 47}, {6, 8}),
                    ("Field 3", {17, 25, 26, 41, 47}, {5, 10})],
    },
    {
        "date": "2026-09-11 (Friday, draw 989)",
        "jackpot": 40_000_000,
        "draw": ({14, 21, 35, 37, 49}, {1, 12}),
        "tickets": [("Ticket 1", {35, 38, 39, 44, 50}, {6, 11}),
                    ("Ticket 2", {32, 37, 42, 45, 46}, {8, 12}),
                    ("Ticket 3", {36, 40, 41, 43, 47}, {5, 10})],
    },
]

rule = lambda t: print("\n" + "=" * 76 + f"\n{t}\n" + "=" * 76)


def settle(s):
    dm, de = s["draw"]
    assert len(dm) == 5 and len(de) == 2
    rule(f"DRAW {s['date']}")
    print(f"main : {sorted(dm)}")
    print(f"euro : {sorted(de)}")
    print(f"jackpot played for: EUR {s['jackpot']:,}")
    src = s.get("source", "recommendation")
    label = ("numbers actually purchased (from the ticket screenshot)"
             if src == "player" else
             "numbers recommended by this analysis (purchase not confirmed)")
    print(f"tickets: {len(s['tickets'])} x EUR {STAKE_PER_TICKET:.2f} - {label}\n")

    staked = 0.0
    returned = 0.0
    unknown_prize = False
    for name, main, euro in s["tickets"]:
        staked += STAKE_PER_TICKET
        hm, he = main & dm, euro & de
        k, j = len(hm), len(he)
        won = (k, j) in PAYING
        print(f"{name}: {sorted(main)} + {sorted(euro)}")
        print(f"   main hit: {sorted(hm) or '-'} ({k})   euro hit: {sorted(he) or '-'} ({j})")
        if won:
            p = Fraction(tier_count(k, j), TOTAL_OUTCOMES)
            ref = REFERENCE_PRIZE[(k, j)]
            print(f"   -> {k}+{j}  PRIZE, tier {RANK[(k, j)]} of 12  "
                  f"(1 in {1 / float(p):,.0f})")
            if ref is None:
                unknown_prize = True
                print(f"      amount: top-tier, pari-mutuel - not estimated here")
            else:
                returned += ref
                print(f"      reference level ~EUR {ref:,.2f} "
                      f"(actual amount is that draw's own pari-mutuel figure)")
        else:
            print(f"   -> {k}+{j}  no prize")
    return staked, returned, unknown_prize


total_staked = total_returned = 0.0
for s in SETTLEMENTS:
    st, rt, _ = settle(s)
    total_staked += st
    total_returned += rt

rule("RUNNING TOTAL")

p_one = Fraction(133_127, 4_237_520)          # P(any prize), one ticket
n_tickets = sum(len(s["tickets"]) for s in SETTLEMENTS)
exp_prizes = float(p_one) * n_tickets

print(f"draws settled   : {len(SETTLEMENTS)}")
print(f"tickets settled : {n_tickets}")
print(f"staked          : EUR {total_staked:.2f}")
print(f"returned        : ~EUR {total_returned:.2f}  (reference prize levels)")
print(f"net             : ~EUR {total_returned - total_staked:+.2f}")
print(f"\nexpected prizes across {n_tickets} tickets: {exp_prizes:.3f}")
print(f"observed                        : 1  (the 3+0 on 2026-08-28)")

print("\nIMPORTANT CAVEAT ON THIS TOTAL.")
print("Only the 2026-09-08 line is a confirmed purchase - the ticket screenshot")
print("shows the actual fields and the EUR 6.00 stake. For 2026-08-28, 09-01 and")
print("09-04 this settles the numbers this analysis RECOMMENDED; I have no")
print("confirmation those were the tickets bought, and the 09-08 ticket shows")
print("different numbers and three fields rather than two. So the running total")
print("above is the recommendation's track record, not necessarily the wallet's.")

by_src = {}
for s in SETTLEMENTS:
    k = s.get("source", "recommendation")
    by_src[k] = by_src.get(k, 0) + len(s["tickets"]) * STAKE_PER_TICKET
print(f"\nof which staked on confirmed player numbers : "
      f"EUR {by_src.get('player', 0):.2f}")
print(f"          staked on recommended numbers      : "
      f"EUR {by_src.get('recommendation', 0):.2f}")


rule("ON THE 2026-09-11 RESULT")

print("Ticket 1 took 35            -> 1+0, not a paying tier")
print("Ticket 2 took 37 and euro 12 -> 1+1, not a paying tier")
print("Ticket 3 took nothing        -> 0+0")
print("All three lost. EUR 6.00 gone.")
print("\n1+1 is the nearest of the three to a prize: one more main number would")
print("have made 2+1, one more euro would have made 1+2. It is still simply a")
print("losing outcome - 'one away' is not a tier and carries no information.")
print(f"\nP(all three tickets lose) = 90.6271% - the ordinary result.")

print("\nJACKPOT STATUS UNRESOLVED. The two sources disagree:")
print("  lotteryextreme.com : 5+2 had NO winners (so the jackpot rolls up)")
print("  eurojackpot-numbers.com : next draw 15/09 carries EUR 10m (the reset")
print("    minimum, which would mean the EUR 40m WAS won)")
print("The second source also states this draw's jackpot was EUR 10m, which is")
print("plainly wrong - three sources put it at EUR 40m before the draw. That")
print("makes its jackpot fields look stale, but I am not resolving it on that")
print("basis alone. The ticket settlement above does not depend on it.")


rule("YOUR THREE FIELDS (2026-09-08) - EXACT ODDS OF THE CONFIGURATION PLAYED")

from itertools import combinations
from math import comb


def exact_multi(tickets):
    """
    Exact P(at least one prize) for any number of tickets, by enumerating all
    C(50,5) main draws and all C(12,2) euro draws. Their product is the whole
    139,838,160-outcome space, so this is exact, not sampled.
    """
    mains = [t[1] for t in tickets]
    euros = [t[2] for t in tickets]
    mt = {}
    for d in combinations(range(1, 51), 5):
        s = set(d)
        k = tuple(len(s & m) for m in mains)
        mt[k] = mt.get(k, 0) + 1
    et = {}
    for d in combinations(range(1, 13), 2):
        s = set(d)
        k = tuple(len(s & e) for e in euros)
        et[k] = et.get(k, 0) + 1
    total = win = 0
    for mk, wm in mt.items():
        for ek, we in et.items():
            w = wm * we
            total += w
            if any((mk[i], ek[i]) in PAYING for i in range(len(tickets))):
                win += w
    assert total == TOTAL_OUTCOMES
    return Fraction(win, total)


s0908 = next(s for s in SETTLEMENTS if s["date"].startswith("2026-09-08"))
played = s0908["tickets"]
p_played = exact_multi(played)

# best possible 3-ticket layout: 15 distinct mains, 3 disjoint euro pairs
optimal = [("A", {1, 2, 3, 4, 5}, {1, 2}),
           ("B", {6, 7, 8, 9, 10}, {3, 4}),
           ("C", {11, 12, 13, 14, 15}, {5, 6})]
p_opt = exact_multi(optimal)

all_main = set().union(*(t[1] for t in played))
all_euro = set().union(*(t[2] for t in played))
print(f"Your fields covered {len(all_main)} distinct main numbers "
      f"(47 appears in two fields) and {len(all_euro)} distinct euro numbers.")
print(f"\n  P(any prize), your three fields   : {float(p_played) * 100:.6f}%  "
      f"(1 in {1 / float(p_played):.2f})")
print(f"  P(any prize), optimal three fields: {float(p_opt) * 100:.6f}%  "
      f"(1 in {1 / float(p_opt):.2f})")
print(f"  difference                        : "
      f"{(float(p_opt) - float(p_played)) * 100:+.6f} pp")
print(f"\n  For reference, two optimal tickets: 6.265909%")
print(f"\nThe optimal 3-field layout is 15 different main numbers and three")
print(f"non-overlapping euro pairs. Repeating 47 across two fields costs you")
print(f"{(float(p_opt) - float(p_played)) * 100:.4f} pp - small, but it is the only")
print(f"lever that exists, and it is free to pull.")


