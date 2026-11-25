# A5 pre-registration: CALENDAR AND DATE NUMEROLOGY

- Written: 2026-11-25T05:55:40Z (UTC, `date -u`). No evaluation had been run when this was written.
  Inspected before writing: harness.py, data format (first two records), date gaps (two gaps:
  2025-12-23 -> 2025-12-26 and 2026-04-02 -> 2026-04-04, so dates are NOT strictly consecutive) and
  weekday-label counts (Pondelok 60, Utorok 60, Streda 58, Stvrtok 58, Piatok 58, Sobota 59, Nedela 59).
  No number frequencies were looked at.
- Data: van412.json sha256 ce9a079e488f458befa620ef7695a3c9f01a2e3fbbe02f3229a4d13d807bd73e
  Harness: harness.py sha256 a85a1e3e57b1a3113fc0ca37e6e403f8ad3cc2111fb5f302afe98f993427aad4
- Script: agents/A5.py (python3 -I, numpy only), output agents/A5.json. Master seed SEED = 20261125.

## Target date

A rule for evaluated index t receives past = DRAWS[:t]. Its target date is the calendar date of draw t,
read as DRAWS[t]['date'] (the `date` field only; never `main`/`order` of draw t). For the final ticket
(t = 412) the target date is 2026-11-25 (Wednesday). Because of the two gaps, the date cannot be derived
as "previous date + 1", so it is taken from the calendar column.

## Tie-breaking (all rules)

Priority permutation of 1..22: `numpy.random.default_rng([SEED, r, t]).permutation(22) + 1`
(r = rule number 1..3, t = len(past)). Numbers are sorted by the rule's key, ties by this priority order
(earlier in the permutation = selected first).

## Rules (all parameters fixed here)

- R1 (PRIMARY) Same-weekday cold numbers. w = weekday of the target date (Mon..Sun).
  f_w(n) = number of past draws with weekday w whose `main` contains n. Ticket = the 11 numbers with the
  SMALLEST f_w (hypothesis: a weekday-specific bias persists, so numbers rarely drawn on this weekday stay
  rare on it). At t = 30 each weekday has 4-5 past draws.
- R2 Date-numerology anchors. Target date d (day of month), m (month), y (year). wrap(x) = ((x-1) mod 22) + 1.
  Anchor set A = { wrap(d), m, wrap(digit sum of the 8-digit DDMMYYYY string), digit sum of d,
  ISO weekday 1..7 (Mon = 1) } (duplicates merged, 1..5 anchors).
  Key(n) = circular distance on the ring 1..22 to the nearest anchor: min over a in A of
  min(|n-a|, 22-|n-a|). Ticket = the 11 numbers with the LARGEST key (hypothesis: "date numbers" and
  their neighbours are drawn more often than chance, so the farthest numbers are least likely).
  Uses no draw data at all.
- R3 Lunar-phase cold numbers. Mean lunar age at the draw time 17:00 UTC (18:00 CET) of each date:
  age = (JD - 2451550.2597) mod 29.530588853 days (reference new moon 2000-01-06 18:14 UTC).
  Bucket b = floor(age / 29.530588853 * 4 + 0.5) mod 4 (0 new, 1 first quarter, 2 full, 3 last quarter;
  each bucket centred on its phase). f_b(n) = number of past draws in the target date's bucket that
  contain n. Ticket = the 11 numbers with the SMALLEST f_b (same persistence hypothesis as R1).

## Metrics

Harness `evaluate` over t = 30..411 (n = 382): primary p_mean_lower (exact P(sum hits <= observed));
secondary p_le3. Raw p only (the lead applies Holm across all agents). Primary rule = R1;
ticket_25_11 = R1 applied to all 412 draws with target date 2026-11-25.
