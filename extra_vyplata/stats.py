"""Statistical tests on the historical archive.

The point of this module is *falsification*, not fortune telling.  Frequency
tables are the thing every lottery site publishes and every player
over-reads.  So the job here is to measure whether the observed spread of
"hot" and "cold" numbers is bigger than what a perfectly fair machine
produces by chance.  If it is not -- and it never is, in a sample this size
-- then past results carry no information about the next draw, and the only
honest levers left are the combinatorial ones in :mod:`coverage`.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from .game import MAIN_PICK, MAIN_POOL, EXTRA_POOL

# --------------------------------------------------------------------------
# Chi-square tail probability, without scipy
# --------------------------------------------------------------------------


def _gammln(x: float) -> float:
    return math.lgamma(x)


def _gser(a: float, x: float) -> float:
    """Lower regularized incomplete gamma P(a, x) via series expansion."""
    if x <= 0.0:
        return 0.0
    ap = a
    total = 1.0 / a
    delta = total
    for _ in range(1000):
        ap += 1.0
        delta *= x / ap
        total += delta
        if abs(delta) < abs(total) * 1e-15:
            break
    return total * math.exp(-x + a * math.log(x) - _gammln(a))


def _gcf(a: float, x: float) -> float:
    """Upper regularized incomplete gamma Q(a, x) via continued fraction."""
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return math.exp(-x + a * math.log(x) - _gammln(a)) * h


def chi2_sf(chi2: float, df: int) -> float:
    """P(X >= chi2) for a chi-square variable with ``df`` degrees of freedom."""
    if chi2 <= 0:
        return 1.0
    a, x = df / 2.0, chi2 / 2.0
    if x < a + 1.0:
        return 1.0 - _gser(a, x)
    return _gcf(a, x)


# --------------------------------------------------------------------------
# Uniformity of the drawn numbers
# --------------------------------------------------------------------------


@dataclass
class UniformityResult:
    counts: dict[int, int]
    expected: float
    chi2: float
    df: int
    p_value: float
    n_draws: int

    @property
    def hottest(self) -> list[tuple[int, int]]:
        return sorted(self.counts.items(), key=lambda kv: (-kv[1], kv[0]))

    @property
    def coldest(self) -> list[tuple[int, int]]:
        return sorted(self.counts.items(), key=lambda kv: (kv[1], kv[0]))

    def band_95(self) -> tuple[float, float]:
        """Roughly the range a fair machine keeps ~95% of counts inside.

        Each number's count is Binomial(n_draws, pick/pool); the normal
        approximation is good enough for an eyeball test.
        """
        p = self.expected / self.n_draws
        sd = math.sqrt(self.n_draws * p * (1 - p))
        return (self.expected - 1.96 * sd, self.expected + 1.96 * sd)


def main_number_uniformity(draws: list[tuple[int, ...]]) -> UniformityResult:
    counts = Counter()
    for nums in draws:
        counts.update(nums)
    for n in range(1, MAIN_POOL + 1):
        counts.setdefault(n, 0)

    n_draws = len(draws)
    expected = n_draws * MAIN_PICK / MAIN_POOL
    chi2 = sum((counts[n] - expected) ** 2 / expected for n in range(1, MAIN_POOL + 1))
    df = MAIN_POOL - 1
    return UniformityResult(
        counts=dict(sorted(counts.items())),
        expected=expected,
        chi2=chi2,
        df=df,
        p_value=chi2_sf(chi2, df),
        n_draws=n_draws,
    )


def extra_uniformity(extras: list[int]) -> UniformityResult:
    counts = Counter(extras)
    for n in range(1, EXTRA_POOL + 1):
        counts.setdefault(n, 0)

    n_draws = len(extras)
    expected = n_draws / EXTRA_POOL
    chi2 = sum((counts[n] - expected) ** 2 / expected for n in range(1, EXTRA_POOL + 1))
    df = EXTRA_POOL - 1
    return UniformityResult(
        counts=dict(sorted(counts.items())),
        expected=expected,
        chi2=chi2,
        df=df,
        p_value=chi2_sf(chi2, df),
        n_draws=n_draws,
    )


# --------------------------------------------------------------------------
# Shape statistics of the drawn six -- sum, parity, spacing, carry-over
# --------------------------------------------------------------------------


def sum_stats(draws: list[tuple[int, ...]]) -> dict[str, float]:
    sums = [sum(d) for d in draws]
    mean = sum(sums) / len(sums)
    var = sum((s - mean) ** 2 for s in sums) / (len(sums) - 1)

    # Exact moments of the sum of a 6-subset of 1..27 (sampling without
    # replacement from a finite population).
    pop = list(range(1, MAIN_POOL + 1))
    mu = sum(pop) / MAIN_POOL
    sigma2 = sum((x - mu) ** 2 for x in pop) / MAIN_POOL
    exp_mean = MAIN_PICK * mu
    fpc = (MAIN_POOL - MAIN_PICK) / (MAIN_POOL - 1)      # finite population correction
    exp_var = MAIN_PICK * sigma2 * fpc

    return {
        "observed_mean": mean,
        "expected_mean": exp_mean,
        "observed_sd": math.sqrt(var),
        "expected_sd": math.sqrt(exp_var),
        "observed_min": min(sums),
        "observed_max": max(sums),
    }


def odd_even_profile(draws: list[tuple[int, ...]]) -> dict[int, int]:
    """How many of the six drawn numbers were odd, tallied over the archive."""
    profile = Counter(sum(1 for n in d if n % 2) for d in draws)
    return {k: profile.get(k, 0) for k in range(MAIN_PICK + 1)}


def consecutive_pairs(draws: list[tuple[int, ...]]) -> dict[int, int]:
    """Number of adjacent pairs (like 14,15) inside each drawn set."""
    tally = Counter(
        sum(1 for a, b in zip(d, d[1:]) if b - a == 1) for d in draws
    )
    return {k: tally.get(k, 0) for k in range(MAIN_PICK)}


def carryover(draws: list[tuple[int, ...]]) -> dict[str, float]:
    """How many numbers repeat from one draw to the next.

    ``draws`` is newest-first, which does not matter for the statistic.
    Expected value under fairness is 6 * 6/27 = 1.333.
    """
    overlaps = [
        len(set(a) & set(b)) for a, b in zip(draws, draws[1:])
    ]
    expected = MAIN_PICK * MAIN_PICK / MAIN_POOL
    return {
        "observed_mean": sum(overlaps) / len(overlaps),
        "expected_mean": expected,
        "distribution": {k: overlaps.count(k) for k in range(MAIN_PICK + 1)},
        "n_transitions": len(overlaps),
    }


def repeated_full_sets(draws: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    """Any 6-set that has come up more than once (a curiosity, not a signal)."""
    seen = Counter(tuple(sorted(d)) for d in draws)
    return [s for s, c in seen.items() if c > 1]
