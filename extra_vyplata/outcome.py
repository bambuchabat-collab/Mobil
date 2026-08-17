"""Exact outcome distribution for a complete bet slip.

:mod:`coverage` answers "do I win anything".  This module answers "what is
the best thing I win", by sweeping all 296,010 x 7 = 2,072,070 equally
likely draws and recording, for each one, the highest tier any tip on the
slip reaches.

It also settles the one real decision the powerball offers.  Because the
bottom tier is 3+0, the powerball cannot make the difference between
winning and not winning -- but it does decide whether a win lands in a
"+1" tier or its plain twin, so the way you spread it across the slip is a
variance choice worth getting right.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .coverage import Ticket, draw_universe, hits_against
from .game import EXTRA_POOL, MIN_PAYING_HITS, TIERS, TIP_PRICE, to_mask

#: (main hits, powerball matched) -> tier label, ordered best first.
_KEY_TO_LABEL = {(t.hits, t.extra): t.label for t in TIERS}


@dataclass
class SlipOutcome:
    """Distribution over the best tier reached by a slip."""

    tier_probability: dict[str, float]
    p_any_prize: float
    n_tips: int
    cost_eur: float
    expected_return_eur: float = field(default=0.0)

    @property
    def p_plus_one_tier(self) -> float:
        return sum(
            p for label, p in self.tier_probability.items() if label.endswith("+1")
        )


def _group_max_hits(
    tickets: list[Ticket], powerballs: list[int]
) -> tuple[dict[int, np.ndarray], np.ndarray]:
    """Per-powerball-group and overall best main-number hit counts per draw."""
    draws = draw_universe()
    overall = np.zeros(len(draws), dtype=np.int8)
    groups: dict[int, np.ndarray] = {}

    for ticket, pb in zip(tickets, powerballs):
        h = hits_against(draws, to_mask(ticket)).astype(np.int8)
        overall = np.maximum(overall, h)
        if pb in groups:
            groups[pb] = np.maximum(groups[pb], h)
        else:
            groups[pb] = h
    return groups, overall


def slip_outcome(
    tickets: list[Ticket],
    powerballs: list[int],
    payouts: dict[str, float] | None = None,
) -> SlipOutcome:
    """Exact probability of each best-tier result for the given slip.

    ``powerballs[i]`` is the number 1..7 marked on tip ``i``.
    """
    if len(tickets) != len(powerballs):
        raise ValueError("each tip needs exactly one powerball")
    if not all(1 <= p <= EXTRA_POOL for p in powerballs):
        raise ValueError("powerball outside 1..7")

    groups, overall = _group_max_hits(tickets, powerballs)
    n_draws = len(overall)
    weight = 1.0 / (n_draws * EXTRA_POOL)

    tally: dict[str, float] = {t.label: 0.0 for t in TIERS}
    p_any = 0.0

    for e in range(1, EXTRA_POOL + 1):
        matched = groups.get(e)
        # Best key is the lexicographic max of (hits, extra) over all tips.
        if matched is None:
            best_hits, best_extra = overall, np.zeros(n_draws, dtype=bool)
        else:
            take_matched = matched >= overall
            best_hits = np.where(take_matched, matched, overall)
            best_extra = take_matched & (matched >= MIN_PAYING_HITS)

        paying = best_hits >= MIN_PAYING_HITS
        p_any += float(np.count_nonzero(paying)) * weight

        for hits in range(MIN_PAYING_HITS, 7):
            for extra in (True, False):
                sel = paying & (best_hits == hits) & (best_extra == extra)
                count = int(np.count_nonzero(sel))
                if count:
                    tally[_KEY_TO_LABEL[(hits, extra)]] += count * weight

    cost = len(tickets) * float(TIP_PRICE)
    out = SlipOutcome(
        tier_probability=tally,
        p_any_prize=p_any,
        n_tips=len(tickets),
        cost_eur=cost,
    )
    if payouts:
        out.expected_return_eur = sum(
            tally[label] * payouts.get(label, 0.0) for label in tally
        )
    return out


def spread_powerballs(n_tips: int) -> list[int]:
    """Cycle 1..7 across the tips -- guarantees a tip holds the drawn ball."""
    return [(i % EXTRA_POOL) + 1 for i in range(n_tips)]


def single_powerball(n_tips: int, value: int = 1) -> list[int]:
    """Mark the same powerball on every tip -- all-or-nothing on the upgrade."""
    return [value] * n_tips


def compare_powerball_strategies(tickets: list[Ticket]) -> dict[str, SlipOutcome]:
    """Spreading versus concentrating the powerball, on identical main numbers."""
    n = len(tickets)
    return {
        "spread": slip_outcome(tickets, spread_powerballs(n)),
        "concentrated": slip_outcome(tickets, single_powerball(n)),
    }
