"""Historical EXTRA VYPLATA results.

Collected from the public result archives (bingoo.sk / 777.sk, cross-checked
against tipos.sk), last updated 2026-08-27.  Each entry is
(ISO date, 6 main numbers, powerball).

The game started drawing on 2026-01-05 (Mondays only); Thursday draws were
added on 2026-04-23.  This table covers the continuous run from 2026-03-30
to 2026-08-27 inclusive.
"""

from __future__ import annotations

Draw = tuple[str, tuple[int, int, int, int, int, int], int]

DRAWS: list[Draw] = [
    ("2026-08-27", (3, 8, 14, 17, 18, 19), 5),
    ("2026-08-24", (5, 8, 10, 11, 18, 24), 5),
    ("2026-08-20", (1, 10, 13, 15, 21, 24), 3),
    ("2026-08-17", (9, 13, 23, 24, 25, 26), 2),
    ("2026-08-13", (5, 11, 18, 20, 23, 24), 6),
    ("2026-08-10", (14, 15, 16, 24, 25, 27), 4),
    ("2026-08-06", (2, 7, 11, 12, 16, 19), 2),
    ("2026-08-03", (1, 4, 12, 18, 20, 24), 3),
    ("2026-07-30", (3, 10, 11, 22, 23, 27), 5),
    ("2026-07-27", (2, 3, 6, 15, 20, 26), 5),
    ("2026-07-23", (1, 3, 10, 11, 19, 26), 4),
    ("2026-07-20", (2, 9, 11, 15, 16, 18), 2),
    ("2026-07-16", (2, 6, 11, 12, 22, 24), 2),
    ("2026-07-13", (8, 12, 14, 16, 20, 22), 5),
    ("2026-07-09", (1, 4, 6, 9, 15, 24), 7),
    ("2026-07-06", (5, 7, 13, 24, 25, 26), 7),
    ("2026-07-02", (4, 7, 12, 18, 20, 22), 4),
    ("2026-06-29", (11, 14, 18, 21, 24, 25), 6),
    ("2026-06-25", (9, 13, 15, 16, 17, 19), 2),
    ("2026-06-22", (8, 14, 20, 21, 22, 24), 6),
    ("2026-06-18", (7, 10, 11, 12, 19, 20), 2),
    ("2026-06-15", (2, 9, 10, 19, 22, 23), 4),
    ("2026-06-11", (3, 7, 8, 16, 17, 21), 5),
    ("2026-06-08", (7, 10, 15, 18, 20, 23), 1),
    ("2026-06-04", (6, 13, 16, 17, 25, 26), 3),
    ("2026-06-01", (3, 6, 9, 20, 21, 25), 6),
    ("2026-05-28", (2, 6, 11, 14, 24, 25), 4),
    ("2026-05-25", (6, 10, 17, 18, 19, 26), 2),
    ("2026-05-21", (4, 6, 12, 17, 19, 20), 1),
    ("2026-05-18", (2, 4, 8, 23, 24, 25), 3),
    ("2026-05-14", (2, 6, 12, 17, 18, 20), 3),
    ("2026-05-11", (3, 6, 11, 14, 15, 23), 1),
    ("2026-05-07", (6, 15, 18, 22, 24, 25), 1),
    ("2026-05-04", (1, 6, 9, 14, 21, 27), 5),
    ("2026-04-30", (1, 4, 14, 19, 21, 25), 2),
    ("2026-04-27", (4, 6, 13, 15, 19, 24), 2),
    ("2026-04-23", (7, 10, 13, 17, 22, 23), 3),
    ("2026-04-20", (6, 7, 11, 19, 23, 27), 7),
    ("2026-04-13", (3, 7, 17, 23, 26, 27), 1),
    ("2026-04-06", (2, 7, 9, 15, 16, 25), 2),
    ("2026-03-30", (8, 9, 12, 17, 19, 26), 4),
]


def main_numbers() -> list[tuple[int, ...]]:
    return [d[1] for d in DRAWS]


def extras() -> list[int]:
    return [d[2] for d in DRAWS]


def sanity_check() -> None:
    """Fail loudly if the transcribed archive is malformed."""
    seen_dates = set()
    for date, nums, extra in DRAWS:
        if date in seen_dates:
            raise ValueError(f"duplicate draw date {date}")
        seen_dates.add(date)
        if len(nums) != 6 or len(set(nums)) != 6:
            raise ValueError(f"{date}: expected 6 distinct main numbers, got {nums}")
        if not all(1 <= n <= 27 for n in nums):
            raise ValueError(f"{date}: main number out of range in {nums}")
        if list(nums) != sorted(nums):
            raise ValueError(f"{date}: main numbers not sorted: {nums}")
        if not 1 <= extra <= 7:
            raise ValueError(f"{date}: powerball {extra} out of range")
