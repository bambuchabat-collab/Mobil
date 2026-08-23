"""Generalised engine for pick-k-of-n numerical lotteries.

The EXTRA VYPLATA toolkit in ``extra_vyplata/`` is hardwired to 6-of-27.
This module takes the game as a parameter so the same exact-enumeration
machinery works for LOTO 5 z 35, and for anything else of the same shape.

Masks are 64-bit here, because a 35-number pool no longer fits in uint32.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations, islice
from math import comb

import numpy as np

Ticket = tuple[int, ...]


@dataclass(frozen=True)
class GameSpec:
    """Everything the engine needs to know about a lottery."""

    name: str
    pool: int            # numbers are 1..pool
    pick: int            # numbers marked per tip, and numbers drawn
    min_hits: int        # fewest matches that still pays something
    tip_price: float     # EUR

    @property
    def total_draws(self) -> int:
        return comb(self.pool, self.pick)

    def hit_combos(self, k: int) -> int:
        """How many draws match a given tip in exactly ``k`` numbers."""
        return comb(self.pick, k) * comb(self.pool - self.pick, self.pick - k)

    def draws_won_by_one_tip(self) -> int:
        return sum(self.hit_combos(k) for k in range(self.min_hits, self.pick + 1))

    def p_any_prize(self) -> float:
        return self.draws_won_by_one_tip() / self.total_draws

    def p_jackpot(self) -> float:
        return 1 / self.total_draws


LOTO_5_Z_35 = GameSpec("LOTO 5 z 35", pool=35, pick=5, min_hits=3, tip_price=0.60)
EXTRA_VYPLATA = GameSpec("EXTRA VYPLATA", pool=27, pick=6, min_hits=3, tip_price=1.50)


# --------------------------------------------------------------------------
# Draw universe and exact evaluation
# --------------------------------------------------------------------------

_UNIVERSE: dict[tuple[int, int], np.ndarray] = {}


def to_mask(numbers, spec: GameSpec) -> int:
    mask = 0
    for n in numbers:
        if not 1 <= n <= spec.pool:
            raise ValueError(f"number {n} outside 1..{spec.pool}")
        bit = 1 << (n - 1)
        if mask & bit:
            raise ValueError(f"duplicate number {n}")
        mask |= bit
    return mask


def from_mask(mask: int, spec: GameSpec) -> Ticket:
    return tuple(i + 1 for i in range(spec.pool) if mask >> i & 1)


def draw_universe(spec: GameSpec) -> np.ndarray:
    key = (spec.pool, spec.pick)
    if key not in _UNIVERSE:
        _UNIVERSE[key] = np.fromiter(
            (to_mask(c, spec) for c in combinations(range(1, spec.pool + 1), spec.pick)),
            dtype=np.uint64,
            count=spec.total_draws,
        )
    return _UNIVERSE[key]


def wins_against(draws: np.ndarray, mask: int, spec: GameSpec) -> np.ndarray:
    return np.bitwise_count(draws & np.uint64(mask)) >= spec.min_hits


@dataclass
class SetEvaluation:
    tickets: list[Ticket]
    covered: int
    total: int
    expected_winning_tips: float
    cost_eur: float
    disjoint_events: bool

    @property
    def p_any_prize(self) -> float:
        return self.covered / self.total

    @property
    def odds_one_in(self) -> float:
        return self.total / self.covered if self.covered else float("inf")


def evaluate(tickets: list[Ticket], spec: GameSpec) -> SetEvaluation:
    """Exact P(at least one tip pays), by sweeping every possible draw."""
    draws = draw_universe(spec)
    paid = np.zeros(len(draws), dtype=np.int16)
    for t in tickets:
        paid += wins_against(draws, to_mask(t, spec), spec)
    covered = int(np.count_nonzero(paid))
    return SetEvaluation(
        tickets=list(tickets),
        covered=covered,
        total=len(draws),
        expected_winning_tips=float(paid.mean()),
        cost_eur=len(tickets) * spec.tip_price,
        disjoint_events=bool(paid.max() <= 1),
    )


# --------------------------------------------------------------------------
# The structural result that makes small games easy to solve exactly
# --------------------------------------------------------------------------


def union_bound(n_tickets: int, spec: GameSpec) -> float:
    """Sum of individual win probabilities -- an upper limit no set can beat."""
    return min(1.0, n_tickets * spec.p_any_prize())


def wins_can_coincide(spec: GameSpec) -> bool:
    """Can two tips that share no number both be paid by the same draw?

    Two tips each need ``min_hits`` matches out of a draw of ``pick``
    numbers.  If the tips are disjoint those matches use distinct numbers, so
    it takes ``2 * min_hits`` drawn numbers to pay both.  When the draw is
    smaller than that, disjoint tips can never win together -- their win
    events are mutually exclusive, and probabilities simply add.
    """
    return 2 * spec.min_hits <= spec.pick


def max_disjoint_tickets(spec: GameSpec) -> int:
    return spec.pool // spec.pick


def optimal_disjoint_set(n_tickets: int, spec: GameSpec, order=None) -> list[Ticket]:
    """``n`` pairwise disjoint tips, carved out of the pool in order.

    When :func:`wins_can_coincide` is False this set is provably optimal:
    it attains the union bound exactly, which nothing can exceed.
    """
    if n_tickets > max_disjoint_tickets(spec):
        raise ValueError(
            f"{spec.name}: at most {max_disjoint_tickets(spec)} disjoint tips fit"
        )
    seq = list(order) if order is not None else list(range(1, spec.pool + 1))
    return [
        tuple(sorted(seq[i * spec.pick : (i + 1) * spec.pick]))
        for i in range(n_tickets)
    ]


# --------------------------------------------------------------------------
# Search, for the cases where disjointness is not achievable
# --------------------------------------------------------------------------


def _random_tickets(n: int, spec: GameSpec, rng: random.Random) -> list[Ticket]:
    pool = list(range(1, spec.pool + 1))
    return [tuple(sorted(rng.sample(pool, spec.pick))) for _ in range(n)]


def random_baseline_stats(
    n_tickets: int, spec: GameSpec, replicates: int = 40, seed: int = 1
) -> dict[str, float]:
    rng = random.Random(seed)
    ps = [
        evaluate(_random_tickets(n_tickets, spec, rng), spec).p_any_prize
        for _ in range(replicates)
    ]
    mean = sum(ps) / len(ps)
    sd = (sum((p - mean) ** 2 for p in ps) / (len(ps) - 1)) ** 0.5 if len(ps) > 1 else 0.0
    return {"mean": mean, "sd": sd, "min": min(ps), "max": max(ps)}


def worst_case_baseline(n_tickets: int, spec: GameSpec) -> list[Ticket]:
    """Maximally correlated tips: the first n sets in lexicographic order."""
    return list(islice(combinations(range(1, spec.pool + 1), spec.pick), n_tickets))


def guaranteed_wheel_lower_bound(spec: GameSpec) -> int:
    """Fewest tips that could conceivably pay on every possible draw."""
    per = spec.draws_won_by_one_tip()
    return -(-spec.total_draws // per)
