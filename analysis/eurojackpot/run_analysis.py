"""
Eurojackpot analysis for the draw of Friday 2026-08-28.

Runs, in order:
  1. Exact per-tier probabilities, cross-checked against the official TIPOS table.
  2. P(any prize) for one ticket and for two tickets.
  3. P(>=4 main) and P(4+2) for two tickets.
  4. RTP given the current jackpot.
  5. Feasibility check: can two disjoint tickets both win in one draw?
  6. Explicit comparison of two-ticket configurations.
  7. Does the euro-pair choice affect P(4+2)?
  9. Power of a frequency (chi-square) test on past draws.
"""

from fractions import Fraction
from math import comb, sqrt
from itertools import combinations

from exact_model import (
    MAIN_POOL, MAIN_PICK, EURO_POOL, EURO_PICK, TOTAL_OUTCOMES,
    TIPOS_OFFICIAL, PAYING, tier_count, single_ticket_table,
    p_any_prize_single, two_ticket_stats, fmt,
)

STAKE = Fraction(2)                 # EUR per tip, verified on tipos.sk
JACKPOT = 10_000_000                # EUR, tipos.sk + independent source
JACKPOT_CAP = 120_000_000           # EUR, secondary sources
PRIZE_FUND_SHARE = Fraction(1, 2)   # 50% of stakes, secondary sources
JACKPOT_TIER_SHARE = Fraction(36, 100)
BOOSTER_SHARE = Fraction(9, 100)
LOWER_TIER_SHARE = 1 - JACKPOT_TIER_SHARE - BOOSTER_SHARE   # 55%

rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --- 1. tier probabilities vs the official TIPOS table -----------------------
rule("1. PER-TIER PROBABILITIES  (exact enumeration vs official TIPOS table)")

print(f"C(50,5) = {comb(50, 5):,}   C(12,2) = {comb(12, 2):,}")
print(f"total outcomes = {TOTAL_OUTCOMES:,}\n")
print(f"{'#':>3} {'tier':>5} {'outcomes':>10} {'exact odds 1:N':>18} "
      f"{'TIPOS 1:N':>12}  match")

all_match = True
for idx, ((k, j), official) in enumerate(TIPOS_OFFICIAL, start=1):
    cnt = tier_count(k, j)
    exact_odds = Fraction(TOTAL_OUTCOMES, cnt)
    # TIPOS prints the odds denominator truncated/rounded to an integer
    ok = int(exact_odds) == official or round(float(exact_odds)) == official
    all_match &= ok
    print(f"{idx:>3} {k}+{j:<3} {cnt:>10,} {float(exact_odds):>18,.2f} "
          f"{official:>12,}  {'OK' if ok else 'MISMATCH'}")

print()
if not all_match:
    raise SystemExit("MODEL INVALID: a tier disagrees with the official table. Analysis stopped.")
print("All 12 tiers reproduce the official TIPOS odds -> model validated.")

# sanity: every outcome is accounted for
assert sum(tier_count(k, j) for k in range(6) for j in range(3)) == TOTAL_OUTCOMES

print("\nNon-paying states (for completeness):")
for k in range(MAIN_PICK + 1):
    for j in range(EURO_PICK + 1):
        if (k, j) not in PAYING:
            c = tier_count(k, j)
            print(f"   {k}+{j}: {c:>12,} outcomes  "
                  f"({float(Fraction(c, TOTAL_OUTCOMES)) * 100:6.3f}%)")


# --- 2. P(any prize) ---------------------------------------------------------
rule("2. P(ANY PRIZE)")

p1 = p_any_prize_single()
print(f"one ticket : {fmt(p1)}")
print(f"             exact fraction = {p1.numerator:,} / {p1.denominator:,}")

losing = 1 - p1
print(f"             P(no prize)    = {float(losing) * 100:.6f}%")


# --- 5. can two disjoint tickets both win? -----------------------------------
rule("5. CAN TWO TICKETS WITH DISJOINT MAIN NUMBERS BOTH WIN IN ONE DRAW?")

print("Minimum paying tiers are 2+1 and 1+2.")
print("If the two tickets shared no main numbers, the total main matches across")
print("both tickets can be at most 5 (only 5 main numbers are drawn).")
print("Question: is 'both win' reachable within that budget?\n")

for e_ov in (0, 1, 2):
    st = two_ticket_stats(0, e_ov)
    print(f"  disjoint mains, euro overlap {e_ov}: P(both tickets win) = "
          f"{fmt(st['p_both_win'])}")

print("\nExplicit witnesses, found by constructive search over real number sets")
print("(tickets have disjoint main numbers; the draw is evaluated directly):")


def find_witness(A_main, A_euro, B_main, B_euro):
    """Search for a concrete draw in which BOTH tickets win. Returns None if none."""
    outside = [n for n in range(1, MAIN_POOL + 1) if n not in A_main | B_main]
    for euro_draw in combinations(range(1, EURO_POOL + 1), EURO_PICK):
        ed = set(euro_draw)
        eA, eB = len(A_euro & ed), len(B_euro & ed)
        for nA in range(MAIN_PICK + 1):
            for nB in range(MAIN_PICK + 1 - nA):
                if (nA, eA) not in PAYING or (nB, eB) not in PAYING:
                    continue
                filler = MAIN_PICK - nA - nB
                md = (set(sorted(A_main)[:nA]) | set(sorted(B_main)[:nB])
                      | set(outside[:filler]))
                if len(md) != MAIN_PICK:
                    continue
                assert len(A_main & md) == nA and len(B_main & md) == nB
                return md, ed, (nA, eA), (nB, eB)
    return None


A_main, B_main = {1, 2, 3, 4, 5}, {6, 7, 8, 9, 10}
for label, A_euro, B_euro in [
    ("disjoint euro pairs", {1, 2}, {3, 4}),
    ("euro pairs sharing one", {1, 2}, {2, 3}),
    ("identical euro pairs", {1, 2}, {1, 2}),
]:
    w = find_witness(A_main, A_euro, B_main, B_euro)
    assert w is not None, f"no witness found for {label}"
    md, ed, (nA, eA), (nB, eB) = w
    print(f"\n  [{label}]")
    print(f"    ticket A {sorted(A_main)} + {sorted(A_euro)}")
    print(f"    ticket B {sorted(B_main)} + {sorted(B_euro)}")
    print(f"    draw     {sorted(md)} + {sorted(ed)}")
    print(f"    -> A wins {nA}+{eA}, B wins {nB}+{eB}  "
          f"(main matches used: {nA}+{nB} = {nA + nB} <= 5)")
print("\n  CONCLUSION: 2 x threshold > 5 is FALSE. Both tickets CAN win in the same")
print("  draw even with disjoint main numbers, in every euro configuration.")
print("  Therefore probabilities do NOT simply add:")
print("  P(A or B) = P(A) + P(B) - P(both), strictly less than 2*P(A).")


# --- 6. configuration comparison ---------------------------------------------
rule("6. TWO-TICKET CONFIGURATIONS COMPARED ON P(ANY PRIZE)")

configs = [(a, e) for a in range(MAIN_PICK + 1) for e in range(EURO_PICK + 1)]
results = [two_ticket_stats(a, e) for a, e in configs]

naive_sum = 2 * p1
print(f"naive 2*P(one ticket) (ignores overlap) = {float(naive_sum) * 100:.6f}%\n")
print(f"{'main ov':>7} {'euro ov':>7} {'P(any prize, 2 tickets)':>24} "
      f"{'P(both win)':>14} {'vs best (pp)':>13}")

best = max(results, key=lambda r: r["p_union_any_prize"])
for r in sorted(results, key=lambda r: -r["p_union_any_prize"]):
    delta = (float(r["p_union_any_prize"]) - float(best["p_union_any_prize"])) * 100
    tag = "  <-- BEST" if r is best else ""
    print(f"{r['main_overlap']:>7} {r['euro_overlap']:>7} "
          f"{float(r['p_union_any_prize']) * 100:>23.6f}% "
          f"{float(r['p_both_win']) * 100:>13.6f}% {delta:>13.6f}{tag}")

print("\nThe three configurations the brief asks to compare explicitly:")
named = [
    ("disjoint mains + DIFFERENT (disjoint) euro pairs", 0, 0),
    ("disjoint mains + IDENTICAL euro pairs", 0, 2),
    ("overlapping mains (3 shared) + disjoint euro pairs", 3, 0),
]
base = None
for label, a, e in named:
    r = two_ticket_stats(a, e)
    if base is None:
        base = r["p_union_any_prize"]
    d = (float(r["p_union_any_prize"]) - float(base)) * 100
    print(f"  {label:<52} {float(r['p_union_any_prize']) * 100:.6f}%   "
          f"delta = {d:+.6f} pp")

winner = two_ticket_stats(0, 0)
print(f"\nBEST CONFIGURATION: disjoint main numbers + disjoint euro pairs")
print(f"  P(any prize, 2 tickets) = {fmt(winner['p_union_any_prize'])}")
print(f"  exact = {winner['p_union_any_prize'].numerator:,} / "
      f"{winner['p_union_any_prize'].denominator:,}")


# --- 3. P(>=4 main) and P(4+2) for two tickets -------------------------------
rule("3. P(>=4 MAIN NUMBERS) AND P(4+2) FOR TWO TICKETS")

p_ge4_one = sum(Fraction(tier_count(k, j), TOTAL_OUTCOMES)
                for k in (4, 5) for j in range(EURO_PICK + 1))
p_42_one = Fraction(tier_count(4, 2), TOTAL_OUTCOMES)

print(f"one ticket, >=4 main : {fmt(p_ge4_one)}")
print(f"one ticket, 4+2      : {fmt(p_42_one)}")
print(f"\ntwo tickets (best config, disjoint mains + disjoint euro pairs):")
print(f"  >=4 main : {fmt(winner['p_union_ge4_main'])}")
print(f"  4+2      : {fmt(winner['p_union_4plus2'])}")
print(f"  P(both tickets hit 4+2) = {fmt(winner['p_both_4plus2'])}")
print(f"\n  exactly 2x the single-ticket value? "
      f">=4 main: {winner['p_union_ge4_main'] == 2 * p_ge4_one}, "
      f"4+2: {winner['p_union_4plus2'] == 2 * p_42_one}")


# --- 7. does the euro pair choice affect P(4+2)? -----------------------------
rule("7. DOES THE EURO-PAIR CHOICE AFFECT P(4+2) FOR TWO TICKETS?")

print("Argument: 'at least one ticket hits 4+2' has probability")
print("  2*P(4+2) - P(both hit 4+2).")
print("The euro choice can only matter through the P(both) term.")
print("Both tickets hit 4+2 => each matches 4 of the 5 drawn main numbers,")
print("so |A n D| = |B n D| = 4 with |D| = 5, forcing |A n B n D| >= 3,")
print("which requires the tickets to SHARE at least 3 main numbers.\n")

print(f"{'main ov':>7} " + " ".join(f"{'euro ov ' + str(e):>22}" for e in range(3)))
for a in range(MAIN_PICK + 1):
    row = [f"{float(two_ticket_stats(a, e)['p_union_4plus2']) * 100:>22.9f}"
           for e in range(3)]
    print(f"{a:>7} " + " ".join(row))

print("\nRows for main overlap 0, 1, 2 are constant across euro overlap:")
for a in range(3):
    vals = {two_ticket_stats(a, e)["p_union_4plus2"] for e in range(3)}
    print(f"  main overlap {a}: identical for all euro choices = {len(vals) == 1}")
print("\nANSWER: with disjoint (or <=2-overlapping) main numbers the euro-pair")
print("choice has NO effect on P(4+2) whatsoever - the two 4+2 events are")
print("mutually exclusive for main reasons alone, so P = 2*P(4+2) exactly.")
print("The euro choice only starts to matter at main overlap >= 3, and even then")
print("only when both euro pairs are identical (both need e=2, and only one euro")
print("pair is drawn).")


# --- 4. RTP ------------------------------------------------------------------
rule("4. RTP (RETURN TO PLAYER) AT THE CURRENT JACKPOT")

p_jackpot = Fraction(tier_count(5, 2), TOTAL_OUTCOMES)
ev_jackpot = Fraction(JACKPOT) * p_jackpot
ev_lower = LOWER_TIER_SHARE * PRIZE_FUND_SHARE * STAKE
ev_total = ev_jackpot + ev_lower

print(f"jackpot for this draw            EUR {JACKPOT:,}  (minimum guaranteed level)")
print(f"P(5+2)                           {float(p_jackpot):.3e}  (1 in {TOTAL_OUTCOMES:,})")
print(f"\nEV from the jackpot tier         EUR {float(ev_jackpot):.6f}  [exact given J]")
print(f"EV from the 11 lower tiers       EUR {float(ev_lower):.6f}  "
      f"[{float(LOWER_TIER_SHARE) * 100:.0f}% of a {float(PRIZE_FUND_SHARE) * 100:.0f}% prize fund]")
print(f"EV total per EUR 2.00 ticket     EUR {float(ev_total):.6f}")
print(f"\nRTP this draw                    {float(ev_total / STAKE) * 100:.2f}%")
print(f"house edge this draw             {float(1 - ev_total / STAKE) * 100:.2f}%")
print(f"long-run design RTP              {float(PRIZE_FUND_SHARE) * 100:.0f}% "
      f"(the 9% booster fund returns to future jackpots)")

print(f"\nTwo tickets: EUR 4.00 staked, expected return EUR {float(2 * ev_total):.4f}, "
      f"expected loss EUR {float(2 * (STAKE - ev_total)):.4f}")

# break-even jackpot and the cap
be_jackpot = (STAKE - ev_lower) / p_jackpot
ev_at_cap = Fraction(JACKPOT_CAP) * p_jackpot + ev_lower
print(f"\nJackpot needed for RTP = 100%    EUR {float(be_jackpot):,.0f}")
print(f"Eurojackpot jackpot cap          EUR {JACKPOT_CAP:,}")
print(f"RTP at the cap                   {float(ev_at_cap / STAKE) * 100:.2f}%")
print(f"=> even at the hard cap the game is EV-negative: "
      f"{float(be_jackpot) > JACKPOT_CAP}")
print("   (and this ignores jackpot splitting between multiple winners,")
print("    which can only push the EV further down)")


# --- 9. power of a frequency test --------------------------------------------
rule("9. FREQUENCY ANALYSIS: WHY IT IS NOT USED (power calculation)")

p0 = Fraction(MAIN_PICK, MAIN_POOL)          # 5/50 = 0.1 per number per draw
rel_bias = 0.10
p1_alt = float(p0) * (1 + rel_bias)


def required_draws(alpha_z, power_z, p_null, p_alt):
    num = (alpha_z * sqrt(p_null * (1 - p_null)) + power_z * sqrt(p_alt * (1 - p_alt))) ** 2
    return num / (p_alt - p_null) ** 2


n_single = required_draws(1.959964, 0.841621, float(p0), p1_alt)
n_bonf = required_draws(3.290527, 0.841621, float(p0), p1_alt)   # alpha/50, two-sided

print(f"Each number appears in a draw with probability {float(p0)}.")
print(f"To detect a {rel_bias:.0%} relative bias in ONE pre-specified number")
print(f"at alpha=0.05, power=80%:            ~{n_single:,.0f} draws")
print(f"Same, Bonferroni-corrected for 50 numbers:  ~{n_bonf:,.0f} draws")
print(f"\nEurojackpot has run since 2012-03-23 (weekly until 2022-03, twice weekly")
print(f"since). That is on the order of 1,000 draws to date - roughly an order of")
print(f"magnitude short of even the uncorrected requirement.")
print("A chi-square goodness-of-fit test on 50 categories (49 df) over ~1,000")
print("draws has an expected count of only ~100 per number and is therefore")
print("underpowered against any bias small enough to be physically plausible.")
print("\nNo frequency analysis is used to pick numbers in this report.")
print("Draws are independent: past frequencies carry zero information about the")
print("next draw, whatever a chi-square test happens to say.")


# --- 10. tier distribution ---------------------------------------------------
rule("10. TIER DISTRIBUTION")

RANK = {tier: i for i, (tier, _) in enumerate(TIPOS_OFFICIAL, start=1)}

print("Per ticket (identical for both tickets, and for every choice of numbers):\n")
print(f"{'#':>3} {'tier':>5} {'probability':>14} {'1 in':>14} {'per 1000 tickets':>18}")
for (k, j), _ in TIPOS_OFFICIAL:
    p = Fraction(tier_count(k, j), TOTAL_OUTCOMES)
    print(f"{RANK[(k, j)]:>3} {k}+{j:<3} {float(p) * 100:>13.7f}% "
          f"{1 / float(p):>14,.0f} {float(p) * 1000:>18.5f}")

# distribution of the BEST tier reached across the two tickets
joint = {}
from exact_model import joint_distribution
for (mA, eA, mB, eB), w in joint_distribution(0, 0).items():
    ranks = [RANK[t] for t in ((mA, eA), (mB, eB)) if t in PAYING]
    best_rank = min(ranks) if ranks else None
    joint[best_rank] = joint.get(best_rank, 0) + w

print("\nTwo tickets (disjoint mains + disjoint euro pairs) - BEST tier reached:\n")
print(f"{'#':>3} {'tier':>5} {'probability':>14} {'1 in':>14}")
inv = {v: k for k, v in RANK.items()}
for r in sorted(x for x in joint if x is not None):
    p = Fraction(joint[r], TOTAL_OUTCOMES)
    k, j = inv[r]
    print(f"{r:>3} {k}+{j:<3} {float(p) * 100:>13.7f}% {1 / float(p):>14,.0f}")
p_none = Fraction(joint[None], TOTAL_OUTCOMES)
print(f"{'-':>3} {'none':>5} {float(p_none) * 100:>13.7f}%")

assert sum(joint.values()) == TOTAL_OUTCOMES
print(f"\ncheck: 1 - P(no prize) = {float(1 - p_none) * 100:.6f}%  "
      f"(matches P(any prize, 2 tickets))")
print(f"expected NUMBER of prizes across the two tickets = "
      f"{float(2 * p1) * 100:.6f}% = {float(2 * p1):.5f} prizes")
