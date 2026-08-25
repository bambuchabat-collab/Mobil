"""Engine for lotteries with a separate pool of bonus numbers.

EXTRA VYPLATA and LOTO 5 z 35 share one property that makes them easy: the
bonus ball cannot decide whether you win, only how much.  EUROMILIONY and
Eurojackpot are different -- their lowest tiers *require* bonus matches, so
the bonus pool enters the win probability itself, and the way a bonus number
is spread across several tips becomes a real decision rather than a
cosmetic one.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import comb

import numpy as np


@dataclass(frozen=True)
class BonusGame:
    name: str
    main_pool: int
    main_pick: int
    extra_pool: int
    extra_pick: int
    winning: frozenset[tuple[int, int]]   # (main matched, extra matched)
    tip_price: float

    @property
    def main_combos(self) -> int:
        return comb(self.main_pool, self.main_pick)

    @property
    def extra_combos(self) -> int:
        return comb(self.extra_pool, self.extra_pick)

    @property
    def total_outcomes(self) -> int:
        return self.main_combos * self.extra_combos

    def p_main(self, k: int) -> float:
        return (
            comb(self.main_pick, k)
            * comb(self.main_pool - self.main_pick, self.main_pick - k)
            / self.main_combos
        )

    def p_extra(self, e: int) -> float:
        return (
            comb(self.extra_pick, e)
            * comb(self.extra_pool - self.extra_pick, self.extra_pick - e)
            / self.extra_combos
        )

    def p_tier(self, k: int, e: int) -> float:
        return self.p_main(k) * self.p_extra(e)

    def p_any_prize(self) -> float:
        return sum(self.p_tier(k, e) for k, e in self.winning)

    def p_jackpot(self) -> float:
        return 1 / self.total_outcomes


EUROMILIONY = BonusGame(
    name="EUROMILIONY",
    main_pool=33, main_pick=7,
    extra_pool=6, extra_pick=1,
    winning=frozenset({(7,1),(7,0),(6,1),(6,0),(5,1),(5,0),(4,1),(4,0),(3,1),(2,1)}),
    tip_price=1.50,
)

EUROJACKPOT = BonusGame(
    name="Eurojackpot",
    main_pool=50, main_pick=5,
    extra_pool=12, extra_pick=2,
    winning=frozenset({(5,2),(5,1),(5,0),(4,2),(4,1),(4,0),
                       (3,2),(2,2),(3,1),(3,0),(1,2),(2,1)}),
    tip_price=2.00,
)


def tier_table(g: BonusGame) -> list[tuple[int, int, float]]:
    """Winning tiers, best first, with their exact probabilities."""
    rows = [(k, e, g.p_tier(k, e)) for k, e in g.winning]
    return sorted(rows, key=lambda r: (-r[0], -r[1]))


# --------------------------------------------------------------------------
# Exact evaluation of a multi-tip slip, by sweeping the main-number space
# --------------------------------------------------------------------------


def _main_masks(g: BonusGame) -> np.ndarray:
    return np.fromiter(
        (
            sum(1 << (n - 1) for n in c)
            for c in combinations(range(1, g.main_pool + 1), g.main_pick)
        ),
        dtype=np.uint64,
        count=g.main_combos,
    )


def evaluate_slip(
    tickets: list[tuple[tuple[int, ...], tuple[int, ...]]], g: BonusGame
) -> dict:
    """P(at least one tip wins something), exactly.

    ``tickets`` is a list of (main numbers, extra numbers).  The main-number
    space is enumerated in full; the bonus space is enumerated in full too,
    so the result is closed-form rather than sampled.
    """
    draws = _main_masks(g)
    hits = [
        np.bitwise_count(draws & np.uint64(sum(1 << (n - 1) for n in main))).astype(np.int8)
        for main, _ in tickets
    ]

    extra_sets = [set(e) for _, e in tickets]
    win_by_main = {}          # (needed extra matches) -> handled per combo below
    total_weight = 0.0
    p_win = 0.0

    for edraw in combinations(range(1, g.extra_pool + 1), g.extra_pick):
        ed = set(edraw)
        # for this bonus draw, how many bonus numbers each tip matched
        e_match = [len(s & ed) for s in extra_sets]
        any_win = np.zeros(len(draws), dtype=bool)
        for h, em in zip(hits, e_match):
            need = {k for k, e in g.winning if e == em}
            if not need:
                continue
            ok = np.zeros(len(draws), dtype=bool)
            for k in need:
                ok |= h == k
            any_win |= ok
        p_win += any_win.mean()
        total_weight += 1.0

    p_win /= total_weight
    return {
        "p_any_prize": float(p_win),
        "n_tips": len(tickets),
        "cost_eur": len(tickets) * g.tip_price,
        "odds_one_in": 1 / p_win if p_win else float("inf"),
    }
