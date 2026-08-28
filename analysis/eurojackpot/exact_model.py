"""
Eurojackpot (5/50 + 2/12) - exact combinatorial model.

Everything here is exact integer / Fraction arithmetic. No simulation,
no Monte-Carlo, no floating point in the derivation (floats only for display).

Game parameters verified against tipos.sk (see REPORT.md for sources):
  - 5 main numbers from 1..50
  - 2 Euro numbers from 1..12
  - stake EUR 2.00 per tip
  - draws Tuesday and Friday after 20:00
"""

from fractions import Fraction
from math import comb

MAIN_POOL, MAIN_PICK = 50, 5
EURO_POOL, EURO_PICK = 12, 2

TOTAL_OUTCOMES = comb(MAIN_POOL, MAIN_PICK) * comb(EURO_POOL, EURO_PICK)

# The 12 paying tiers, in the official TIPOS order (poradie 1..12),
# with the published odds denominator "Pravdepodobnosť 1 : N"
# Source: tipos.sk/loterie/ciselne-loterie/informacie-k-loteriam/pravdepodobnosti
TIPOS_OFFICIAL = [
    ((5, 2), 139_838_160),
    ((5, 1), 6_991_908),
    ((5, 0), 3_107_515),
    ((4, 2), 621_503),
    ((4, 1), 31_075),
    ((3, 2), 14_125),
    ((4, 0), 13_811),
    ((2, 2), 985),
    ((3, 1), 706),
    ((3, 0), 314),
    ((1, 2), 188),
    ((2, 1), 49),
]

PAYING = {tier for tier, _ in TIPOS_OFFICIAL}


def tier_count(k, j):
    """Number of draw outcomes giving exactly k main matches and j euro matches."""
    return (comb(MAIN_PICK, k) * comb(MAIN_POOL - MAIN_PICK, MAIN_PICK - k)
            * comb(EURO_PICK, j) * comb(EURO_POOL - EURO_PICK, EURO_PICK - j))


def single_ticket_table():
    """Exact probability of every (k, j) state for one ticket."""
    return {(k, j): Fraction(tier_count(k, j), TOTAL_OUTCOMES)
            for k in range(MAIN_PICK + 1) for j in range(EURO_PICK + 1)}


def p_any_prize_single():
    return sum(Fraction(tier_count(k, j), TOTAL_OUTCOMES) for (k, j) in PAYING)


# ---------------------------------------------------------------------------
# Two-ticket joint distribution (exact, multivariate hypergeometric)
# ---------------------------------------------------------------------------

def _multivariate_hypergeometric(sizes, draw):
    """
    Exact enumeration of how `draw` balls split across disjoint regions of the
    given `sizes`. Yields (counts, weight) where weight is the number of ways.
    """
    out = []

    def rec(i, remaining, cur, w):
        if i == len(sizes) - 1:
            if remaining <= sizes[i]:
                out.append((tuple(cur) + (remaining,), w * comb(sizes[i], remaining)))
            return
        for n in range(min(sizes[i], remaining) + 1):
            rec(i + 1, remaining - n, cur + [n], w * comb(sizes[i], n))

    rec(0, draw, [], 1)
    return out


def joint_distribution(main_overlap, euro_overlap):
    """
    Exact joint distribution of (mA, eA, mB, eB) for two tickets whose main sets
    share `main_overlap` numbers and whose euro pairs share `euro_overlap`.

    Regions for the main pool: A&B, A-only, B-only, neither.
    Regions for the euro pool: same structure.
    Main draw and euro draw are independent, so the joint law is the product.

    Returns {(mA, eA, mB, eB): weight} with sum(weights) == TOTAL_OUTCOMES.
    """
    a = main_overlap
    assert 0 <= a <= MAIN_PICK
    main_regions = [a, MAIN_PICK - a, MAIN_PICK - a, MAIN_POOL - (2 * MAIN_PICK - a)]

    e = euro_overlap
    assert 0 <= e <= EURO_PICK
    euro_regions = [e, EURO_PICK - e, EURO_PICK - e, EURO_POOL - (2 * EURO_PICK - e)]

    main_law = {}
    for (n11, n10, n01, _n00), w in _multivariate_hypergeometric(main_regions, MAIN_PICK):
        main_law[(n11 + n10, n11 + n01)] = main_law.get((n11 + n10, n11 + n01), 0) + w

    euro_law = {}
    for (s11, s10, s01, _s00), w in _multivariate_hypergeometric(euro_regions, EURO_PICK):
        euro_law[(s11 + s10, s11 + s01)] = euro_law.get((s11 + s10, s11 + s01), 0) + w

    joint = {}
    for (mA, mB), wm in main_law.items():
        for (eA, eB), we in euro_law.items():
            joint[(mA, eA, mB, eB)] = joint.get((mA, eA, mB, eB), 0) + wm * we
    return joint


def two_ticket_stats(main_overlap, euro_overlap):
    """Exact two-ticket probabilities for a given overlap configuration."""
    joint = joint_distribution(main_overlap, euro_overlap)
    assert sum(joint.values()) == TOTAL_OUTCOMES, "joint law must be a probability law"

    w_union = w_both = w_ge4 = w_42 = w_both42 = 0
    for (mA, eA, mB, eB), w in joint.items():
        a_pays = (mA, eA) in PAYING
        b_pays = (mB, eB) in PAYING
        if a_pays or b_pays:
            w_union += w
        if a_pays and b_pays:
            w_both += w
        if mA >= 4 or mB >= 4:
            w_ge4 += w
        if (mA, eA) == (4, 2) or (mB, eB) == (4, 2):
            w_42 += w
        if (mA, eA) == (4, 2) and (mB, eB) == (4, 2):
            w_both42 += w

    F = lambda w: Fraction(w, TOTAL_OUTCOMES)
    return {
        "main_overlap": main_overlap,
        "euro_overlap": euro_overlap,
        "p_union_any_prize": F(w_union),
        "p_both_win": F(w_both),
        "p_union_ge4_main": F(w_ge4),
        "p_union_4plus2": F(w_42),
        "p_both_4plus2": F(w_both42),
    }


def fmt(p):
    """Format a Fraction probability as percent + '1 in N'."""
    if p == 0:
        return "0 (impossible)"
    return f"{float(p) * 100:.6f}%  (1 in {1 / float(p):,.2f})"
