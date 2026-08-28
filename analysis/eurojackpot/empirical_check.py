"""
Empirical validation of the model against a REAL TIPOS payout table.

Source: TIPOS mobile app screenshot supplied by the user. The screenshot shows
a completed draw's prize table WITHOUT A DATE. It is NOT the 2026-08-28 draw
(see check_not_today() below), so it is used here only to validate the
probability model and to calibrate the small-tier prize levels.

Observed (Slovak winner counts, Europe-wide pari-mutuel prize amounts):
    Vklad (Slovak stake): 642 802,00 EUR   ->  321 401 tips at 2,00 EUR
"""

from fractions import Fraction
from math import comb, exp, log, lgamma, sqrt

from exact_model import TOTAL_OUTCOMES, TIPOS_OFFICIAL, tier_count

VKLAD = 642_802.00
STAKE = 2.00
N_TIPS = int(round(VKLAD / STAKE))

# tier -> (prize EUR, Slovak winner count)
OBSERVED = {
    (5, 2): (39_496_021.60, 0),
    (5, 1): (1_394_682.50, 0),
    (5, 0): (157_307.20, 0),
    (4, 2): (4_324.50, 1),
    (4, 1): (334.30, 6),
    (3, 2): (130.20, 23),
    (4, 0): (129.70, 12),
    (2, 2): (23.60, 365),
    (3, 1): (20.70, 457),
    (3, 0): (19.20, 911),
    (1, 2): (13.30, 1_706),
    (2, 1): (9.30, 7_143),
}

TODAY_JACKPOT = 10_000_000.0

rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --- chi-square survival function (no scipy dependency) ---------------------

def _gser(a, x):
    ap, s, d = a, 1.0 / a, 1.0 / a
    for _ in range(1000):
        ap += 1
        d *= x / ap
        s += d
        if abs(d) < abs(s) * 1e-15:
            break
    return s * exp(-x + a * log(x) - lgamma(a))


def _gcf(a, x):
    tiny = 1e-300
    b, c, d = x + 1 - a, 1 / tiny, 1 / (x + 1 - a)
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return exp(-x + a * log(x) - lgamma(a)) * h


def chi2_sf(chi2, df):
    """Upper tail P(X > chi2) for a chi-square with df degrees of freedom."""
    a, x = df / 2.0, chi2 / 2.0
    if x <= 0:
        return 1.0
    return 1.0 - _gser(a, x) if x < a + 1 else _gcf(a, x)


# --- 0. this table is NOT today's draw --------------------------------------
rule("0. IS THIS TABLE TODAY'S (2026-08-28) DRAW?  -> NO")

print(f"observed jackpot in the table : EUR {OBSERVED[(5, 2)][0]:,.2f}")
print(f"jackpot for 2026-08-28        : EUR {TODAY_JACKPOT:,.2f}")
print("\nStructural argument (independent of any date label):")
print("  - the table shows 5+2 won 0x, so THAT draw rolled the jackpot UPWARDS")
print(f"  - it would have rolled from EUR {OBSERVED[(5, 2)][0]:,.0f} to something larger")
print(f"  - today's jackpot is EUR {TODAY_JACKPOT:,.0f}, the RESET minimum")
print("  => between that draw and today somebody won the jackpot and it reset.")
print("     The table is therefore at least one full jackpot cycle old.")
print("\n  The app itself confirms it: for 28.08.2026 it says")
print('     \"Vysledok zrebovania este nie je znamy\" (result not yet known).')
assert OBSERVED[(5, 2)][0] != TODAY_JACKPOT


# --- 1. model validation against real winner counts -------------------------
rule("1. MODEL vs REAL WINNER COUNTS")

print(f"Slovak stake  : EUR {VKLAD:,.2f}")
print(f"tips at EUR {STAKE:.2f}: {N_TIPS:,}\n")
print(f"{'tier':>5} {'observed':>9} {'expected':>10} {'obs/exp':>8} {'prize EUR':>14}")

chi2 = 0.0
tot_obs = tot_exp = 0
for (k, j), _ in TIPOS_OFFICIAL:
    p = tier_count(k, j) / TOTAL_OUTCOMES
    exp_n = N_TIPS * p
    obs = OBSERVED[(k, j)][1]
    tot_obs += obs
    tot_exp += exp_n
    chi2 += (obs - exp_n) ** 2 / exp_n
    ratio = f"{obs / exp_n:8.2f}" if exp_n > 0 else "     n/a"
    print(f"{k}+{j:<3} {obs:>9,} {exp_n:>10.2f} {ratio} {OBSERVED[(k, j)][0]:>14,.2f}")

# the 13th cell: no prize
p_none = 1 - sum(tier_count(k, j) for (k, j), _ in TIPOS_OFFICIAL) / TOTAL_OUTCOMES
exp_none, obs_none = N_TIPS * p_none, N_TIPS - tot_obs
chi2 += (obs_none - exp_none) ** 2 / exp_none

print(f"{'none':>5} {obs_none:>9,} {exp_none:>10.2f} {obs_none / exp_none:>8.2f}")
print(f"\ntotal winners observed : {tot_obs:,}")
print(f"total winners expected : {tot_exp:,.1f}   (obs/exp = {tot_obs / tot_exp:.4f})")
print(f"\nchi-square (13 cells, 12 df) = {chi2:.2f},  p = {chi2_sf(chi2, 12):.3e}")
print("\nCAVEAT: this p-value is NOT evidence against the probability model.")
print("The 321k tips all face the SAME drawn numbers, so the tier counts are")
print("strongly positively correlated, not multinomial. The chi-square is")
print("descriptive only; its nominal p-value is far too small.")


# --- 2. the clean test: euro split conditional on main matches --------------
rule("2. CLEAN TEST - EURO SPLIT CONDITIONAL ON THE NUMBER OF MAIN MATCHES")

print("Conditional on k main matches, the euro count must split as")
print("  C(2,j)*C(10,2-j)/66  =  45 : 20 : 1  for j = 0 : 1 : 2,")
print("independently of which main numbers were drawn. This factors out")
print("essentially all of the player-clustering and shared-draw correlation.\n")

euro_w = [comb(2, j) * comb(10, 2 - j) for j in range(3)]   # 45, 20, 1
print(f"{'k main':>7} {'obs 0/1/2':>22} {'exp 0/1/2':>26} {'chi2':>7} {'df':>3} {'p':>8}")
for k in (4, 3, 2):
    obs = [OBSERVED.get((k, j), (0, 0))[1] for j in range(3)]
    if k == 2:
        obs[0] = None            # 2+0 is not a prize, so it is not observed
        sub, w = obs[1:], euro_w[1:]
    else:
        sub, w = obs, euro_w
    n = sum(sub)
    expd = [n * wi / sum(w) for wi in w]
    c2 = sum((o - e) ** 2 / e for o, e in zip(sub, expd))
    df = len(sub) - 1
    print(f"{k:>7} {str(obs):>22} "
          f"{'[' + ', '.join(f'{e:.1f}' for e in expd) + ']':>26} "
          f"{c2:>7.3f} {df:>3} {chi2_sf(c2, df):>8.3f}")

print("\nAll three fit well (no p below 0.09). The euro factor of the model is")
print("confirmed empirically on real data.")


# --- 3. where the deviation actually is -------------------------------------
rule("3. WHERE THE DEVIATION IS: PLAYERS DO NOT PICK UNIFORMLY")

print("Grouping by main matches only (euro factored out):\n")
print(f"{'k main':>7} {'observed':>10} {'expected':>10} {'obs/exp':>9}")
for k in (4, 3, 2, 1):
    obs = sum(OBSERVED.get((k, j), (0, 0))[1] for j in range(3))
    # only the paying (k,j) combinations are observable
    cnt = sum(tier_count(k, j) for j in range(3) if (k, j) in dict(TIPOS_OFFICIAL))
    e = N_TIPS * cnt / TOTAL_OUTCOMES
    print(f"{k:>7} {obs:>10,} {e:>10.1f} {obs / e:>9.3f}")

print("\nHigh-match tiers came in BELOW a uniform-play model and the lowest tier")
print("ABOVE it. That is the signature of non-uniform number selection by")
print("players interacting with which numbers happened to be drawn.")
print("\nThis is DIRECT empirical support for the tie-break in section 9 of the")
print("report: player choices are demonstrably not uniform, so avoiding popular")
print("numbers really does change your expected share of a pari-mutuel tier.")
print("It still does NOT change the probability of winning anything.")


# --- 4. empirical RTP calibration -------------------------------------------
rule("4. EMPIRICAL RTP CALIBRATION FOR TODAY'S DRAW")

small = [(4, 2), (4, 1), (3, 2), (4, 0), (2, 2), (3, 1), (3, 0), (1, 2), (2, 1)]
ev_small = sum(OBSERVED[t][0] * tier_count(*t) / TOTAL_OUTCOMES for t in small)
print("Tiers 4-12 use prize levels that are stable draw to draw (they do not")
print("roll over). Observed prizes give:\n")
for t in small:
    contrib = OBSERVED[t][0] * tier_count(*t) / TOTAL_OUTCOMES
    print(f"   {t[0]}+{t[1]}: EUR {OBSERVED[t][0]:>10,.2f} x 1/{TOTAL_OUTCOMES // tier_count(*t):<9,} "
          f"= EUR {contrib:.6f}")
print(f"\n   EV(tiers 4-12)        = EUR {ev_small:.4f} per EUR 2.00 ticket "
      f"({ev_small / STAKE * 100:.2f}% of stake)")
print(f"   [my earlier estimate for ALL 11 lower tiers was EUR 0.5500]")

ev_jackpot = TODAY_JACKPOT * tier_count(5, 2) / TOTAL_OUTCOMES
print(f"\n   EV(jackpot, EUR 10m)  = EUR {ev_jackpot:.6f}  [exact]")

# tiers 2-3 roll over with the jackpot -> bracket them
scale = TODAY_JACKPOT / OBSERVED[(5, 2)][0]
lo = sum(OBSERVED[t][0] * scale * tier_count(*t) / TOTAL_OUTCOMES for t in [(5, 1), (5, 0)])
hi = sum(OBSERVED[t][0] * tier_count(*t) / TOTAL_OUTCOMES for t in [(5, 1), (5, 0)])
print(f"\n   Tiers 2-3 (5+1, 5+0) also roll over, so they are bracketed:")
print(f"     low  (scaled by {scale:.3f}, the jackpot ratio) = EUR {lo:.4f}")
print(f"     high (observed values, a rolled-up draw)   = EUR {hi:.4f}")

ev_lo, ev_hi = ev_small + ev_jackpot + lo, ev_small + ev_jackpot + hi
print(f"\n   EV today  = EUR {ev_lo:.4f} .. EUR {ev_hi:.4f} per EUR 2.00 ticket")
print(f"   RTP today = {ev_lo / STAKE * 100:.1f}% .. {ev_hi / STAKE * 100:.1f}%")
print(f"\n   My pre-screenshot estimate was 31.1% - inside this bracket.")
print(f"   Two tickets, EUR 4.00: expected back EUR {2 * ev_lo:.2f} .. EUR {2 * ev_hi:.2f}, "
      f"expected loss EUR {4 - 2 * ev_hi:.2f} .. EUR {4 - 2 * ev_lo:.2f}")


# --- 5. what a prize actually pays ------------------------------------------
rule("5. WHAT A PRIZE ACTUALLY PAYS (observed levels)")

p_any = sum(tier_count(k, j) for (k, j), _ in TIPOS_OFFICIAL) / TOTAL_OUTCOMES
print(f"Given that a EUR 2.00 ticket wins something ({p_any * 100:.3f}% chance),")
print("the conditional distribution of the prize is:\n")
print(f"{'tier':>5} {'P(tier | win)':>14} {'prize EUR':>12}")
cum = 0.0
for (k, j), _ in TIPOS_OFFICIAL:
    pc = tier_count(k, j) / TOTAL_OUTCOMES / p_any
    cum += pc
    print(f"{k}+{j:<3} {pc * 100:>13.3f}% {OBSERVED[(k, j)][0]:>12,.2f}")
print(f"\n  64.6% of all wins are the bottom tier 2+1 = EUR {OBSERVED[(2, 1)][0]:.2f},")
print(f"  which is a EUR {OBSERVED[(2, 1)][0] - 4:.2f} net result against a EUR 4.00 two-ticket spend.")
med = OBSERVED[(2, 1)][0]
print(f"  Median outcome of the whole EUR 4.00 purchase: EUR 0.00 (93.7% of the time).")
