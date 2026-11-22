# Subagent 5 "New ideas" — pre-registration

Written (UTC): 2026-11-22T23:32:15Z — before any test statistic was computed.
Only data *structure* was inspected beforehand (tier keys per era, extra-number range, day labels, premium field = always null).
Data: `data/ev.json` sha256 d2aff931…f7f43e (170 EV draws, 2024-03-25..2026-11-19; 28 "old-era" draws to 2024-09-30 with
extra number 1–4 and no 3+1 tier, then 142 "new-era" draws with extra 1–7; Thursdays from 2026-04-23, 31 draws);
`data/van.json` sha256 8d367f7d…c39ef58c3f (410 VAN draws 2025-10-06..2026-11-22).

Rules source (read before writing this, WebFetch of tipos.sk herný plán text version, čl. 29 and 34):
EV tiers 3–8 (5+1,5+0,4+1,4+0,3+1,3+0) are pure pari-mutuel: 1.5/4.3/4.4/10.8/6.2/27.0 % of the prize fund
(57.90 % of stakes), shared equally, rounded down to 0.10 €, **no minimum prize**; 6+1 (480 000 €) and 6+0 (30 000 €)
are fixed pools **shared** among winners. VAN tiers 10/1 (200 €), 9/2 (20 €), 8/3 (3 €) are **fixed per winner
regardless of the number of winners**; only the 100 000 € (11 or 0 hits) is shared.
Consequence fixed in advance: in VAN, ticket popularity can matter only through the 100 000 € share. Its EV is
100 000·2/705 432 = 0.2835 € per 1.50 € ticket; a random ticket expects λ = bets·2/705 432 ≈ 0.13 co-winners, so even
a ticket nobody else plays gains at most 1 − (1−e^{−λ})/λ ≈ 6 % of that, i.e. **≤ 1.2 pp of stake**.

## Common definitions (EV)

* `bets_t = deposits_t / 1.5`. Responses: `y3_t = log((n(3+0)+n(3+1)) / bets_t)`, `y4_t = log((n(4+0)+n(4+1)) / bets_t)`
  (missing tier = 0 winners).
* Covariates always present (unpenalised): intercept, old-era indicator (no 3+1 tier), Thursday indicator, premium
  indicator, `log(bets_t) − log(1e5)`. Premium draw (definitional, not a hypothesis) = draw whose tier 3–8 payout
  Σ prize·winners / deposits > 0.45 (normal ≈ 0.31, doubled ≈ 0.62).
* Baseline M0 = covariates + 27 drawn-number indicators, ridge λ = 2 (value taken from earlier C1, not tuned here);
  unpenalised columns get 1e-8. Pattern features: unpenalised (1e-8). Interaction blocks (H7, H8): ridge λ = 4.
  Same design for y3 and y4 (fitted separately).
* Walk-forward: draws in date order t = 0..169; burn-in t < 40 (covers the whole old era); for every t = 40..169
  (130 draws) both models are fitted on draws < t only and predict y3_t, y4_t. Pattern features that use history
  (H4) use only draws < t.
* Test statistic for an EV hypothesis with feature set F: `T = Σ_{r∈{y3,y4}} (MSE_r(M0) − MSE_r(M0+F)) / MSE_r(M0)`
  (relative out-of-sample MSE improvement summed over the two responses). If a hypothesis has several alternative
  features (H2, H4, H6), each is added alone and `T = max` over them (max-T handles the internal multiplicity).
* p-value: Freedman–Lane residual permutation. Fit the reduced model on all 170 draws, take fitted values and
  residuals (y3,y4 jointly), permute residual rows within era strata (old/new), add back, re-run the *entire*
  walk-forward for both models, recompute T. R = 1999, `p = (1 + #{T* ≥ T}) / (R + 1)`; seed = 20261123 + hypothesis
  number (numpy default_rng).

## Hypotheses (family of k = 10, Holm–Bonferroni, FWER α = 0.05)

| id | idea | feature(s) added to the reduced model | reduced model |
|---|---|---|---|
| H1 | EV players avoid/seek consecutive numbers | # pairs (i, i+1) in the draw | M0 |
| H2 | bet-slip geometry (layout unknown → generic row-major grids with w = 5, 6, 7, 9, 10 columns) | # same-row pairs, # same-column pairs, one feature at a time (10 features, max-T) | M0 + consecutive pairs |
| H3 | "month/birthday pickers" cluster in 1–12 (non-linear, linear part is absorbed by per-number terms) | C(m,2), m = #drawn numbers ≤ 12 | M0 |
| H4 | players copy recent results (time-varying popularity) | (a) overlap with previous draw; (b) overlap with the latest earlier draw that had a 6+0 or 6+1 winner; (c) overlap with the 6 most frequent numbers in the last 10 draws (ties → smaller number) — max-T | M0 |
| H5 | players spread their picks; clustered draws have fewer winners | SD of the 6 drawn numbers | M0 |
| H6 | pattern pickers (arithmetic sequences, multiples of 5) | (a) # 3-term arithmetic progressions in the draw; (b) C(m5,2), m5 = #drawn in {5,10,15,20,25} — max-T | M0 |
| H7 | Thursday population has a different per-number popularity profile | 27 indicators × Thursday (ridge λ=4) | M0 |
| H8 | premium-month population has a different profile | 27 indicators × premium (ridge λ=4) | M0 |
| H9 | VAN: pattern tickets are over-played (visible in the fixed tiers' winner counts) | see below | — |
| H10 | EV main–extra coupling: players pick an extra number that is also among their main numbers | 1[drawn extra ∈ drawn main]; responses u3 = log(n(3+1)/n(3+0)), u4 = log(n(4+1)/n(4+0)) | intercept + Thursday + premium + 7 extra-number dummies (ridge λ=2) |

H10 details: new-era draws only (142); burn-in = first 30 new-era draws, evaluate the remaining 112; same T and
Freedman–Lane permutation (no strata), counts of 0 replaced by 0.5.

H9 details (VAN): per draw t and tier h ∈ {0,1,2,3,8,9,10,11}: `E_{t,h} = bets_t · C(11,h)C(11,11−h)/C(22,11)`.
Pattern list (14 sets of 11): the 12 contiguous windows {k..k+10}, k = 1..12, odds, evens. A pattern P "hits"
cell (t,h) if |D_t ∩ P| = h with h in the list (its players land in that tier). Statistic = inverse-variance
estimate of excess players per pattern: `m̂ = Σ_cells (n−E)/E / Σ_cells 1/E` over all hit cells (a cell hit by j
patterns counts j times). Null: the same statistic for 14 uniformly random 11-subsets (independent per replicate),
R = 9999, seed 20261132, `p = (1 + #{m̂* ≥ m̂}) / (R + 1)` (one-sided: over-played). This null automatically absorbs
over-dispersion and any mis-calibration of `bets`.

## Practical relevance (decided now)

A hypothesis is a *finding* only if Holm-adjusted p < 0.05 **and** its money effect is ≥ 0.5 pp of expected return
per 1 € staked (normal month) **and** it changes the recommended ticket.
Money effect (EV, H1–H8, H10): fit full and reduced models on all 170 draws. Expected return of tiers 3–8 per 1 € =
Σ_tiers s_k · E[exp(−f_k(D)) | field wins tier k] where s_k = tier share × 0.579 and f_k is the model's popularity
log-factor normalised so that E_uniform D[exp(f_k)] = 1 (tier 3 uses the y3 model, tiers 4 and 5 use the y4 model;
exact enumeration of D given the field). Two disjoint fields; optimise each model's best pair by local search
(swaps, 5 random restarts, seed fixed); effect = R_full(best_full) − R_full(best_reduced). Fixed tiers 6+1/6+0 are
left out (λ small; same for both). For H10 the effect is computed on the +1 tiers with the coupling term.
H9: by the bound above it cannot reach 0.5 pp for a random-looking ticket; it is reported for completeness and
would only confirm the existing "no pattern tickets" advice.

## Descriptive rules checks (not tests, not in the Holm family)

D1 EV per-tier realised share Σ prize·winners/deposits vs rules (and old era), smallest prize per tier (any floor?).
D2 6+0 / 6+1 multiple-winner draws and the prize paid. D3 VAN tiers 2–7 constant over all 410 draws?
D4 exact P(any prize) for 3 € on a Monday: 2 EV disjoint, 2 VAN (5–6 common), 1 EV + 1 VAN.
D5 does the EV extra number affect P(any prize)? (rules: no, 3+0 pays) — and value of extra-number choice via C2.
D6 VAN tier-count over-dispersion (variance/mean of standardized counts) as a descriptive measure of ticket clustering.

Scripts: `scripts/ideas_ev.py` (H1–H8, H10 + money), `scripts/ideas_van.py` (H9, D3, D6),
`scripts/ideas_rules.py` (D1–D5), `scripts/ideas_holm.py` (Holm + outputs). All run with `python3 -I`.
