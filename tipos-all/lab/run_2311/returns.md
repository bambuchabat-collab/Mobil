# Returns and exact odds — target Monday 23.11.2026 (subagent 3)

Script: `lab/run_2311/scripts/returns.py` (python3 -I). All numbers: `returns.json`. No prediction: only prize arithmetic. Stake 2 × 1,50 € = 3 €.

## Sanity table (per draw, 3 € stake)

| Purchase | P(any prize) | Return per 1 € (6+1 PV 3 %) | 0 % / 5 % PV | low tiers only | € back on average |
|---|---|---|---|---|---|
| 2× EV, disjoint, normal month | 20.05 % | **0.491** | 0.511 / 0.480 | 0.311 ± 0.0002 | 1.47 € |
| 2× EV, disjoint, premium month | 20.05 % | **0.805** | 0.825 / 0.793 | 0.624 ± 0.0004 | 2.41 € |
| 2× VAN, 5 common | 16.71 % | **0.495** (rule, sharing) | realized 0.472 ± 0.025 | 0.314 | 1.48 € |
| 1 EV + 1 VAN (normal EV month) | 17.84 % | **0.493** | 0.503 (0 %) | — | 1.48 € |
| 1 EV + 1 VAN (premium EV month) | 17.84 % | **0.650** | 0.660 (0 %) | — | 1.95 € |

Player outcome spread (low tiers only, one draw): 2× EV SD ≈ 4.2 € (premium 8.5 €), 2× VAN SD ≈ 5.9 €. The mean is a long-run figure; a single draw is almost always 0 € or one small prize.

P(payout ≥ 4 €, i.e. more than the 3 € stake): 2× EV normal 4.88 %, premium 20.05 %; 2× VAN 2.24 %. EV 3+0 alone pays about the stake back in normal months (2026: mean 3.01 €, range 2.6–3.3 €); VAN 8/3 hits pay exactly 3 €.

## 1. Exact odds

EV one field: P(any) = 10.093 %; 6 main 1 : 296,010; 6+1 1 : 2,072,070; 5 main 1 : 2,349.

EV two fields, c common main numbers (extra numbers different / same):

| c | P(any) | P(≥5+0 either) | P(6 main either) | 6+1 either 1 : (extras diff / same) | P(a "+1" tier) diff / same | SD low € diff / same |
|---|---|---|---|---|---|---|
| 0 | 20.051 % | 0.0858 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 2.864 % | 4.25 / 4.25 |
| 1 | 19.545 % | 0.0858 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 2.792 % | 4.26 / 4.26 |
| 2 | 18.701 % | 0.0858 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 2.672 % | 4.31 / 4.32 |
| 3 | 17.593 % | 0.0858 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 2.513 % | 4.42 / 4.44 |
| 4 | 16.140 % | 0.0845 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 2.306 % | 4.64 / 4.68 |
| 5 | 13.944 % | 0.0767 % | 1 : 148,005 | 1,036,035 / 1,036,035 | 2.884 % / 1.992 % | 5.03 / 5.12 |
| 6 | 10.093 % | 0.0429 % | 1 : 296,010 | 1,036,035 / 2,072,070 | 2.884 % / 1.442 % | 5.89 / 6.07 |

- P(any) does not depend on the extra numbers (3+0 already pays); disjoint fields maximise it: 29677/148005 = 20.051 %. Different extra numbers only change the mix (more often a '+1' tier, lower SD); same main numbers with different extras keep the same 6+1 odds but halve the 6-main odds.

VAN two tickets, s common numbers:

| s | P(any) | P(≥20 €) | P(≥200 €) | top (11 or 0) 1 : |
|---|---|---|---|---|
| 0 | 8.611 % | 0.892 % | 0.0346 % | 352,716 |
| 1 | 12.693 % | 1.466 % | 0.0629 % | 176,358 |
| 2 | 14.408 % | 1.650 % | 0.0680 % | 176,358 |
| 3 | 15.551 % | 1.739 % | 0.0692 % | 176,358 |
| 4 | 16.321 % | 1.774 % | 0.0692 % | 176,358 |
| 5 | 16.711 % | 1.784 % | 0.0692 % | 176,358 |
| 6 | 16.711 % | 1.784 % | 0.0692 % | 176,358 |
| 7 | 16.321 % | 1.774 % | 0.0692 % | 176,358 |
| 8 | 15.551 % | 1.739 % | 0.0692 % | 176,358 |
| 9 | 14.408 % | 1.650 % | 0.0680 % | 176,358 |
| 10 | 12.693 % | 1.466 % | 0.0629 % | 176,358 |
| 11 | 8.611 % | 0.892 % | 0.0346 % | 352,716 |

Confirmed: s = 5 and 6 give the maximum 16.711 % (4912/29393). Mixed 1 EV + 1 VAN: P(any) = 17.835 % (independent games).

## 2. EV realized return of tiers 3+0…5+1 (share of stakes)

| Group | draws | bets/draw | mean | SD draw-to-draw | bootstrap SE | realized 6+1/6+0 (nominal) |
|---|---|---|---|---|---|---|
| 2024 to Sep (old rules: extra 1–4, no 3+1) | 28 | 208,661 | 0.2771 | 0.0013 | 0.0002 | 0.533 |
| 2024 Oct–Dec | 13 | 213,655 | 0.3097 | 0.0018 | 0.0005 | 0.158 |
| 2025 | 52 | 173,678 | 0.3103 | 0.0015 | 0.0002 | 0.159 |
| 2026 normal months | 60 | 99,395 | 0.3107 | 0.0017 | 0.0002 | 0.225 |
| 2026 normal, Mon | 38 | 107,108 | 0.3103 | 0.0017 | 0.0003 | 0.138 |
| 2026 normal, Thu | 22 | 86,072 | 0.3115 | 0.0015 | 0.0003 | 0.412 |
| 2026 premium (May, Oct) | 17 | 105,881 | 0.6243 | 0.0016 | 0.0004 | 0.422 |
| premium, Mon | 8 | 111,576 | 0.6246 | 0.0014 | 0.0005 | 0.426 |
| premium, Thu | 9 | 100,820 | 0.6241 | 0.0019 | 0.0006 | 0.419 |

By rule: 0,579 × 0,542 = 0.3138 (normal), ×2 = 0.6276 (premium). Low-tier share is almost deterministic (SD ≈ 0,002): the pool is parimutuel, so only top tiers and personal luck vary. Only May and Oct 2026 show doubled tiers (auto-detected, matches the decisions).

Top tiers (current plan, Monday bets ≈ 104,818 = mean of last 8 Mondays):

| 6+1 PV rate | PV factor (120 monthly) | 6+1 per 1 € | 6+0 per 1 € | top per 1 € |
|---|---|---|---|---|
| 0% | 1.0000 | 0.1506 | 0.0499 | 0.2006 |
| 3% | 0.8647 | 0.1302 | 0.0499 | 0.1802 |
| 5% | 0.7897 | 0.1190 | 0.0499 | 0.1689 |

Sharing factors at 104,818 bets: 6+1 ×0.975 (λ = 0.051), 6+0 ×0.862 (λ = 0.304). Yearly instead of monthly instalments: PV 3 % 0.853, 5 % 0.772. Top-tier return vs bets (3 %): 60k → 0.185, 80k → 0.183, 100k → 0.181, 120k → 0.179, 200k → 0.171.

## 2b. VAN return per 1 €

- By rule: low tiers 0.3145 + top 0.1890 = 0.5035; with sharing (Monday ≈ 33,129 bets, λ = 0.094, factor 0.954) = **0.4949**.
- All 410 draws (2025-10-06…2026-11-22, 46,481 bets/draw): realized 0.4720 ± 0.025 (low 0.3145, top 0.1574; top winners 46 vs 54.0 expected, p = 0.15); with the 13.11 premium codes 0.4723.
- Last 3 months (2026-08-23…2026-11-22, 32,790 bets/draw): realized 0.4959 ± 0.063 (low 0.3191, top 0.1768; top winners 8 vs 8.6 expected, p = 0.52); with the 13.11 premium codes 0.4981.

## 3. Checks on the tier counts

- Since 07.10.2024 deposits/1,5 is the right column count: low-tier winners / expected = 5+1 0.997, 5+0 1.000, 4+1 0.996, 4+0 1.000, 3+1 0.997, 3+0 1.004; bets from tier counts / (deposits/1,5) = 1.0023.
- Before Oct 2024 the extra drum had 1–4 (drawn extra numbers only 1–4; with 1/7 the '+1' tiers look ×1.83, with 1/4 they fit: 4+1 1.048, 4+0 1.014). So the naive 1/7 expectation for 2024 is wrong.
- 6+1: 19 winners vs 12.3 (naive 1/7, p = 0.045) but 14.4 with correct 2024 rules (p = 0.14); since Oct 2024: 9 vs 9.4 (normal).
- 6+0: 89 vs 71.5 (correct rules, Poisson p = 0.025); since Oct 2024 71 vs 56.7 (p = 0.037). But winners come in clusters (2–3 per draw; low tiers have dispersion index 2.96–11.72 ≫ 1), so plain Poisson overstates significance. Draws with ≥1 6+0 winner since Oct 2024: 55 vs 45.9 expected (p = 0.06) → chance, nothing to exploit.
- Old 2024 payouts: 6+1 480 000 € for 1–2 winners, 320 000 € ×3 (cap 960 000 €); 6+0 24 000 € (48 000 € cap in spring, 12 000 € each in Sep 2024). Current plan (from 18.03.2026): 2 winners get 240 000 € each, ≥3 share 720 000 €; 6+0 shares 30 000 €.

## Assumptions

- 6+1 is paid in 120 monthly instalments (480 000 € → 4 000 €/month); no lump-sum option unless ≥7 winners. PV uses annuity-immediate; 3 % is the headline rate.
- Co-winners ~ Poisson with uniform number choice (bets = mean of last 8 Mondays). Unpopular numbers would only raise the top-tier value a bit; not modelled here.
- Low tiers use the realized 2026 share (normal or premium months); the same number holds for Monday and Thursday.
- VAN: fixed prizes, 100 000 € shared by all 11-or-0 winners; premium codes (13.11.2026, 10 × 1 000 €) are a one-off and excluded from the headline.
- Tax: lottery winnings from games operated under the Slovak gambling act are fully tax-exempt (§ 9 ods. 2 písm. l) zákona 595/2003; Finančná správa FAQ).
- November/December 2026: no assumption on premium here — both columns are given.
