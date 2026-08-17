"""Combinatorial ticket-set design.

Every single tip in EXTRA VYPLATA has exactly the same chance of winning
something: 29,877 of the 296,010 possible main draws pay it, i.e. 10.093%.
Choosing 3-8-14-19-22-27 instead of 1-2-3-4-5-6 does not move that number by
one part in a billion.

So when you buy several tips, the *only* thing you control is how much the
tips overlap.  Two tips that share five numbers win and lose together; two
disjoint tips fail together far less often.  That correlation structure is a
real, exploitable degree of freedom -- it does not change the expected
payout by a cent, but it changes the probability of walking away with
*something*, which is exactly what was asked for.

This module evaluates ticket sets exactly (by sweeping all 296,010 draws,
no simulation) and searches for good ones.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations, islice

import numpy as np

from .game import (
    MAIN_PICK,
    MAIN_POOL,
    MIN_PAYING_HITS,
    TIP_PRICE,
    TOTAL_MAIN_COMBOS,
    from_mask,
    to_mask,
)

Ticket = tuple[int, ...]


# --------------------------------------------------------------------------
# The universe of draws, as a packed uint32 array of 27-bit masks
# --------------------------------------------------------------------------

_DRAW_CACHE: np.ndarray | None = None


def draw_universe() -> np.ndarray:
    """All 296,010 possible main-number draws as uint32 bitmasks."""
    global _DRAW_CACHE
    if _DRAW_CACHE is None:
        masks = np.fromiter(
            (
                to_mask(c)
                for c in combinations(range(1, MAIN_POOL + 1), MAIN_PICK)
            ),
            dtype=np.uint32,
            count=TOTAL_MAIN_COMBOS,
        )
        _DRAW_CACHE = masks
    return _DRAW_CACHE


def hits_against(draws: np.ndarray, ticket_mask: int) -> np.ndarray:
    """How many main numbers each draw shares with ``ticket_mask``."""
    return np.bitwise_count(draws & np.uint32(ticket_mask))


def wins_against(draws: np.ndarray, ticket_mask: int) -> np.ndarray:
    """Boolean mask: which draws pay this ticket at least the bottom tier."""
    return hits_against(draws, ticket_mask) >= MIN_PAYING_HITS


# --------------------------------------------------------------------------
# Exact evaluation of a ticket set
# --------------------------------------------------------------------------


@dataclass
class SetEvaluation:
    tickets: list[Ticket]
    covered: int                 # draws paying at least one tip
    total: int                   # 296,010
    expected_winning_tips: float
    hit_histogram: dict[int, int]   # #tips paid -> #draws
    cost_eur: float

    @property
    def p_any_prize(self) -> float:
        return self.covered / self.total

    @property
    def odds_one_in(self) -> float:
        return self.total / self.covered if self.covered else float("inf")

    @property
    def guaranteed(self) -> bool:
        return self.covered == self.total


def evaluate(tickets: list[Ticket]) -> SetEvaluation:
    """Exact probability that a ticket set wins at least one prize.

    Sweeps the whole draw space, so the result is a closed-form probability
    rather than a Monte-Carlo estimate.
    """
    draws = draw_universe()
    paid_count = np.zeros(len(draws), dtype=np.int16)
    for t in tickets:
        paid_count += wins_against(draws, to_mask(t))

    covered = int(np.count_nonzero(paid_count))
    hist_vals, hist_counts = np.unique(paid_count, return_counts=True)
    return SetEvaluation(
        tickets=list(tickets),
        covered=covered,
        total=len(draws),
        expected_winning_tips=float(paid_count.mean()),
        hit_histogram={int(v): int(c) for v, c in zip(hist_vals, hist_counts)},
        cost_eur=len(tickets) * float(TIP_PRICE),
    )


def pairwise_overlap_penalty(tickets: list[Ticket]) -> dict[int, int]:
    """How many ticket pairs share k numbers, k = 0..6.

    A healthy wheel is dominated by pairs sharing 0 or 1 numbers.
    """
    tally = {k: 0 for k in range(MAIN_PICK + 1)}
    for a, b in combinations(tickets, 2):
        tally[len(set(a) & set(b))] += 1
    return tally


# --------------------------------------------------------------------------
# Candidate scoring: how many still-uncovered draws would a ticket pick up?
# --------------------------------------------------------------------------


def _score_candidates(
    candidates: np.ndarray, uncovered: np.ndarray, chunk: int = 64
) -> np.ndarray:
    """Vectorised: for each candidate mask, count uncovered draws it pays."""
    scores = np.empty(len(candidates), dtype=np.int64)
    for start in range(0, len(candidates), chunk):
        block = candidates[start : start + chunk]
        inter = uncovered[None, :] & block[:, None]
        scores[start : start + chunk] = (
            np.bitwise_count(inter) >= MIN_PAYING_HITS
        ).sum(axis=1)
    return scores


def _random_tickets(n: int, rng: random.Random) -> list[Ticket]:
    pool = list(range(1, MAIN_POOL + 1))
    return [tuple(sorted(rng.sample(pool, MAIN_PICK))) for _ in range(n)]


def _starved_tickets(
    n: int, chosen: list[Ticket], rng: random.Random
) -> list[Ticket]:
    """Candidates biased towards numbers the current wheel under-uses.

    Pure random sampling wastes most of its candidates on numbers that are
    already saturated; weighting by starvation finds better picks per unit of
    compute.
    """
    usage = {n_: 0 for n_ in range(1, MAIN_POOL + 1)}
    for t in chosen:
        for x in t:
            usage[x] += 1
    worst = max(usage.values()) if usage else 0
    weights = [1 + (worst - usage[n_]) ** 2 for n_ in range(1, MAIN_POOL + 1)]
    numbers = list(range(1, MAIN_POOL + 1))

    out = []
    for _ in range(n):
        picked: set[int] = set()
        w = list(weights)
        while len(picked) < MAIN_PICK:
            choice = rng.choices(numbers, weights=w, k=1)[0]
            if choice not in picked:
                picked.add(choice)
                w[choice - 1] = 0.0
        out.append(tuple(sorted(picked)))
    return out


def _candidate_pool(
    chosen: list[Ticket], pool_size: int, rng: random.Random
) -> np.ndarray:
    half = pool_size // 2
    cands = _random_tickets(pool_size - half, rng) + _starved_tickets(
        half, chosen, rng
    )
    return np.fromiter(
        (to_mask(t) for t in cands), dtype=np.uint32, count=len(cands)
    )


# --------------------------------------------------------------------------
# Guaranteed-win wheel: cover every possible draw
# --------------------------------------------------------------------------


def lower_bound_tickets() -> int:
    """No wheel smaller than this can possibly cover every draw.

    One tip pays on 29,877 of 296,010 draws, so at least
    ceil(296010 / 29877) = 10 tips are needed.  (The true minimum is larger,
    because tips cannot be made to overlap this little.)
    """
    from .game import draws_won_by_one_tip

    per_ticket = draws_won_by_one_tip()
    return -(-TOTAL_MAIN_COMBOS // per_ticket)


def build_guaranteed_wheel(
    pool_size: int = 1500, seed: int = 20260817, restarts: int = 6
) -> list[Ticket]:
    """Search for a small set of tips that pays a prize on *every* draw.

    Greedy set cover with randomised candidate pools, repeated from several
    seeds; the smallest wheel found is returned.  The result is verified
    exactly by :func:`evaluate` before being handed back.
    """
    best: list[Ticket] | None = None

    for r in range(restarts):
        rng = random.Random(seed + r * 7919)
        draws = draw_universe()
        uncovered = draws
        chosen: list[Ticket] = []

        # By symmetry every first pick is equivalent, so fix one and skip a
        # pointless full-universe scan.
        first = tuple(sorted(rng.sample(range(1, MAIN_POOL + 1), MAIN_PICK)))
        chosen.append(first)
        uncovered = uncovered[~wins_against(uncovered, to_mask(first))]

        while len(uncovered):
            cands = _candidate_pool(chosen, pool_size, rng)
            scores = _score_candidates(cands, uncovered)
            best_idx = int(np.argmax(scores))
            if scores[best_idx] == 0:
                raise RuntimeError("candidate pool exhausted without covering")
            pick_mask = int(cands[best_idx])
            chosen.append(from_mask(pick_mask))
            uncovered = uncovered[~wins_against(uncovered, pick_mask)]

        chosen = _prune(chosen)
        if best is None or len(chosen) < len(best):
            best = chosen

    assert best is not None
    if not evaluate(best).guaranteed:
        raise RuntimeError("constructed wheel failed verification")
    return best


def _prune(tickets: list[Ticket]) -> list[Ticket]:
    """Drop any tip that the rest of the wheel already makes redundant."""
    draws = draw_universe()
    keep = list(tickets)
    changed = True
    while changed:
        changed = False
        for t in list(keep):
            trial = [x for x in keep if x != t]
            if not trial:
                continue
            covered = np.zeros(len(draws), dtype=bool)
            for u in trial:
                covered |= wins_against(draws, to_mask(u))
            if covered.all():
                keep = trial
                changed = True
                break
    return keep


# --------------------------------------------------------------------------
# Best ticket set for a fixed budget
# --------------------------------------------------------------------------


def optimize_budget(
    n_tickets: int,
    pool_size: int = 1200,
    seed: int = 20260817,
    passes: int = 4,
) -> list[Ticket]:
    """Maximise P(at least one prize) for exactly ``n_tickets`` tips.

    Greedy construction followed by steepest-descent replacement: each tip in
    turn is removed and re-chosen against the coverage of all the others,
    until no swap helps.
    """
    rng = random.Random(seed)
    draws = draw_universe()

    chosen: list[Ticket] = [
        tuple(sorted(rng.sample(range(1, MAIN_POOL + 1), MAIN_PICK)))
    ]
    uncovered = draws[~wins_against(draws, to_mask(chosen[0]))]

    while len(chosen) < n_tickets and len(uncovered):
        cands = _candidate_pool(chosen, pool_size, rng)
        scores = _score_candidates(cands, uncovered)
        pick_mask = int(cands[int(np.argmax(scores))])
        chosen.append(from_mask(pick_mask))
        uncovered = uncovered[~wins_against(uncovered, pick_mask)]

    while len(chosen) < n_tickets:      # already total cover; pad harmlessly
        chosen.append(tuple(sorted(rng.sample(range(1, MAIN_POOL + 1), MAIN_PICK))))

    for _ in range(passes):
        improved = False
        for i in range(len(chosen)):
            others = [t for j, t in enumerate(chosen) if j != i]
            covered_by_others = np.zeros(len(draws), dtype=bool)
            for t in others:
                covered_by_others |= wins_against(draws, to_mask(t))
            residual = draws[~covered_by_others]
            if not len(residual):
                continue

            current = int(
                np.count_nonzero(wins_against(residual, to_mask(chosen[i])))
            )
            cands = _candidate_pool(others, pool_size, rng)
            scores = _score_candidates(cands, residual)
            best_idx = int(np.argmax(scores))
            if scores[best_idx] > current:
                chosen[i] = from_mask(int(cands[best_idx]))
                improved = True
        if not improved:
            break

    return chosen


# --------------------------------------------------------------------------
# Reference baselines to compare a wheel against
# --------------------------------------------------------------------------


def naive_baseline(n_tickets: int, seed: int = 1) -> list[Ticket]:
    """What a player gets by just picking n random tips with no structure."""
    rng = random.Random(seed)
    return _random_tickets(n_tickets, rng)


def random_baseline_stats(
    n_tickets: int, replicates: int = 40, seed: int = 1
) -> dict[str, float]:
    """Average win probability of *unstructured* random tips.

    A single random sample is noisy enough to swamp the effect we are
    measuring, so the comparison baseline has to be an average over many
    independent sets rather than one draw of the dice.
    """
    rng = random.Random(seed)
    ps = [
        evaluate(_random_tickets(n_tickets, rng)).p_any_prize
        for _ in range(replicates)
    ]
    mean = sum(ps) / len(ps)
    sd = (
        (sum((p - mean) ** 2 for p in ps) / (len(ps) - 1)) ** 0.5
        if len(ps) > 1
        else 0.0
    )
    return {
        "mean": mean,
        "sd": sd,
        "min": min(ps),
        "max": max(ps),
        "replicates": replicates,
    }


def worst_case_baseline(n_tickets: int) -> list[Ticket]:
    """Maximally correlated tips -- the trap of 'nudging one number'.

    The first ``n`` 6-subsets in lexicographic order: 1-2-3-4-5-6, then
    1-2-3-4-5-7, and so on.  Consecutive tips differ by a single number, so
    they succeed and fail almost together -- the worst possible use of a
    budget, and precisely what a player does when they fill a slip by
    tweaking one digit per row.
    """
    if n_tickets > TOTAL_MAIN_COMBOS:
        raise ValueError("more tips requested than distinct combinations exist")
    return list(
        islice(combinations(range(1, MAIN_POOL + 1), MAIN_PICK), n_tickets)
    )
