"""
TIPOS Loto 5 z 35 - exact analysis, same method as the Eurojackpot work.

Parameters verified on tipos.sk:
  - 5 numbers from 1..35
  - draws Wednesday, Friday and Sunday at 18:00
  - stake EUR 0.60 per tip
  - prize fund = 52% of stakes
  - minimum guaranteed jackpot EUR 20,000
  - official odds (page "Pravdepodobnosti"): 1. poradie 1:324 632,
    2. poradie 1:2 164, 3. poradie 1:75

Everything below is exact integer / Fraction arithmetic over the full
C(35,5) = 324,632 outcome space. No simulation.
"""

from fractions import Fraction
from itertools import combinations
from math import comb

POOL, PICK = 35, 5
TOTAL = comb(POOL, PICK)
STAKE = 0.60
PRIZE_FUND_SHARE = 0.52          # official, tipos.sk

# official TIPOS odds table: tier -> published "1 : N"
TIPOS_OFFICIAL = [(5, 324_632), (4, 2_164), (3, 75)]
PAYING = {5, 4, 3}

# Most recent completed draw, from the TIPOS Loto 5 z 35 page:
#   vklad EUR 103,663.20   na vyhry EUR 112,041.71
LAST_DRAW = {5: (42_620.25, 2), 4: (220.40, 89), 3: (3.60, 1_996)}
LAST_STAKES = 103_663.20

JACKPOT = 20_000                 # current, tipos.sk (= the guaranteed minimum)

rule = lambda t: print("\n" + "=" * 74 + f"\n{t}\n" + "=" * 74)


def tier_count(k):
    return comb(PICK, k) * comb(POOL - PICK, PICK - k)


# --- 1. validate against the official table ----------------------------------
rule("1. TIER PROBABILITIES vs OFFICIAL TIPOS TABLE")

print(f"C(35,5) = {TOTAL:,}\n")
print(f"{'poradie':>8} {'match':>6} {'outcomes':>9} {'exact 1:N':>13} "
      f"{'TIPOS 1:N':>10}  ok")
ok_all = True
for i, (k, official) in enumerate(TIPOS_OFFICIAL, start=1):
    c = tier_count(k)
    odds = TOTAL / c
    ok = round(odds) == official or int(odds) == official
    ok_all &= ok
    print(f"{i:>8}. {k:>6} {c:>9,} {odds:>13,.2f} {official:>10,}  "
          f"{'OK' if ok else 'MISMATCH'}")
if not ok_all:
    raise SystemExit("MODEL INVALID - a tier disagrees with the official table.")
print("\nAll three tiers reproduce the official odds -> model validated.")
assert sum(tier_count(k) for k in range(6)) == TOTAL


# --- 2. the structural difference from Eurojackpot ---------------------------
rule("2. KEY STRUCTURAL FACT: DISJOINT TICKETS CANNOT BOTH WIN")

print("The lowest paying tier is 3 matches. Two tickets sharing no numbers")
print("would need 3 + 3 = 6 matches between them, but only 5 numbers are drawn.")
print("So with disjoint tickets the winning events are MUTUALLY EXCLUSIVE and")
print("probabilities add EXACTLY - no inclusion-exclusion correction at all.")
print("\nThis is the opposite of Eurojackpot, where the 2+1 and 1+2 tiers let two")
print("disjoint tickets both win, so there P(A or B) < P(A) + P(B) strictly.")


# --- 3. exact probabilities ---------------------------------------------------
rule("3. EXACT PROBABILITIES")

p_one = Fraction(sum(tier_count(k) for k in PAYING), TOTAL)
print(f"one ticket, any prize    : {p_one} = {float(p_one) * 100:.5f}%  "
      f"(1 in {1 / float(p_one):.2f})")
for n in (2, 3, 4):
    p = n * p_one
    print(f"{n} disjoint tickets        : {p} = {float(p) * 100:.5f}%  "
          f"(1 in {1 / float(p):.2f})")

print(f"\nper tier, one ticket:")
for k, _ in TIPOS_OFFICIAL:
    p = Fraction(tier_count(k), TOTAL)
    print(f"  {k} matches: {float(p) * 100:9.6f}%   1 in {1 / float(p):>10,.2f}")

max_disjoint = POOL // PICK
print(f"\nMost disjoint tickets possible: {max_disjoint} "
      f"({max_disjoint * PICK} of {POOL} numbers)")
print(f"  P(any prize) with {max_disjoint} disjoint tickets = "
      f"{float(max_disjoint * p_one) * 100:.5f}%")


# --- 4. brute-force verification ----------------------------------------------
rule("4. INDEPENDENT VERIFICATION - FULL ENUMERATION OF ALL 324,632 DRAWS")

TICKETS = [
    ("Ticket 1", {3, 17, 26, 32, 35}),
    ("Ticket 2", {8, 13, 22, 33, 34}),
    ("Ticket 3", {6, 11, 19, 28, 31}),
]

win = both = 0
per_tier = {}
for draw in combinations(range(1, POOL + 1), PICK):
    d = set(draw)
    hits = [len(d & t[1]) for t in TICKETS]
    paying = [h for h in hits if h in PAYING]
    if paying:
        win += 1
        per_tier[max(paying)] = per_tier.get(max(paying), 0) + 1
    if len(paying) > 1:
        both += 1

p_brute = Fraction(win, TOTAL)
print(f"draws enumerated        : {TOTAL:,}")
print(f"at least one ticket wins: {win:,}  = {float(p_brute) * 100:.5f}%")
print(f"more than one ticket wins: {both}  <- must be 0, see section 2")
print(f"closed form (3 x p_one) : {3 * p_one} = {float(3 * p_one) * 100:.5f}%")
print(f"match: {p_brute == 3 * p_one}")
assert both == 0 and p_brute == 3 * p_one


# --- 5. RTP -------------------------------------------------------------------
rule("5. RTP")

tips_last = LAST_STAKES / STAKE
print(f"Most recent completed draw (from tipos.sk):")
print(f"  stakes EUR {LAST_STAKES:,.2f}  ->  {tips_last:,.0f} tips")
print(f"{'match':>6} {'prize EUR':>12} {'winners':>9} {'expected':>10} {'EV':>10}")
ev_last = 0.0
for k, _ in TIPOS_OFFICIAL:
    prize, w = LAST_DRAW[k]
    exp_w = tips_last * tier_count(k) / TOTAL
    ev = prize * tier_count(k) / TOTAL
    ev_last += ev
    print(f"{k:>6} {prize:>12,.2f} {w:>9,} {exp_w:>10.1f} {ev:>10.6f}")

print(f"\nThat draw's EV per EUR {STAKE:.2f} ticket : EUR {ev_last:.6f}  "
      f"(RTP {ev_last / STAKE * 100:.1f}%)")
print(f"  - but its jackpot had rolled to EUR {LAST_DRAW[5][0]:,.2f}")

ev_jack_now = JACKPOT / TOTAL
ev_lower = sum(LAST_DRAW[k][0] * tier_count(k) / TOTAL for k in (4, 3))
ev_now = ev_jack_now + ev_lower
print(f"\nTonight's jackpot is EUR {JACKPOT:,} - the guaranteed MINIMUM:")
print(f"  EV from tier 1 (5 matches) : EUR {ev_jack_now:.6f}   [exact given J]")
print(f"  EV from tiers 2-3          : EUR {ev_lower:.6f}   [last draw's levels]")
print(f"  EV total                   : EUR {ev_now:.6f}")
print(f"  RTP                        : {ev_now / STAKE * 100:.1f}%")
print(f"\nOfficial long-run design RTP is {PRIZE_FUND_SHARE * 100:.0f}% "
      f"(prize fund = 52% of stakes).")
print(f"At the reset minimum jackpot the draw returns well under that, exactly")
print(f"as with Eurojackpot: the shortfall accumulates into future rollovers.")
print(f"A minimum jackpot is the WORST moment to buy, on RTP grounds.")

print(f"\nThree tickets, EUR {3 * STAKE:.2f}:")
print(f"  expected return EUR {3 * ev_now:.3f}   expected loss EUR "
      f"{3 * STAKE - 3 * ev_now:.3f}")

be = (STAKE - ev_lower) * TOTAL
print(f"\nJackpot needed for RTP = 100%: EUR {be:,.0f}")
print(f"  (the jackpot has no published cap, so unlike Eurojackpot this one is")
print(f"   not structurally unreachable - but it is far above normal levels)")


# --- 6. tickets ---------------------------------------------------------------
rule("6. THREE TICKETS")

allnum = set().union(*(t[1] for t in TICKETS))
for name, m in TICKETS:
    odd = sum(1 for n in m if n % 2)
    gaps = [b - a for a, b in zip(sorted(m), sorted(m)[1:])]
    print(f"{name}: {sorted(m)}   parity {odd} odd / {PICK - odd} even   gaps {gaps}")

checks = {
    "15 distinct numbers - the optimal disjoint layout": len(allnum) == 15,
    "overall parity 8 odd / 7 even": sum(1 for n in allnum if n % 2) == 8,
    "no uniform gap in any ticket": all(
        len({b - a for a, b in zip(sorted(m), sorted(m)[1:])}) > 1
        for _, m in TICKETS),
    "uses all four numbers above 31 (32,33,34,35)": {32, 33, 34, 35} <= allnum,
}
print()
for label, v in checks.items():
    print(f"  [{'x' if v else ' '}] {label}")
assert all(checks.values())

print("\nNOTE ON THE UNPOPULARITY TIE-BREAK: it is much weaker here than in")
print("Eurojackpot. Only 4 of the 35 numbers (32-35) fall outside the day-of-month")
print("range, against 19 of 50 there. So 'avoid birthday numbers' can move very")
print("little in this game - all four are used and the rest is parity balance and")
print("absence of visible pattern. As always this changes the SHARE of a")
print("pari-mutuel tier, never the probability of winning.")

rule("7. WHERE A WIN WOULD LAND (best tier, three tickets)")
print(f"{'match':>6} {'probability':>13} {'1 in':>10} {'prize EUR (last draw)':>22}")
for k in sorted(per_tier, reverse=True):
    p = Fraction(per_tier[k], TOTAL)
    print(f"{k:>6} {float(p) * 100:>12.6f}% {1 / float(p):>10,.0f} "
          f"{LAST_DRAW[k][0]:>22,.2f}")
print(f"{'none':>6} {float(1 - p_brute) * 100:>12.6f}%")
print(f"\n{float(1 - p_brute) * 100:.2f}% of the time three tickets return nothing.")
print(f"A 3-match win pays about EUR {LAST_DRAW[3][0]:.2f} against EUR "
      f"{3 * STAKE:.2f} staked for three tickets, i.e. "
      f"EUR {LAST_DRAW[3][0] - 3 * STAKE:+.2f} net - it does cover the outlay,")
print(f"the same shape as Eurojackpot's bottom tier. But it is the outcome in")
print(f"{float(Fraction(per_tier[3], TOTAL)) / float(p_brute) * 100:.1f}% of all "
      f"wins, so the realistic upside of a EUR {3 * STAKE:.2f} purchase is")
print(f"about EUR {LAST_DRAW[3][0] - 3 * STAKE:.2f}, not the jackpot.")
