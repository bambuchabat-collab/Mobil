# A6 pre-registration: CROSS-GAME SIGNALS

Written: Wed Nov 25 05:57:23 UTC 2026 (before any evaluation was run).

## Data
- VAN: lab/run_2511/van412.json via harness (evaluated draws 30..411, n = 382).
- Extra vyplata (EV, 6 of 27 + extra 1..7, Mon from 2024-03-25, Mon+Thu from 2026-04-20, 18:00):
  agents/A6_ev.json = run_2311/data/ev.json (170 draws to 2026-11-19) + draw 2026-11-23 fetched today via
  tipos.sk GetForDate (2026 overlap of the fresh download matched ev.json exactly: 0 mismatches). 171 draws.
- Loto 5 z 35 (L535, 5 of 35, Wed/Fri/Sun): agents/A6_l535.json, 286 draws 2025-01-01..2026-11-22, fetched today
  (raw downloads in the scratchpad dir a6/).
- For a VAN draw on date D, only other-game draws with date < D (strictly) are used. Same-day draws are never used.
- Only main numbers that fall in 1..22 are used (EV numbers 23..27 and L535 numbers 23..35 are ignored).
  The EV extra number is not used in any rule.

## Common construction ("recency ticket")
Given a sequence S of other-game draws with date < D, newest first (S1 = most recent):
- age(x) = smallest j with x in S_j (x in 1..22); age(x) = 10**6 if x is in none of the last 60 draws of S.
- cnt(x) = number of the 10 most recent draws S1..S10 that contain x.
- tie-break u(x) = position of x in a random permutation of 1..22 drawn with numpy default_rng([2511, 6, len(past)])
  (len(past) = index of the evaluated VAN draw; fixed seed, independent of any draw outcome).
- Rank x by (age ascending, cnt descending, u ascending). HOT = first 11 numbers, COLD = remaining 11.

## Rules (all parameters fixed above; no tuning)
- **R1 (PRIMARY) EV-hot-avoid:** S = EV draws with date < D. Ticket = HOT (the 11 numbers of 1..22 drawn most recently in EV).
  Hypothesis: numbers just drawn in EV are LESS likely to be drawn in VAN next, so the ticket gets fewer hits.
- **R2 EV-hot-repeat:** same S. Ticket = COLD (exact complement of R1, hits = 11 - hits_R1).
  Hypothesis: numbers just drawn in EV are MORE likely in VAN (shared RNG / hot balls), so avoid them.
- **R3 EV+L535-hot-avoid:** S = EV and L535 draws with date < D merged and sorted by date, newest first (no date carries both games
  in the evaluated window; if one did, the EV draw is placed first). Ticket = HOT. Hypothesis as R1, with a denser signal from two games.

Primary metric: p_mean_lower (harness). Secondary: p_le3. Raw p only (no multiple-testing correction here).
ticket_25_11 = R1 ticket from all 412 VAN draws (EV draws with date < 2026-11-25, i.e. latest = 2026-11-23).
