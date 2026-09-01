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

RANK = {tier: i for i, (tier, _) in enumerate(TIPOS_OFFICIAL, start=1)}
STAKE_PER_TICKET = 2.00

# Reference prize levels (observed real payouts; the exact amount for a given
# draw is pari-mutuel and only known from that draw's own payout table).
REFERENCE_PRIZE = {
    (5, 2): None, (5, 1): None, (5, 0): None,
    (4, 2): 4_324.50, (4, 1): 334.30, (3, 2): 130.20, (4, 0): 129.70,
    (2, 2): 23.60, (3, 1): 20.70, (3, 0): 19.20, (1, 2): 13.30, (2, 1): 9.30,
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
]

rule = lambda t: print("\n" + "=" * 76 + f"\n{t}\n" + "=" * 76)


def settle(s):
    dm, de = s["draw"]
    assert len(dm) == 5 and len(de) == 2
    rule(f"DRAW {s['date']}")
    print(f"main : {sorted(dm)}")
    print(f"euro : {sorted(de)}")
    print(f"jackpot played for: EUR {s['jackpot']:,}\n")

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
print(f"draws settled   : {len(SETTLEMENTS)}")
print(f"tickets bought  : {sum(len(s['tickets']) for s in SETTLEMENTS)}")
print(f"staked          : EUR {total_staked:.2f}")
print(f"returned        : ~EUR {total_returned:.2f}  (reference prize levels)")
print(f"net             : ~EUR {total_returned - total_staked:+.2f}")

p_any_two = Fraction(2_190_533, 34_959_540)
n = len(SETTLEMENTS)
exp_wins = float(p_any_two) * n
print(f"\nexpected winning DRAWS out of {n}: {exp_wins:.3f}")
print(f"observed                        : 1")
print(f"\nP(at least one winning draw in {n}) "
      f"= {(1 - (1 - float(p_any_two)) ** n) * 100:.2f}%")
print(f"P(no prize at all in {n} draws)  "
      f"= {(1 - float(p_any_two)) ** n * 100:.2f}%")


rule("ON THE 2026-09-01 RESULT SPECIFICALLY")

print("Ticket 2 landed on 2+0. The minimum paying tiers are 2+1 and 1+2, so a")
print("single euro number separated it from tier 12 (about EUR 9.30).")
print("\nThat 'near miss' is worth naming for what it is: 2+0 is simply a losing")
print("outcome, statistically no closer to winning than 0+0. The sense of having")
print("almost won is a documented design feature of lottery products, not")
print("information. P(2+1) was 1 in 49.27 before the draw and is 1 in 49.27")
print("for the next one, whatever happened tonight.")

print("\nAlso note ticket 2 held 9 as a EURO number while 9 was drawn as a MAIN")
print("number. The two pools are separate draws; a number matching in one pool")
print("has no bearing on the other.")

print(f"\nThe outcome was the single most likely one: both tickets losing had")
print(f"probability 93.734091%. Nothing about this draw was surprising, and")
print(f"nothing about it changes the odds of the next.")
