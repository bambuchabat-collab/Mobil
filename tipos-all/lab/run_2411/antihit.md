# VAN anti-hit walk-forward test: results

Pre-registration: `antihit_prereg.md` (written before any result). Data sha256 `8d367f7db9761ca3…`, 412 draws 2025-10-06..2026-11-24 (2 appended). Evaluation draws t = 31..412 (n = 382; R12 n = 381). Seed 20261124.

Null: hits ~ hypergeometric(22, 11, 11), mean 5.5, var 1.440476; P(hits<=3) = 0.04305; P(0 hits) = 1/705432. Expected winnings under null = 0.7552 € per 1.50 € ticket.

## Primary: mean hits < 5.5 (exact one-sided, Holm over R1-R12)

| Rule | Description | n | mean hits | z | p (mean<5.5) | Holm p | survives |
|---|---|---:|---:|---:|---:|---:|:---:|
| R1 | complement of previous draw | 382 | 5.500 | +0.00 | 0.509 | 1.000 | no |
| R2 | complement of draw t-2 | 382 | 5.521 | +0.34 | 0.641 | 1.000 | no |
| R3 | 11 least-frequent, last 5 | 382 | 5.482 | -0.30 | 0.391 | 1.000 | no |
| R4 | 11 least-frequent, last 10 | 382 | 5.615 | +1.88 | 0.971 | 1.000 | no |
| R5 | 11 least-frequent, last 30 | 382 | 5.597 | +1.58 | 0.945 | 1.000 | no |
| R6 | 11 least-frequent, all past | 382 | 5.508 | +0.13 | 0.559 | 1.000 | no |
| R7 | 11 most-frequent, last 5 | 382 | 5.563 | +1.02 | 0.852 | 1.000 | no |
| R8 | 11 most-frequent, last 10 | 382 | 5.448 | -0.85 | 0.203 | 1.000 | no |
| R9 | 11 most-frequent, last 30 | 382 | 5.437 | -1.02 | 0.158 | 1.000 | no |
| R10 | 11 most-frequent, all past | 382 | 5.469 | -0.51 | 0.312 | 1.000 | no |
| R11 | 11 most recently drawn (= previous draw) | 382 | 5.500 | +0.00 | 0.509 | 1.000 | no |
| R12 | late half of prev order (pos 6-11) + 5 random non-drawn | 381 | 5.546 | +0.75 | 0.779 | 1.000 | no |
| R13 | random ticket (negative control) | 382 | 5.469 | -0.51 | 0.312 | — | control |

## Secondary: draws with 0-3 hits, exact 0-hit draws

| Rule | hits<=3 obs | expected | p (binom, >=) | Holm p | 0-hit draws (exp.) | hit histogram 0..11 |
|---|---:|---:|---:|---:|---:|---|
| R1 | 18 | 16.4 | 0.382 | 1.000 | 0 (0.0005) | 0 1 0 17 54 123 110 59 17 1 0 0 |
| R2 | 17 | 16.4 | 0.479 | 1.000 | 0 (0.0005) | 0 0 1 16 63 102 126 60 5 9 0 0 |
| R3 | 18 | 16.4 | 0.382 | 1.000 | 0 (0.0005) | 0 0 4 14 61 114 111 64 10 4 0 0 |
| R4 | 15 | 16.4 | 0.678 | 1.000 | 0 (0.0005) | 0 0 0 15 49 113 114 76 12 3 0 0 |
| R5 | 13 | 16.4 | 0.841 | 1.000 | 0 (0.0005) | 0 0 2 11 50 125 108 61 24 1 0 0 |
| R6 | 21 | 16.4 | 0.153 | 1.000 | 0 (0.0005) | 0 0 3 18 49 128 103 59 21 1 0 0 |
| R7 | 13 | 16.4 | 0.841 | 1.000 | 0 (0.0005) | 0 0 2 11 62 112 114 58 17 6 0 0 |
| R8 | 15 | 16.4 | 0.678 | 1.000 | 0 (0.0005) | 0 1 2 12 67 122 103 57 17 1 0 0 |
| R9 | 26 | 16.4 | 0.016 | 0.188 | 0 (0.0005) | 0 0 1 25 56 106 131 45 17 1 0 0 |
| R10 | 17 | 16.4 | 0.479 | 1.000 | 0 (0.0005) | 0 0 1 16 69 106 118 52 19 1 0 0 |
| R11 | 18 | 16.4 | 0.382 | 1.000 | 0 (0.0005) | 0 0 1 17 59 110 123 54 17 0 1 0 |
| R12 | 12 | 16.4 | 0.897 | 1.000 | 0 (0.0005) | 0 0 0 12 51 123 118 67 9 1 0 0 |
| R13 | 14 | 16.4 | 0.766 | — | 0 (0.0005) | 0 0 2 12 66 122 100 67 11 2 0 0 |

## Money (1 ticket per draw, nominal prize table, top prize counted at full 100 000 €)

Expected under null includes the jackpot EV (2 x 100 000 €/705432 = 0.2835 € per ticket); no rule hit 0 or 11, so the comparable figure without jackpot is 180 € for n = 382.

| Rule | won 0-3 side € | won 8-11 side € | total won € | expected under null € | cost € | net € |
|---|---:|---:|---:|---:|---:|---:|
| R1 | 251 | 71 | 322 | 288 | 573 | -251 |
| R2 | 68 | 195 | 263 | 288 | 573 | -310 |
| R3 | 122 | 110 | 232 | 288 | 573 | -341 |
| R4 | 45 | 96 | 141 | 288 | 573 | -432 |
| R5 | 73 | 92 | 165 | 288 | 573 | -408 |
| R6 | 114 | 83 | 197 | 288 | 573 | -376 |
| R7 | 73 | 171 | 244 | 288 | 573 | -329 |
| R8 | 276 | 71 | 347 | 288 | 573 | -226 |
| R9 | 95 | 71 | 166 | 288 | 573 | -407 |
| R10 | 68 | 77 | 145 | 288 | 573 | -428 |
| R11 | 71 | 251 | 322 | 288 | 573 | -251 |
| R12 | 36 | 47 | 83 | 288 | 572 | -488 |
| R13 | 76 | 73 | 149 | 288 | 573 | -424 |

## Conclusion

- Rules surviving Holm (primary, mean hits < 5.5): none.
- Rules surviving Holm (secondary, excess of 0-3 hit draws): none.
- Check: hits(R1) + hits(R11) = 11 on every draw: True (R11 is the previous draw itself).
- The p-value of the negative control R13 shows the spread expected by chance alone.
