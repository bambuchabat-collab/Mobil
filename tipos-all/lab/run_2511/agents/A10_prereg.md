# A10 pre-registration — family: PLAYER POPULARITY ("is the draw biased against what players pick?")

Written 2026-11-25T05:56:18Z (UTC), before any evaluation was run. Only data-integrity checks were done
(van.json draws 0..409 match van412.json by date and main set; all 410 have tiers 11/10/9/8/3/2/1/0; no zero counts).

## Popularity estimate (shared by R1–R3), computed for draw t from past draws only
- Tier data: /home/user/Mobil/tipos-all/lab/run_2311/data/van.json, available for draws 0..409. For evaluated draw t the
  training set is draws s < t with s <= 409 (so draws 410, 411 and the 25.11 ticket use draws 0..409).
- Per draw s: H_s = W8+W9+W10, L_s = W3+W2+W1 (winner counts). Under uniform random draws E[H_s] = E[L_s] = bets*P(3 or 2 or 1),
  so y_s = log((H_s+0.5)/(L_s+0.5)) = log(H/E) - log(L/E): bets cancel. y_s > 0 means the drawn set overlapped players' tickets
  more than chance ("popular draw"). Under the null y(D) = -y(complement D), so its null centre is exactly 0.
- x_s = 22 indicators (number i drawn in s). Ridge regression with unpenalized intercept: centre the x columns and y by their
  training means, beta = (Xc'Xc + lambda I)^-1 Xc'yc, lambda = 1.0 (fixed a priori). Column centring removes any mechanical link
  between beta and past draw frequency. beta_i = popularity of number i.
- Ranking: sort by beta descending, ties broken by smaller number first.

## Rules
- **R1 (primary) "operator avoids popular numbers"**: ticket = the 11 numbers with the largest beta (most popular).
  Hypothesis: popular numbers are drawn less, so this ticket hits fewer than 5.5.
- **R2 "reverse"**: ticket = the 11 numbers with the smallest beta (least popular). Hypothesis: unpopular numbers are drawn
  less. (Its hits are exactly 11 - R1's hits; it is the other tail of R1.)
- **R3 "previous draw's winners -> opposite draw"**: let y_{t-1} be the popularity index of the previous draw (needs tier data,
  i.e. t-1 <= 409; for t = 411 use the last draw with tier data, 409). If y_{t-1} > 0 (previous draw had more 8–10 winners than
  1–3 winners: it favoured players) the next draw is predicted to be the opposite (unpopular), so ticket = R1's ticket (11 most
  popular); if y_{t-1} <= 0, the next draw is predicted popular, so ticket = R2's ticket (11 least popular). Threshold 0 is the
  exact null centre, no tuning.

## Evaluation
harness.evaluate over draws 30..411 (n = 382). Primary metric p_mean_lower; also p_le3. Raw p only (no correction).
Ticket for 25.11.2026 = R1 applied to all 412 draws (popularity from draws 0..409).
