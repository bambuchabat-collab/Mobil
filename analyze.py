#!/usr/bin/env python3
"""Full analysis run for the EXTRA VYPLATA draw of 2026-08-17.

Usage:
    python3 analyze.py [--out results.json] [--quick]

Everything printed here is either exact combinatorics over the complete
296,010-draw space or a stated estimate.  Nothing is simulated and nothing
is predicted.
"""

from __future__ import annotations

import argparse
import json
import time

from extra_vyplata import coverage as cv
from extra_vyplata import data, game, outcome, stats

TARGET_DRAW = "2026-08-17"
SEP = "=" * 72


def section(title: str) -> None:
    print(f"\n{SEP}\n{title}\n{SEP}")


# --------------------------------------------------------------------------


def report_game(results: dict) -> None:
    section("1. GAME STRUCTURE AND EXACT ODDS")
    print(
        f"Pick {game.MAIN_PICK} of {game.MAIN_POOL} main numbers "
        f"+ 1 of {game.EXTRA_POOL} powerball."
    )
    print(
        f"{game.TOTAL_MAIN_COMBOS:,} main combinations "
        f"x {game.EXTRA_POOL} = {game.TOTAL_OUTCOMES:,} equally likely outcomes."
    )
    print(f"One tip costs EUR {float(game.TIP_PRICE):.2f}; a slip of 8 costs "
          f"EUR {float(game.SLIP_PRICE):.2f}.\n")

    print(f"{'tier':>5} {'match':>6} {'outcomes':>9} {'probability':>13} {'odds':>16}")
    tiers = []
    for t in game.TIERS:
        p = float(t.probability)
        print(
            f"{t.rank:>5} {t.label:>6} {t.combos:>9,} {p:>13.9f} "
            f"{'1 in ' + format(t.odds_one_in, ',.1f'):>16}"
        )
        tiers.append(
            {
                "rank": t.rank,
                "label": t.label,
                "outcomes": t.combos,
                "probability": p,
                "odds_one_in": t.odds_one_in,
                "fixed_eur": t.fixed_eur,
            }
        )

    p_any = game.p_any_prize()
    print(
        f"\nAny prize at all needs >= {game.MIN_PAYING_HITS} main numbers "
        f"(the powerball never pays on its own):"
    )
    print(
        f"  P(any prize) = {p_any} = {float(p_any):.6%}  ->  1 in "
        f"{1 / float(p_any):.3f} tips"
    )
    print(
        f"  {game.draws_won_by_one_tip():,} of the {game.TOTAL_MAIN_COMBOS:,} "
        f"possible draws pay any given tip."
    )
    results["game"] = {
        "tiers": tiers,
        "p_any_prize": float(p_any),
        "p_any_prize_exact": str(p_any),
        "draws_won_by_one_tip": game.draws_won_by_one_tip(),
        "total_main_combos": game.TOTAL_MAIN_COMBOS,
        "total_outcomes": game.TOTAL_OUTCOMES,
    }


def report_ev(results: dict) -> None:
    section("2. EXPECTED VALUE (what the ticket is actually worth)")
    ev = game.expected_value_per_tip()
    print(f"Calibrated on the draw of {game.REFERENCE_DRAW['date']} "
          f"(pari-mutuel tiers move every draw).")
    print(f"  implied tips sold that draw : {ev['tips_sold_estimate']:>12,.0f}")
    print(f"  EV from fixed tiers (6+1,6) : EUR {ev['fixed_tiers_ev']:>8.4f}")
    print(f"  EV from pari-mutuel tiers   : EUR {ev['pari_mutuel_ev']:>8.4f}")
    print(f"  total EV per EUR 1.50 tip   : EUR {ev['total_ev']:>8.4f}")
    print(f"  return to player            : {ev['rtp']:>11.1%}")
    print(f"  house edge                  : {ev['house_edge']:>11.1%}")
    print(
        "\nNo selection method changes this number. Every strategy below "
        "redistributes\nprobability; none of them creates value."
    )
    results["expected_value"] = ev


def report_stats(results: dict) -> None:
    section("3. IS THERE ANY EXPLOITABLE BIAS IN PAST DRAWS?")
    data.sanity_check()
    draws = data.main_numbers()
    print(f"Archive: {len(draws)} draws, {data.DRAWS[-1][0]} .. {data.DRAWS[0][0]}\n")

    uni = stats.main_number_uniformity(draws)
    lo, hi = uni.band_95()
    print(f"Main numbers 1..27, expected {uni.expected:.2f} appearances each")
    print(f"  95% band for a fair machine: {lo:.1f} .. {hi:.1f}")
    print("  counts:", " ".join(f"{n}:{c}" for n, c in uni.counts.items()))
    print(f"  hottest: {uni.hottest[:5]}")
    print(f"  coldest: {uni.coldest[:5]}")
    print(f"  chi-square = {uni.chi2:.2f} on {uni.df} df  ->  p = {uni.p_value:.3f}")

    ext = stats.extra_uniformity(data.extras())
    print(f"\nPowerball 1..7, expected {ext.expected:.2f} each")
    print("  counts:", dict(ext.counts))
    print(f"  chi-square = {ext.chi2:.2f} on {ext.df} df  ->  p = {ext.p_value:.3f}")

    ss = stats.sum_stats(draws)
    print(
        f"\nSum of the six drawn numbers: observed mean {ss['observed_mean']:.1f} "
        f"(theory {ss['expected_mean']:.1f}), "
        f"sd {ss['observed_sd']:.1f} (theory {ss['expected_sd']:.1f})"
    )
    co = stats.carryover(draws)
    print(
        f"Numbers repeating from the previous draw: mean "
        f"{co['observed_mean']:.2f} (theory {co['expected_mean']:.2f}) "
        f"over {co['n_transitions']} transitions"
    )
    print(f"Odd-count profile (how many of the 6 were odd): {stats.odd_even_profile(draws)}")
    print(f"Adjacent pairs per draw: {stats.consecutive_pairs(draws)}")
    repeats = stats.repeated_full_sets(draws)
    print(f"Exactly repeated 6-number sets: {repeats if repeats else 'none'}")

    verdict = (
        "Both chi-square tests are consistent with a fair machine. There is no "
        "hot/cold\nsignal to exploit: the observed spread is what randomness "
        "looks like at this\nsample size. Past numbers must be treated as "
        "irrelevant to 2026-08-17."
    )
    print(f"\nVERDICT:\n{verdict}")

    results["statistics"] = {
        "n_draws": len(draws),
        "main_counts": uni.counts,
        "main_chi2": uni.chi2,
        "main_df": uni.df,
        "main_p_value": uni.p_value,
        "main_expected_per_number": uni.expected,
        "main_95_band": [lo, hi],
        "extra_counts": ext.counts,
        "extra_chi2": ext.chi2,
        "extra_df": ext.df,
        "extra_p_value": ext.p_value,
        "sum_stats": ss,
        "carryover": co,
        "odd_even_profile": stats.odd_even_profile(draws),
        "consecutive_pairs": stats.consecutive_pairs(draws),
        "repeated_sets": [list(r) for r in repeats],
    }


def report_coverage(
    results: dict, budgets: list[int], pool: int, passes: int, replicates: int
) -> dict:
    section("4. HOW MANY TIPS BUY HOW MUCH CHANCE OF WINNING SOMETHING")
    print("Every tip has the same 10.0932% chance on its own. The only lever is")
    print("overlap between tips. Exact figures, swept over all 296,010 draws.\n")
    print("'random' is the mean over independent unstructured sets, +- its sd.\n")
    print(
        f"{'tips':>5} {'cost':>8} {'optimised':>11} {'random (mean+-sd)':>21} "
        f"{'worst':>9} {'gain':>8}"
    )

    rows = []
    best_sets: dict[int, list] = {}
    for n in budgets:
        opt = cv.optimize_budget(n, pool_size=pool, passes=passes, seed=20260817)
        e_opt = cv.evaluate(opt)
        rnd = cv.random_baseline_stats(n, replicates=replicates, seed=n * 101 + 5)
        e_bad = cv.evaluate(cv.worst_case_baseline(n))
        gain = e_opt.p_any_prize - rnd["mean"]
        print(
            f"{n:>5} {e_opt.cost_eur:>7.2f}E {e_opt.p_any_prize:>10.4%} "
            f"{rnd['mean']:>13.4%} +-{rnd['sd']:>5.2%} "
            f"{e_bad.p_any_prize:>8.4%} {gain:>+7.2%}"
        )
        best_sets[n] = opt
        rows.append(
            {
                "tips": n,
                "cost_eur": e_opt.cost_eur,
                "optimised": e_opt.p_any_prize,
                "random_mean": rnd["mean"],
                "random_sd": rnd["sd"],
                "random_min": rnd["min"],
                "random_max": rnd["max"],
                "worst_case": e_bad.p_any_prize,
                "optimised_tickets": [list(t) for t in opt],
                "expected_winning_tips": e_opt.expected_winning_tips,
                "overlap_profile": cv.pairwise_overlap_penalty(opt),
            }
        )

    results["coverage_curve"] = rows
    return best_sets


def report_slip(results: dict, tickets: list, label: str) -> None:
    section(f"5. RECOMMENDED SLIP -- {label}")
    n = len(tickets)
    pbs = outcome.spread_powerballs(n)
    print(f"{'#':>3}  {'main numbers':<26} {'powerball':>9}")
    for i, (t, pb) in enumerate(zip(tickets, pbs), 1):
        print(f"{i:>3}  {'-'.join(f'{x:02d}' for x in t):<26} {pb:>9}")

    ev = cv.evaluate(tickets)
    print(f"\ncost                       : EUR {ev.cost_eur:.2f}")
    print(f"P(at least one prize)      : {ev.p_any_prize:.4%}  (1 in {ev.odds_one_in:.2f})")
    print(f"expected number of paid tips: {ev.expected_winning_tips:.4f}")
    print(f"pair overlap profile       : {cv.pairwise_overlap_penalty(tickets)}")
    print("  (0 = the two tips share no number; keeping this concentrated on 0/1")
    print("   is exactly what pushes the win probability up)")

    print("\nBest-tier distribution, powerball spread 1..7 across the tips:")
    so = outcome.slip_outcome(tickets, pbs)
    for lab, p in so.tier_probability.items():
        if p:
            print(f"    {lab:>4} : {p:>12.8%}   1 in {1/p:>12,.0f}")
    print(f"    none : {1 - so.p_any_prize:>12.8%}")

    cmp_ = outcome.compare_powerball_strategies(tickets)
    print("\nPowerball placement (main numbers unchanged):")
    for name, res in cmp_.items():
        print(
            f"    {name:<13} P(any prize)={res.p_any_prize:.4%}   "
            f"P(a '+1' tier)={res.p_plus_one_tier:.4%}"
        )
    print("    -> P(any prize) is identical: the powerball cannot win on its own.")
    print("       Spreading it raises the chance of reaching a '+1' tier.")

    results.setdefault("slips", {})[label] = {
        "tickets": [list(t) for t in tickets],
        "powerballs": pbs,
        "cost_eur": ev.cost_eur,
        "p_any_prize": ev.p_any_prize,
        "expected_winning_tips": ev.expected_winning_tips,
        "tier_probability": so.tier_probability,
        "overlap_profile": cv.pairwise_overlap_penalty(tickets),
        "powerball_comparison": {
            k: {"p_any_prize": v.p_any_prize, "p_plus_one": v.p_plus_one_tier}
            for k, v in cmp_.items()
        },
    }


def report_guarantee(results: dict, pool: int, restarts: int) -> list:
    section("6. THE GUARANTEED WHEEL -- winning something with certainty")
    lb = cv.lower_bound_tickets()
    print(f"Counting bound: one tip pays on {game.draws_won_by_one_tip():,} of the")
    print(f"{game.TOTAL_MAIN_COMBOS:,} draws, so no wheel below {lb} tips can cover")
    print("every draw. Tips cannot overlap that little in practice, so the real")
    print("minimum is higher; below is the smallest wheel this search found.\n")

    t0 = time.time()
    wheel = cv.build_guaranteed_wheel(pool_size=pool, restarts=restarts)
    ev = cv.evaluate(wheel)
    print(f"wheel size          : {len(wheel)} tips  (search took {time.time()-t0:.0f}s)")
    print(f"cost                : EUR {ev.cost_eur:.2f}")
    print(f"coverage            : {ev.covered:,}/{ev.total:,} draws = {ev.p_any_prize:.4%}")
    print(f"VERIFIED GUARANTEED : {ev.guaranteed}")
    print(f"expected paid tips  : {ev.expected_winning_tips:.3f}")
    print("\ntips:")
    for i, t in enumerate(wheel, 1):
        print(f"  {i:>3}  {'-'.join(f'{x:02d}' for x in t)}")

    worst_prize = 3.00
    print(f"\nHonest arithmetic: the guarantee is only the bottom tier. Cost "
          f"EUR {ev.cost_eur:.2f},")
    print(f"guaranteed return about EUR {worst_prize:.2f}. The wheel converts a "
          f"chance of")
    print("winning nothing into a certainty of winning a little, at a large "
          "premium.")
    print("It is a demonstration of what 'guaranteed' really costs, not advice "
          "to buy it.")

    results["guaranteed_wheel"] = {
        "size": len(wheel),
        "cost_eur": ev.cost_eur,
        "tickets": [list(t) for t in wheel],
        "verified_full_cover": ev.guaranteed,
        "counting_lower_bound": lb,
        "expected_winning_tips": ev.expected_winning_tips,
        "overlap_profile": cv.pairwise_overlap_penalty(wheel),
    }
    return wheel


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results.json")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    pool = 300 if args.quick else 900
    passes = 2 if args.quick else 4
    restarts = 2 if args.quick else 10
    replicates = 10 if args.quick else 40
    wheel_pool = 600 if args.quick else 2000
    budgets = [1, 2, 4, 8] if args.quick else [1, 2, 3, 4, 5, 6, 7, 8, 12, 16, 24, 32]

    results: dict = {"target_draw": TARGET_DRAW, "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}

    print(SEP)
    print(f"EXTRA VYPLATA (TIPOS) -- analysis for the draw of {TARGET_DRAW}")
    print(SEP)

    report_game(results)
    report_ev(results)
    report_stats(results)
    best_sets = report_coverage(results, budgets, pool, passes, replicates)
    report_slip(results, best_sets[8], "one bet slip (8 tips, EUR 12.00)")
    if not args.quick:
        report_slip(results, best_sets[16], "two bet slips (16 tips, EUR 24.00)")
    report_guarantee(results, wheel_pool, restarts)

    section("7. BOTTOM LINE")
    p1 = results["game"]["p_any_prize"]
    slip = results["slips"]["one bet slip (8 tips, EUR 12.00)"]
    row8 = next(r for r in results["coverage_curve"] if r["tips"] == 8)
    print(f"* One tip, any numbers whatsoever : {p1:.4%} chance of a prize.")
    print(f"* Eight tips picked at random     : {row8['random_mean']:.4%}"
          f" (average, sd {row8['random_sd']:.2%})")
    print(f"* Eight tips, optimally spread    : {slip['p_any_prize']:.4%}"
          f"  <- the recommendation")
    print(f"* Eight tips, one number nudged   : "
          f"{row8['worst_case']:.4%}  <- the common mistake")
    print(f"* Guaranteed prize                : "
          f"{results['guaranteed_wheel']['size']} tips, "
          f"EUR {results['guaranteed_wheel']['cost_eur']:.2f}")
    print(f"\nExpected return stays at "
          f"{results['expected_value']['rtp']:.0%} of stake in every one of these "
          f"cases.")

    with open(args.out, "w") as fh:
        json.dump(results, fh, indent=2, default=str)
    print(f"\nMachine-readable results written to {args.out}")


if __name__ == "__main__":
    main()
