#!/usr/bin/env python3
"""LOTO 5 z 35 -- optimal use of a EUR 3.00 budget (exactly 5 tips).

Unlike EXTRA VYPLATA, this game has a *provable* optimum rather than a
best-found-by-search one.  See section 2: because two disjoint tips can never
be paid by the same draw, the union bound is attained exactly, so no cleverer
set exists and no search is necessary.
"""

from __future__ import annotations

import random
from itertools import combinations

import lotto_engine as le

SPEC = le.LOTO_5_Z_35
BUDGET = 3.00
SEP = "=" * 70

# Payouts observed in a recent draw; tiers 1-2 are pari-mutuel and move.
JACKPOT_TODAY = 20_000.00
TIER4_REFERENCE = 386.70
TIER3_FIXED = 3.60


def section(t: str) -> None:
    print(f"\n{SEP}\n{t}\n{SEP}")


def main() -> None:
    s = SPEC
    n = round(BUDGET / s.tip_price)

    section("1. ТОЧНЫЕ ШАНСЫ")
    print(f"{s.name}: {s.pick} из {s.pool}, ставка EUR {s.tip_price:.2f}")
    print(f"C({s.pool},{s.pick}) = {s.total_draws:,} равновероятных тиражей\n")
    for k in range(s.pick, -1, -1):
        c = s.hit_combos(k)
        pays = "выигрыш" if k >= s.min_hits else "—"
        print(f"  {k} совпад.: {c:>7,}  p={c/s.total_draws:.8f}  "
              f"1 к {s.total_draws/c:>9,.1f}   {pays}")
    print(f"\nP(хоть что-то) = {s.draws_won_by_one_tip():,}/{s.total_draws:,} "
          f"= {s.p_any_prize():.6%}  (1 к {1/s.p_any_prize():.1f})")
    print(f"P(джекпот)     = 1 к {s.total_draws:,}")

    section("2. ПОЧЕМУ ОПТИМУМ ЗДЕСЬ ДОКАЗУЕМ, А НЕ НАЙДЕН ПЕРЕБОРОМ")
    print(f"Чтобы две ставки выиграли в одном тираже, каждой нужно {s.min_hits}")
    print(f"совпадений. Если ставки не пересекаются, эти совпадения — разные")
    print(f"числа, значит нужно {2*s.min_hits} выпавших чисел. А выпадает {s.pick}.")
    print(f"  {2*s.min_hits} > {s.pick}  =>  непересекающиеся ставки НЕ МОГУТ выиграть вместе.")
    print(f"\nСобытия взаимоисключающие => вероятности складываются точно:")
    print(f"  P(объединение) = {n} x {s.p_any_prize():.8f} = {n*s.p_any_prize():.8f}")
    print(f"Union bound — потолок, который не может превысить НИ ОДИН набор.")
    print(f"Непересекающийся набор достигает его точно => это оптимум.")
    print(f"(в пул из {s.pool} чисел влезает до {le.max_disjoint_tickets(s)} "
          f"непересекающихся ставок)")

    section(f"3. НАБОР НА EUR {BUDGET:.2f} ({n} СТАВОК)")
    # Отбрасываем 10 самых «народных» низких чисел: в пуле 1..35 числа 32..35
    # вообще вне диапазона дней месяца, а 1..10 выбирают чаще всего.
    rng = random.Random(20260823)
    high = list(range(11, s.pool + 1))          # 25 чисел = ровно 5 ставок
    rng.shuffle(high)
    tickets = [tuple(sorted(high[i * s.pick:(i + 1) * s.pick])) for i in range(n)]

    for i, t in enumerate(tickets, 1):
        print(f"  ставка {i}:  {'  '.join(f'{x:02d}' for x in t)}")

    e = le.evaluate(tickets, s)
    print(f"\nстоимость              : EUR {e.cost_eur:.2f}")
    print(f"P(выиграть хоть что-то): {e.p_any_prize:.6%}   (1 к {e.odds_one_in:.2f})")
    print(f"события взаимоисключающие: {e.disjoint_events}")
    print(f"достигнут union bound  : {e.covered == n * s.draws_won_by_one_tip()}")
    print(f"P(джекпот)             : {n}/{s.total_draws:,} = 1 к {s.total_draws/n:,.0f}")

    section("4. СРАВНЕНИЕ")
    rnd = le.random_baseline_stats(n, s, replicates=200, seed=42)
    bad = le.evaluate(le.worst_case_baseline(n, s), s)
    print(f"  оптимально (непересек.) : {e.p_any_prize:.6%}")
    print(f"  случайные {n} ставок      : {rnd['mean']:.6%}  (sd {rnd['sd']:.4%})")
    print(f"  худший случай           : {bad.p_any_prize:.6%}")
    print(f"\nВыигрыш структуры мал ({e.p_any_prize/rnd['mean']:.3f}x), и это честно:")
    print("в 5 из 35 ставки и так почти не пересекаются случайно.")
    print("Главное здесь — не переплатить за ошибку (худший случай теряет "
          f"{(1-bad.p_any_prize/e.p_any_prize)*100:.0f}%).")

    section("5. МАТОЖИДАНИЕ")
    p3 = s.hit_combos(3) / s.total_draws
    p4 = s.hit_combos(4) / s.total_draws
    p5 = s.hit_combos(5) / s.total_draws
    ev = p3 * TIER3_FIXED + p4 * TIER4_REFERENCE + p5 * JACKPOT_TODAY
    print(f"  3 числа (фикс. EUR {TIER3_FIXED:.2f}) : EUR {p3*TIER3_FIXED:.4f}")
    print(f"  4 числа (~EUR {TIER4_REFERENCE:.2f})    : EUR {p4*TIER4_REFERENCE:.4f}")
    print(f"  5 чисел (джекпот {JACKPOT_TODAY:,.0f}): EUR {p5*JACKPOT_TODAY:.4f}")
    print(f"  ИТОГО на ставку EUR {s.tip_price:.2f} : EUR {ev:.4f}  ->  RTP ~ {ev/s.tip_price:.1%}")
    print(f"  на весь бюджет EUR {BUDGET:.2f}   : EUR {ev*n:.2f}")
    print("\n  (тиражи 1-2 тотализаторные — оценка, а не гарантия)")

    section("6. ЧТО ЗДЕСЬ НЕВОЗМОЖНО")
    lb = le.guaranteed_wheel_lower_bound(s)
    print(f"Гарантировать выигрыш: нужно >= {lb} ставок (>= EUR {lb*s.tip_price:.2f}),")
    print(f"и это лишь нижняя граница — реально заметно больше. За EUR {BUDGET:.2f}")
    print("гарантии не существует.")
    print(f"\nПредсказать джекпот: невозможно. Все {s.total_draws:,} комбинаций")
    print(f"равновероятны; {n} ставок дают ровно {n} шансов из {s.total_draws:,}.")


if __name__ == "__main__":
    main()
