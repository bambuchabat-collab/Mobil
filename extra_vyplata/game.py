"""Game model for the TIPOS numerical lottery EXTRA VYPLATA (Slovakia).

Rules (verified against tipos.sk / etipos.sk, August 2026)
---------------------------------------------------------
* The player picks 6 main numbers from 1..27.
* The player also picks 1 "dodatkove cislo" (powerball) from 1..7.
* Two independent drawing machines: 6 of 27, then 1 of 7.
* One tip costs EUR 1.50; one bet slip holds up to 8 tips (EUR 12.00).
* Draws take place Mondays at 18:00, and Thursdays as well since 2026-04-23.
* Eight prize tiers.  Tier 1 (6+1) pays EUR 480,000 as an annuity of
  EUR 4,000/month for 10 years.  Tier 2 (6+0) pays EUR 30,000 in one payment.
  Tiers 3..8 are pari-mutuel: the amount depends on the pool and on how many
  tickets share the tier, so it changes from draw to draw.

The single most important structural fact for "win at least something":
the lowest paying tier is 3+0, i.e. three main numbers.  The powerball
never pays on its own.  Therefore

    P(any prize) == P(at least 3 of the 6 main numbers)

and the powerball choice has *no influence whatsoever* on whether a tip
wins something.  It only decides which of the paired tiers you land in.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import comb

# --------------------------------------------------------------------------
# Game constants
# --------------------------------------------------------------------------

MAIN_POOL = 27          # main numbers are drawn from 1..27
MAIN_PICK = 6           # the player marks 6 of them
EXTRA_POOL = 7          # the powerball is drawn from 1..7
TIP_PRICE = Fraction(3, 2)          # EUR 1.50 per tip
TIPS_PER_SLIP = 8                   # max tips on one bet slip
SLIP_PRICE = TIP_PRICE * TIPS_PER_SLIP

TOTAL_MAIN_COMBOS = comb(MAIN_POOL, MAIN_PICK)      # 296_010
TOTAL_OUTCOMES = TOTAL_MAIN_COMBOS * EXTRA_POOL     # 2_072_070

#: Lowest number of main hits that still pays anything.
MIN_PAYING_HITS = 3


@dataclass(frozen=True)
class Tier:
    """One prize tier of the game plan."""

    rank: int          # 1..8, as printed on the official results table
    hits: int          # main numbers matched
    extra: bool        # powerball matched?
    label: str
    fixed_eur: float | None   # fixed prize, or None when pari-mutuel

    @property
    def combos(self) -> int:
        """How many of the TOTAL_OUTCOMES equally likely draws land in this tier."""
        main_ways = comb(MAIN_PICK, self.hits) * comb(
            MAIN_POOL - MAIN_PICK, MAIN_PICK - self.hits
        )
        extra_ways = 1 if self.extra else EXTRA_POOL - 1
        return main_ways * extra_ways

    @property
    def probability(self) -> Fraction:
        return Fraction(self.combos, TOTAL_OUTCOMES)

    @property
    def odds_one_in(self) -> float:
        return TOTAL_OUTCOMES / self.combos


#: The official eight tiers, best first.
TIERS: tuple[Tier, ...] = (
    Tier(1, 6, True, "6+1", 480_000.0),
    Tier(2, 6, False, "6", 30_000.0),
    Tier(3, 5, True, "5+1", None),
    Tier(4, 5, False, "5", None),
    Tier(5, 4, True, "4+1", None),
    Tier(6, 4, False, "4", None),
    Tier(7, 3, True, "3+1", None),
    Tier(8, 3, False, "3", None),
)


def hit_distribution() -> dict[int, Fraction]:
    """P(exactly k of the 6 main numbers matched), k = 0..6."""
    return {
        k: Fraction(
            comb(MAIN_PICK, k) * comb(MAIN_POOL - MAIN_PICK, MAIN_PICK - k),
            TOTAL_MAIN_COMBOS,
        )
        for k in range(MAIN_PICK + 1)
    }


def p_any_prize() -> Fraction:
    """Probability that a single tip wins *something* (>= 3 main numbers).

    Independent of the powerball, because the lowest tier is 3+0.
    """
    dist = hit_distribution()
    return sum(
        (dist[k] for k in range(MIN_PAYING_HITS, MAIN_PICK + 1)), Fraction(0)
    )


def draws_won_by_one_tip() -> int:
    """Number of distinct 6-number draws (out of 296_010) that pay a tip."""
    return sum(
        comb(MAIN_PICK, k) * comb(MAIN_POOL - MAIN_PICK, MAIN_PICK - k)
        for k in range(MIN_PAYING_HITS, MAIN_PICK + 1)
    )


# --------------------------------------------------------------------------
# Expected value
# --------------------------------------------------------------------------

#: Pari-mutuel payouts actually observed in the draw of 2026-08-13, together
#: with the number of winning tips.  Used to calibrate the return-to-player
#: estimate.  Source: tipos.sk results table for that draw.
REFERENCE_DRAW = {
    "date": "2026-08-13",
    "payouts": {          # tier label -> EUR per winning tip
        "5+1": 364.90,
        "5": 104.60,
        "4+1": 27.60,
        "4": 9.50,
        "3+1": 4.80,
        "3": 3.00,
    },
    "winners": {          # tier label -> number of winning tips
        "5+1": 3,
        "5": 30,
        "4+1": 116,
        "4": 825,
        "3+1": 942,
        "3": 6544,
    },
}


def estimate_tips_sold(reference: dict = REFERENCE_DRAW) -> float:
    """Back out how many tips were in play from the observed winner counts.

    Every tier's winner count is an unbiased estimate of
    ``tips_sold * P(tier)``, so we pool them by total expected weight.  The
    low tiers dominate and are the statistically stable ones.
    """
    by_label = {t.label: t for t in TIERS}
    observed = sum(reference["winners"].values())
    expected_rate = sum(
        float(by_label[label].probability) for label in reference["winners"]
    )
    return observed / expected_rate


def expected_value_per_tip(reference: dict = REFERENCE_DRAW) -> dict[str, float]:
    """Return-to-player breakdown for one EUR 1.50 tip.

    The two fixed jackpot tiers are exact.  The pari-mutuel tiers are valued
    at the payouts of the reference draw, which is an estimate: those amounts
    move with the pool and with the number of co-winners.
    """
    by_label = {t.label: t for t in TIERS}

    fixed_ev = sum(
        float(t.probability) * t.fixed_eur for t in TIERS if t.fixed_eur is not None
    )
    pari_ev = sum(
        float(by_label[label].probability) * amount
        for label, amount in reference["payouts"].items()
    )
    total = fixed_ev + pari_ev
    stake = float(TIP_PRICE)
    return {
        "fixed_tiers_ev": fixed_ev,
        "pari_mutuel_ev": pari_ev,
        "total_ev": total,
        "stake": stake,
        "rtp": total / stake,
        "house_edge": 1.0 - total / stake,
        "tips_sold_estimate": estimate_tips_sold(reference),
    }


# --------------------------------------------------------------------------
# Bitmask helpers -- tickets and draws are 27-bit masks over numbers 1..27
# --------------------------------------------------------------------------


def to_mask(numbers) -> int:
    """Turn an iterable of numbers in 1..27 into a bitmask."""
    mask = 0
    for n in numbers:
        if not 1 <= n <= MAIN_POOL:
            raise ValueError(f"number {n} outside 1..{MAIN_POOL}")
        bit = 1 << (n - 1)
        if mask & bit:
            raise ValueError(f"duplicate number {n}")
        mask |= bit
    return mask


def from_mask(mask: int) -> tuple[int, ...]:
    """Inverse of :func:`to_mask`."""
    return tuple(i + 1 for i in range(MAIN_POOL) if mask >> i & 1)


def all_draw_masks() -> list[int]:
    """Every one of the 296_010 possible main-number draws, as bitmasks."""
    return [to_mask(c) for c in combinations(range(1, MAIN_POOL + 1), MAIN_PICK)]
