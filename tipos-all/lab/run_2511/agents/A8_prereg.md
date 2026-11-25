# A8 pre-registration — family: PSEUDO-RANDOM GENERATOR / SEED SEARCH
Written: 2026-11-25T05:56:07Z (UTC), before any evaluation on draws 30..411.

Hypothesis: VAN draws come from a weak software PRNG seeded by the draw date; reproducing the generator's output
for the evaluated date gives the draw, and its complement gives a 0-hit ticket.

## Search space (72 combos = 3 generators x 6 seed formats x 4 methods)
Date D = date of the evaluated draw. Only the 'date' field of the evaluated draw is read (via DRAWS[len(past)]['date'];
for the 25.11 ticket D = 2026-11-25); its 'main'/'order' are never read. The draw date is public in advance.
Generators: PY = random.Random(seed) (Mersenne Twister); RS = numpy.random.RandomState(seed); PCG = numpy.random.default_rng(seed).
Seed formats: YMD = int(YYYYMMDD); DMY = int(DDMMYYYY); YMD6 = int(YYMMDD); UDAY = days since 1970-01-01;
 TS_LOC = unix timestamp of 18:00:00 Europe/Bratislava local time (CET/CEST); TS_CET = unix timestamp of 18:00:00 fixed UTC+1.
Methods (output = set of 11 numbers in 1..22):
 SAMPLE: PY rng.sample(range(1,23),11); RS/PCG rng.choice(np.arange(1,23),11,replace=False)
 SHUF:   a = [1..22]; rng.shuffle(a); first 11
 SEQ:    pool = [1..22]; 11 times pick x = rng.choice(pool) (single element) and remove it
 REJ:    draw uniform ints in 1..22 (PY randint(1,22); RS randint(1,23); PCG integers(1,23)) until 11 distinct
(For RS, SAMPLE and SHUF are algorithmically identical; kept, noted.)

## Step 1 (search on draws 0..29 only)
overlap(c, t) = |output_c(D_t) ∩ main_t|. Score = #draws in 0..29 with overlap >= 9 (null P = 3147/705432 = 0.00446,
expected 0.134 per combo). Best combo = max score, tie-break higher mean overlap on 0..29, then enumeration order
(gen PY,RS,PCG; seed YMD,DMY,YMD6,UDAY,TS_LOC,TS_CET; method SAMPLE,SHUF,SEQ,REJ).
"More than chance" judged by per-combo binomial p and family-wise p = 1-(1-p)^72 for the max score. Also report
#draws with overlap <= 2 (complement-style generator) in 0..29.

## Rules (evaluated with harness.evaluate on draws 30..411; primary metric p_mean_lower)
R1 (PRIMARY): ticket = complement of best-combo (Step 1) output for date D.
R2: ticket = complement of the combo with highest mean overlap on draws 0..29 (tie-break enumeration order).
R3: ticket = direct output (no complement) of the combo with LOWEST mean overlap on draws 0..29 (tie-break enumeration order).

## Additional reports (descriptive, not rules)
- Overlap distribution of the R1 combo on draws 30..411 and on all 412 vs hypergeometric(22,11,11):
  chi-square on bins {0-3,4,5,6,7,8-11}, Monte Carlo p (numpy default_rng(12345), 20000 sims of n draws).
- For all 72 combos: #draws with overlap >= 9 on 30..411 (expected 1.70) and mean overlap — descriptive only.
No parameters are tuned on draws 30..411.
