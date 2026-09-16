"""
The JOKER supplementary game: every possible way to "know" the draw, examined.

Verified on tipos.sk and the TIPOS rules:
  - JOKER is a bet on a six-digit number PRINTED ON THE TICKET, created by a
    random number generator: "Hra JOKER je stavka na sescislie uvedene na
    potvrdeni o uzatvoreni stavky, ktore vytvori generator nahodnych cisel."
  - The draw: six drums, ten balls each (1-10), one ball from each drum.
  - Matching is POSITIONAL and counted FROM THE END of the number.
  - Stake for the Loto 5 z 35 JOKER: EUR 0.60 (tipos.sk). A secondary source
    says EUR 0.50 for the Loto JOKER - both are priced below, because this one
    number decides the whole answer.
  - Prize tiers (Loto JOKER): 1st jackpot (min EUR 6,600), 2nd EUR 3,300,
    3rd EUR 330, 4th EUR 33, 5th EUR 3.30, 6th no prize.

Jackpots as printed on tipos.sk right now:
  Loto 5 z 35 : EUR 37,576.65      JOKER : EUR 432,626.40
"""

from fractions import Fraction
from itertools import product

DIGITS, BASE = 6, 10
TOTAL = BASE ** DIGITS
JACKPOT = 432_626.40
STAKE_OFFICIAL = 0.60
STAKE_ALT = 0.50
LOWER = {5: 3_300.00, 4: 330.00, 3: 33.00, 2: 3.30}   # matched-from-end -> prize
MIN_JACKPOT = 6_600.00

rule = lambda t: print("\n" + "=" * 76 + f"\n{t}\n" + "=" * 76)


# --- 0. the fact that settles the question -----------------------------------
rule("0. THE STRUCTURAL FACT THAT ENDS THE PREDICTION QUESTION")

print("You do not choose your JOKER number. A random number generator assigns")
print("it and prints it on the betting slip. There is no field to fill in.")
print("\nSo even a PERFECT prediction of tonight's six digits would be unusable:")
print("knowing the answer does not let you write it on a ticket. The only")
print("choice you have is whether to tick the JOKER box at all.")
print("\nThat turns the whole question into a single yes/no decision with an")
print("exactly computable expected value - which is what the rest of this does.")


# --- 1. exact probabilities, verified by full enumeration --------------------
rule("1. EXACT PROBABILITIES (brute-forced over all 1,000,000 draws)")

TICKET = (4, 7, 1, 9, 0, 3)      # any fixed number; by symmetry all are equal


def matched_from_end(a, b):
    """How many trailing digits agree."""
    n = 0
    while n < DIGITS and a[DIGITS - 1 - n] == b[DIGITS - 1 - n]:
        n += 1
    return n


counts = {k: 0 for k in range(DIGITS + 1)}
for draw in product(range(BASE), repeat=DIGITS):
    counts[matched_from_end(TICKET, draw)] += 1
assert sum(counts.values()) == TOTAL

print(f"{'matched from end':>17} {'outcomes':>10} {'probability':>14} {'1 in':>12}")
for k in range(DIGITS, 0, -1):
    p = Fraction(counts[k], TOTAL)
    print(f"{k:>17} {counts[k]:>10,} {float(p) * 100:>13.5f}% "
          f"{1 / float(p):>12,.1f}")
print(f"{'0 (nothing)':>17} {counts[0]:>10,} "
      f"{counts[0] / TOTAL * 100:>13.5f}%")

paying = sum(counts[k] for k in range(2, DIGITS + 1))
p_any = Fraction(paying, TOTAL)
print(f"\n  P(any JOKER prize) = {paying:,}/{TOTAL:,} = {p_any} = "
      f"{float(p_any) * 100:.4f}%  (exactly 1 in {1 / float(p_any):.0f})")
print("  Closed form check: sum over k>=2 of 9/10^k, plus 1/10^6, = 1/100 exactly.")
assert p_any == Fraction(1, 100)


# --- 2. expected value --------------------------------------------------------
rule("2. EXPECTED VALUE - THE PART THAT IS GENUINELY CALCULABLE")

ev_lower = sum(prize * counts[k] / TOTAL for k, prize in LOWER.items())
ev_jack = JACKPOT / TOTAL
ev = ev_jack + ev_lower

print(f"{'tier':>6} {'prize EUR':>12} {'probability':>14} {'EV contribution':>17}")
print(f"{6:>6} {JACKPOT:>12,.2f} {counts[6] / TOTAL * 100:>13.5f}% {ev_jack:>17.6f}")
for k in (5, 4, 3, 2):
    c = LOWER[k] * counts[k] / TOTAL
    print(f"{k:>6} {LOWER[k]:>12,.2f} {counts[k] / TOTAL * 100:>13.5f}% {c:>17.6f}")
print(f"\n  EV from the four lower tiers : EUR {ev_lower:.6f}")
print("  Note they contribute EUR 0.0297 EACH - the prize falls 10x per tier")
print("  while the probability rises 10x, so the structure is exactly balanced.")
print(f"\n  EV from the jackpot          : EUR {ev_jack:.6f}")
print(f"  TOTAL EV per ticket          : EUR {ev:.6f}")

print(f"\n{'stake':>10} {'RTP':>9} {'edge':>10}")
for label, st in (("EUR 0.60", STAKE_OFFICIAL), ("EUR 0.50", STAKE_ALT)):
    print(f"{label:>10} {ev / st * 100:>8.2f}% {(ev / st - 1) * 100:>+9.2f}%")
print("\n  tipos.sk states EUR 0.60 for the Loto 5 z 35 JOKER; a secondary")
print("  source says EUR 0.50 for the Loto JOKER. At EUR 0.50 this bet is")
print("  ALREADY EV-POSITIVE. That single number decides it, so verify the")
print("  price on your own slip before drawing any conclusion from this.")


# --- 3. the break-even jackpot ------------------------------------------------
rule("3. WHEN JOKER BECOMES EV-POSITIVE - A REAL, DATED ANSWER")

for label, st in (("EUR 0.60", STAKE_OFFICIAL), ("EUR 0.50", STAKE_ALT)):
    be = (st - ev_lower) * TOTAL
    gap = be - JACKPOT
    print(f"  at a {label} stake: break-even jackpot = EUR {be:,.0f}")
    if gap > 0:
        print(f"      current EUR {JACKPOT:,.2f} is EUR {gap:,.0f} short")
    else:
        print(f"      current EUR {JACKPOT:,.2f} is ALREADY EUR {-gap:,.0f} past it")

GROWTH = 432_626.40 - 413_142.00        # observed over one draw, 11.09 -> 16.09
be60 = (STAKE_OFFICIAL - ev_lower) * TOTAL
print(f"\n  Observed jackpot growth: EUR {413_142.00:,.0f} -> EUR {JACKPOT:,.2f}")
print(f"  over one intervening draw = about EUR {GROWTH:,.0f} per draw.")
print(f"  At that rate the EUR 0.60 break-even of EUR {be60:,.0f} arrives in")
print(f"  about {(be60 - JACKPOT) / GROWTH:.1f} more draws - roughly a week, IF nobody wins it first.")
print("\n  This is the one genuinely actionable number in the whole exercise,")
print("  and it has nothing to do with predicting digits.")


# --- 4. every way to "know" the draw, enumerated -----------------------------
rule("4. EVERY POSSIBLE WAY TO KNOW THE DRAW - EXHAUSTIVELY")

ways = [
    ("A1", "Frequency analysis of past JOKER digits, per drum",
     "TESTABLE",
     "Six independent drums, ten balls each. A biased drum WOULD show up as a "
     "skewed digit distribution. But see the killer below: you cannot choose "
     "your number, so a detected bias is unusable."),
    ("A2", "Serial correlation between consecutive JOKER draws",
     "TESTABLE",
     "Same verdict as A1 - and the same killer applies."),
    ("A3", "Cross-game correlation (Loto JOKER vs Eurojackpot JOKER)",
     "TESTABLE",
     "Separate draws on separate devices. Same killer."),
    ("B1", "Physical modelling of the drum dynamics",
     "THE ONLY METHOD THAT HAS EVER WORKED ANYWHERE",
     "Roulette was beaten this way (Eudaemons, 1970s) by measuring initial "
     "conditions in real time. It needs physical access, millisecond timing "
     "and knowledge of the machine. The draw is sealed, off-site and under "
     "notarial supervision. Not available, and still hits the killer."),
    ("B2", "Ball-wear bias accumulating over years",
     "REAL PHENOMENON, REDUCES TO A1",
     "Documented in some lotteries. Detectable only as a frequency skew, so "
     "it collapses into test A1 - and into the same killer."),
    ("C1", "Recovering the PRNG state of the DRAW",
     "DOES NOT APPLY",
     "The draw is mechanical - six drums of ten balls. There is no PRNG to "
     "attack on the draw side."),
    ("C2", "Recovering the PRNG that assigns YOUR ticket number",
     "WRONG TARGET",
     "This RNG exists and is real. But predicting what number YOU will be "
     "given tells you nothing about what will be DRAWN. It would only let you "
     "re-roll until you got a number you liked - which is just buying tickets, "
     "priced in section 5."),
    ("D1", "Brute-force coverage: buy enough tickets to guarantee a hit",
     "MATHEMATICALLY VALID, PRICED IN SECTION 5",
     "The one approach that genuinely raises your chance of holding the "
     "winning number. It does not improve RTP by a cent."),
    ("E1", "Insider access to the draw",
     "OUT OF SCOPE",
     "Illegal. Not something I will help with."),
    ("E2", "Buying after the numbers are known",
     "IMPOSSIBLE",
     "Sales close before the draw."),
]
for code, name, verdict, note in ways:
    print(f"\n  [{code}] {name}")
    print(f"       verdict: {verdict}")
    for line in (note[i:i + 66] for i in range(0, len(note), 66)):
        print(f"       {line}")

print("\n" + "-" * 76)
print("THE KILLER, which applies to A1, A2, A3, B1 and B2 alike:")
print("even a method that predicted the six digits with certainty would be")
print("worthless, because the ticket's number is assigned by the operator's")
print("RNG. Prediction without the ability to act on it is not an edge.")
print("-" * 76)


# --- 5. brute-force coverage, priced ------------------------------------------
rule("5. BRUTE FORCE: WHAT BUYING N TICKETS ACTUALLY BUYS")

print("Because the number is assigned at random, N tickets are N INDEPENDENT")
print("samples WITH replacement - duplicates are possible and you cannot")
print("arrange coverage. This is the crucial difference from the main game,")
print("where choosing distinct number sets does buy real coverage.\n")
print(f"{'tickets':>10} {'cost EUR':>12} {'P(hit jackpot)':>16} {'EV back EUR':>13}")
for n in (1, 100, 10_000, 100_000, 693_147, 1_000_000):
    cost = n * STAKE_OFFICIAL
    p_hit = 1 - (1 - 1 / TOTAL) ** n
    print(f"{n:>10,} {cost:>12,.2f} {p_hit * 100:>15.4f}% {n * ev:>13,.2f}")

n50 = 693_147
print(f"\n  To reach a 50% chance of holding the winning number you need")
print(f"  {n50:,} tickets costing EUR {n50 * STAKE_OFFICIAL:,.0f} - to chase a")
print(f"  EUR {JACKPOT:,.0f} jackpot. And buying 1,000,000 tickets does NOT")
print(f"  guarantee a hit: P = {(1 - (1 - 1 / TOTAL) ** TOTAL) * 100:.2f}%, not 100%,")
print("  precisely because the numbers are drawn with replacement.")
print(f"\n  The return is linear at {ev / STAKE_OFFICIAL * 100:.2f}% of whatever you stake.")
print("  Coverage changes the SHAPE of the outcome, never the average.")


# --- 6. the package -----------------------------------------------------------
rule("6. TONIGHT'S PACKAGE: LOTO 5 z 35 + JOKER")

LOTO_JACKPOT = 37_576.65
LOTO_STAKE = 0.60
L_TOTAL = 324_632
l_counts = {5: 1, 4: 150, 3: 4_350}
LAST = {4: 220.40, 3: 3.60}          # observed levels from the last draw table
ev_loto = LOTO_JACKPOT / L_TOTAL + sum(LAST[k] * l_counts[k] / L_TOTAL
                                       for k in (4, 3))
print(f"  Loto 5 z 35 : jackpot EUR {LOTO_JACKPOT:,.2f}, EV EUR {ev_loto:.4f} "
      f"per EUR {LOTO_STAKE:.2f}  -> RTP {ev_loto / LOTO_STAKE * 100:.1f}%")
print(f"  JOKER       : jackpot EUR {JACKPOT:,.2f}, EV EUR {ev:.4f} "
      f"per EUR {STAKE_OFFICIAL:.2f}  -> RTP {ev / STAKE_OFFICIAL * 100:.1f}%")
both_ev = ev_loto + ev
both_st = LOTO_STAKE + STAKE_OFFICIAL
print(f"  both        : EV EUR {both_ev:.4f} per EUR {both_st:.2f}  "
      f"-> RTP {both_ev / both_st * 100:.1f}%")
print(f"\n  JOKER at its current rolled jackpot has the HIGHEST RTP of anything")
print(f"  analysed in this whole project - {ev / STAKE_OFFICIAL * 100:.1f}% against 46.7% for")
print(f"  Eurojackpot at EUR 48m. Not because anyone predicted anything, but")
print(f"  because a EUR 432,626 jackpot sits on a 1-in-1,000,000 event priced")
print(f"  at EUR 0.60. That is the whole edge, and it is arithmetic.")
