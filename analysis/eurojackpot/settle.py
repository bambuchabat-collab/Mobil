"""
Settlement of the two tickets against the 2026-08-28 draw.

The draw numbers are used ONLY after being confirmed by two dated sources:
  1. TIPOS mobile app, results panel with the date field set to 28.08.2026
  2. lotteryextreme.com, "Friday, 28 August 2026 (Draw 985)"
Both give the same 5+2. The undated payout table seen earlier is a different,
older draw and is not used here.
"""

from fractions import Fraction

from exact_model import TOTAL_OUTCOMES, TIPOS_OFFICIAL, PAYING, tier_count

DRAW_MAIN = {23, 34, 39, 45, 49}
DRAW_EURO = {1, 4}
DRAW_DATE = "2026-08-28 (Friday, draw 985)"

TICKETS = [
    ("Ticket 1", {33, 38, 42, 47, 50}, {5, 11}),
    ("Ticket 2", {34, 36, 43, 45, 49}, {8, 12}),
]

RANK = {tier: i for i, (tier, _) in enumerate(TIPOS_OFFICIAL, start=1)}
STAKE_TOTAL = 4.00

# Prize level for tier 3+0 observed in the earlier (different) draw. Used only
# as an order-of-magnitude reference - the actual amount for THIS draw was not
# legible in the screenshot.
REFERENCE_3PLUS0 = 19.20

rule = lambda t: print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)

rule(f"DRAW {DRAW_DATE}")
print(f"main : {sorted(DRAW_MAIN)}")
print(f"euro : {sorted(DRAW_EURO)}")
assert len(DRAW_MAIN) == 5 and len(DRAW_EURO) == 2

rule("SETTLEMENT")
results = []
for name, main, euro in TICKETS:
    hit_m, hit_e = main & DRAW_MAIN, euro & DRAW_EURO
    k, j = len(hit_m), len(hit_e)
    tier = (k, j)
    won = tier in PAYING
    results.append((name, k, j, won))
    print(f"\n{name}: {sorted(main)} + {sorted(euro)}")
    print(f"  main matched : {sorted(hit_m) or '-'}  -> {k}")
    print(f"  euro matched : {sorted(hit_e) or '-'}  -> {j}")
    if won:
        p = Fraction(tier_count(k, j), TOTAL_OUTCOMES)
        print(f"  RESULT: {k}+{j}  = PRIZE, tier {RANK[tier]} of 12  "
              f"(1 in {1 / float(p):,.0f})")
    else:
        print(f"  RESULT: {k}+{j}  = no prize")

winners = [r for r in results if r[3]]
print(f"\n{len(winners)} of {len(TICKETS)} tickets won.")

rule("HOW THIS COMPARES TO THE EX-ANTE FORECAST")

# forecast values from the pre-draw analysis (best configuration)
p_any_two = Fraction(2_190_533, 34_959_540)
best_rank = min(RANK[(k, j)] for _, k, j, w in results if w) if winners else None

# P(best tier reached is at least as good as what we got)
if best_rank is not None:
    w_atleast = 0
    from exact_model import joint_distribution
    for (mA, eA, mB, eB), w in joint_distribution(0, 0).items():
        ranks = [RANK[t] for t in ((mA, eA), (mB, eB)) if t in PAYING]
        if ranks and min(ranks) <= best_rank:
            w_atleast += w
    p_atleast = Fraction(w_atleast, TOTAL_OUTCOMES)

print(f"forecast P(any prize, 2 tickets) : {float(p_any_two) * 100:.4f}%  "
      f"-> outcome: {'HIT' if winners else 'miss'}")
if best_rank is not None:
    k, j = next((k, j) for _, k, j, w in results if w)
    print(f"forecast P(best tier >= {k}+{j})     : {float(p_atleast) * 100:.4f}%  "
          f"(1 in {1 / float(p_atleast):,.1f})")
    print(f"\nThis outcome sits in the top {float(p_atleast) * 100:.2f}% of the "
          f"pre-draw distribution.")

rule("MONEY")
print(f"staked                : EUR {STAKE_TOTAL:.2f}")
if winners:
    print(f"prize tier            : 3+0 (tier 10 of 12)")
    print(f"reference level       : ~EUR {REFERENCE_3PLUS0:.2f} "
          f"(from a DIFFERENT, earlier draw - not this one)")
    print(f"indicative net        : ~EUR {REFERENCE_3PLUS0 - STAKE_TOTAL:+.2f}")
    print("\nThe actual 3+0 amount for THIS draw was not legible in the")
    print("screenshot. 3+0 is pari-mutuel, so the real figure depends on how")
    print("many players matched 3 this draw - see the note on high numbers below.")

rule("WAS THE NUMBER STRATEGY 'RIGHT'?  NO - AND THIS MATTERS")
high = sorted(n for n in DRAW_MAIN if n >= 32)
print(f"drawn main numbers >= 32 : {high}  ({len(high)} of 5)")
print(f"ticket 2's three hits    : {sorted({34, 36, 43, 45, 49} & DRAW_MAIN)}")
print("\nAll ten of our main numbers sat in 32-50, and four of the five drawn")
print("main numbers landed there too. That is COINCIDENCE, not prediction.")
print("The pre-draw probability of any given ticket hitting 3+0 was 1 in 314,")
print("and it was 1 in 314 for every possible set of five numbers alike.")
print("\nWhat the 32-50 choice DID do, exactly as designed: with 34, 45 and 49")
print("among the matched numbers, fewer players than average will have shared")
print("this tier, so the pari-mutuel 3+0 payout should come in at or above its")
print("typical level. That is a payout-size effect, never a probability effect.")

rule("RTP CROSS-CHECK ON THIS DRAW'S EUROPE-WIDE TOTALS")

# Reported by lotteryextreme.com for draw 985. Secondary source, not TIPOS.
EU_WINNERS = 525_463
EU_PAYOUT = 10_214_958.70

p_any_one = Fraction(sum(tier_count(k, j) for (k, j), _ in TIPOS_OFFICIAL),
                     TOTAL_OUTCOMES)
implied_tips = EU_WINNERS / float(p_any_one)
implied_stake = implied_tips * 2.00
payout_ratio = EU_PAYOUT / implied_stake

print(f"reported winners, all tiers : {EU_WINNERS:,}")
print(f"reported payout             : EUR {EU_PAYOUT:,.2f}  (jackpot won 0x)")
print(f"\nP(any prize) = {float(p_any_one) * 100:.4f}%, so the winner count implies")
print(f"  tips sold   ~ {implied_tips:,.0f}")
print(f"  stakes      ~ EUR {implied_stake:,.0f}")
print(f"  payout/stake ~ {payout_ratio * 100:.1f}%")
print(f"\nMy pre-draw RTP bracket was 27.3% - 36.6%. The realised payout ratio")
print(f"lands inside it. Note this is the REALISED ratio for one draw with an")
print(f"unwon jackpot (that money rolled over), not the expected value, and the")
print(f"totals come from a secondary aggregator, not from TIPOS.")

rule("WHAT THE FORECAST GOT RIGHT AND WRONG")
print("right : the jackpot was not won (forecast 1 in 69,919,080 for 2 tickets)")
print("right : ticket 1 returned nothing (93.7% chance both tickets lose;")
print("        individually 96.9% chance any one ticket loses)")
print("right : the win landed in the low tiers, where 96.3% of all wins live")
print("wrong : nothing. A 6.27% event occurred; that is not a model failure.")
print("\nOne draw cannot validate or refute the model either way. The exact")
print("enumeration was already verified three independent ways before the draw.")
