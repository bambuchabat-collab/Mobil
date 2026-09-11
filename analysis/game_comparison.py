"""
Which TIPOS game loses money slowest?

The question "which one do I play so as not to go into minus" has no solution:
every game here has RTP well below 100%, so the expected result is negative in
all of them. What CAN be answered is how fast each one takes money, which is
RTP and stake and draw frequency together - and the frequency term turns out to
dominate everything else.

Sources for each RTP are marked. Only Loto 5 z 35 is confirmed on tipos.sk
itself; the rest are secondary or design figures and are labelled as such.
"""

RULE = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

# name, stake EUR, draws per week, RTP, source quality, note
GAMES = [
    ("Loto 5 z 35", 0.60, 3, 0.52, "OFFICIAL tipos.sk",
     "5 from 35; Wed/Fri/Sun"),
    ("Loto (6 z 49)", 1.20, 2, 0.50, "assumed, not verified",
     "Wed/Sun; stake from the game plan"),
    ("Eurojackpot", 2.00, 2, 0.50, "design figure, secondary",
     "Tue/Fri"),
    ("Euromiliony", 1.50, 2, 0.50, "secondary: 'fund is half the stake'",
     "stake not verified"),
    ("Keno 10", 0.50, 7, 0.40, "secondary estimate, variable",
     "daily; stake 0.50-10 EUR, KENO PLUS doubles it"),
    ("Vsetko alebo nic", 1.00, 7, None, "NOT VERIFIED",
     "11 of 22; win on ALL or NONE matched"),
    ("Extra vyplata", 1.00, 1, None, "NOT VERIFIED", "Mondays"),
]

RULE("1. THE HONEST ANSWER FIRST")
print("Expected result = stake x (RTP - 1). RTP < 1 in every one of these, so")
print("the expectation is NEGATIVE in all of them, always. No game on this")
print("screen avoids the minus. Choosing between them only changes HOW FAST.")
print("\nThe only stake with a non-negative expectation is zero. That is not a")
print("moral point, it is the arithmetic.")

RULE("2. RANKED BY RTP - HOW MUCH OF EACH EURO COMES BACK")
print(f"{'game':<20} {'stake':>7} {'RTP':>7} {'house keeps':>12}  source")
for name, stake, _, rtp, src, _ in sorted(
        GAMES, key=lambda g: -(g[3] or 0)):
    if rtp is None:
        print(f"{name:<20} {stake:>7.2f} {'?':>7} {'?':>12}  {src}")
    else:
        print(f"{name:<20} {stake:>7.2f} {rtp * 100:>6.0f}% "
              f"{(1 - rtp) * 100:>11.0f}%  {src}")

print("\nBest verified RTP: Loto 5 z 35 at 52%, and it also has the smallest")
print("stake (EUR 0.60). Worst of the measurable ones: Keno 10 at roughly 40%.")

RULE("3. BUT RTP IS NOT THE DECIDING NUMBER - FREQUENCY IS")
print(f"{'game':<20} {'stake':>7} {'draws/wk':>9} {'staked/wk':>10} "
      f"{'expected loss/wk':>17}")
rows = []
for name, stake, per_week, rtp, _, _ in GAMES:
    if rtp is None:
        continue
    staked = stake * per_week
    loss = staked * (1 - rtp)
    rows.append((loss, name, stake, per_week, staked))
for loss, name, stake, per_week, staked in sorted(rows):
    print(f"{name:<20} {stake:>7.2f} {per_week:>9} {staked:>10.2f} "
          f"{loss:>17.2f}")

RULE("4. THE ONE TO AVOID OUTRIGHT: eKLUB KENO")
print("eKlub Keno draws EVERY 2 MINUTES. That is 30 draws an hour.")
print("Even at a generous 60% RTP, at the minimum stake:\n")
for hours in (0.5, 1, 2, 3):
    draws = 30 * hours
    for stake in (0.50, 1.00):
        loss_hr = draws * stake * 0.40
        print(f"  {hours:>4.1f} h/day at EUR {stake:.2f}/draw -> "
              f"EUR {loss_hr:6.2f}/day = EUR {loss_hr * 7:7.2f}/week = "
              f"EUR {loss_hr * 365:8.0f}/year")
print("\nOne hour a day at EUR 0.50 costs about EUR 84 a week - roughly")
print("100x what Loto 5 z 35 costs at three draws a week. Same arithmetic,")
print("different clock speed. A game that never makes you wait is the")
print("expensive one, whatever its RTP says.")

RULE("5. THE JACKPOT-SIZE EFFECT - WHEN, NOT WHICH")
print("Within a single game the realised RTP swings hard with the jackpot,")
print("because a reset jackpot is underfunded relative to its share:\n")
print(f"{'game / moment':<34} {'jackpot':>14} {'RTP':>8}")
print(f"{'Eurojackpot, reset minimum':<34} {'EUR 10m':>14} {'27%':>8}")
print(f"{'Eurojackpot, after rollovers':<34} {'EUR 40m':>14} {'41%':>8}")
print(f"{'Loto 5 z 35, reset minimum':<34} {'EUR 20k':>14} {'35%':>8}")
print(f"{'Loto 5 z 35, after rollovers':<34} {'EUR 43k':>14} {'47%':>8}")
print("\nSo WHEN you buy moves the number by 14-20 points, more than the gap")
print("between most of these games. A minimum jackpot is the worst moment in")
print("every one of them. Right now Loto 5 z 35 sits at its EUR 20,000 floor,")
print("so it is currently at its own worst point despite the best headline RTP.")

RULE("6. IF THE GOAL IS 'STOP GOING INTO MINUS'")
print("It cannot be met by picking a game. The levers that actually move your")
print("result, in order of size:\n")
print("  1. How often you play      - dominates everything (see section 4)")
print("  2. How much per draw       - linear, and fully under your control")
print("  3. Which game              - 52% vs 40% RTP, a 12-point difference")
print("  4. When (jackpot level)    - 14-20 points inside one game")
print("  5. Which numbers           - ZERO effect, proven on 476 real draws")
print("\nYour own record so far, from settle.py: EUR 24.00 staked across five")
print("draws, about EUR 16.80 back, net about -EUR 7.20. That is a realised")
print("return near 70%, which is ABOVE the ~40% these games pay on average -")
print("you have been running lucky, not unlucky. Expect the gap to widen.")

RULE("7. VERDICT")
print("If you are going to play something on this screen:")
print("\n  Loto 5 z 35 - best verified RTP (52%), smallest stake (EUR 0.60),")
print("  three draws a week. At one ticket per draw that is EUR 1.80 staked")
print("  and about EUR 0.86 expected loss per week. It is the cheapest way to")
print("  stay in the game, and its jackpot is at the floor right now, so it is")
print("  also at its own weakest moment - worth waiting for a rollover.")
print("\n  Avoid eKlub Keno entirely. Not because of its RTP, which I could not")
print("  verify, but because a draw every two minutes turns any RTP into a")
print("  large weekly number.")
print("\n  And the honest bottom line: none of these stops the minus. Over any")
print("  length of time the house keeps 48-60 cents of every euro. The only")
print("  way to not lose is to not stake - everything else is choosing a rate.")
