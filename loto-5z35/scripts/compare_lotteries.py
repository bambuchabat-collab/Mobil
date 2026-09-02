"""Compare every TIPOS numeric lottery on return to player.

Two methods, because they answer different questions:
  - empirical: prizes actually paid / stakes, pooled over years. Correct for
    games whose top prize is hit often enough to be sampled.
  - combinatorial: exact tier odds x observed prize levels. Needed for
    Eurojackpot, where Slovak players hit the top tier once in 4.5 years so
    the empirical figure is luck, not design.
"""
from math import comb

TOT = comb(50, 5) * comb(12, 2)          # 139,838,160


def ej_prob(m, e):
    return comb(5, m) * comb(45, 5 - m) * comb(2, e) * comb(10, 2 - e) / TOT


# median prize per tier, measured from 475 Slovak draws 2022-2026
EJ_LOWER = {(5, 1): 539537.0, (5, 0): 133307.15, (4, 2): 4908.0, (4, 1): 317.60,
            (3, 2): 160.60, (4, 0): 113.10, (2, 2): 25.60, (3, 1): 20.30,
            (3, 0): 17.20, (1, 2): 12.90, (2, 1): 9.90}
EJ_PRICE = 2.00
ev_low = sum(ej_prob(m, e) * v for (m, e), v in EJ_LOWER.items())

print("=== EUROJACKPOT: return as a function of the jackpot ===")
print(f"  lower tiers alone: {ev_low:.4f} EUR = {ev_low / EJ_PRICE * 100:.1f}% of the 2.00 EUR ticket")
for J in (15e6, 23e6, 50e6, 120e6):
    ev = ev_low + ej_prob(5, 2) * J
    print(f"  jackpot {J:>13,.0f} -> EV {ev:.4f} EUR, return {ev / EJ_PRICE * 100:5.1f}%")
need = (EJ_PRICE - ev_low) / ej_prob(5, 2)
print(f"\n  jackpot required to break even: {need:,.0f} EUR")
print(f"  Eurojackpot is capped at 120,000,000 EUR, so break-even is unreachable.")

print("\n=== EMPIRICAL RETURN, prizes actually paid / stakes ===")
for nm, rtp, n, span in (("LOTO 5 z 35", 52.1, 560, "2022-2026"),
                         ("LOTO 6/49", 51.2, 564, "2022-2026"),
                         ("Vsetko alebo nic", 47.3, 329, "2025-2026"),
                         ("Eurojackpot (SK realised)", 31.2, 475, "2022-2026")):
    print(f"  {nm:26s} {rtp:5.1f}%   n={n:4d}  {span}")
print("\n  The Eurojackpot line is realised Slovak luck, not the game's design:")
print("  one 5+2 hit in 4.5 years. By design it pays out about half of stakes,")
print("  but almost all of that sits in events of probability 1 in 139,838,160.")

print("\n=== ODDS OF WINNING ANYTHING ===")
p_any = sum(ej_prob(m, e) for m, e in list(EJ_LOWER) + [(5, 2)])
print(f"  Eurojackpot: 1 in {1 / p_any:.1f}   (typical low-tier prize ~10 EUR on a 2.00 EUR ticket)")
p35 = (comb(5, 3) * comb(30, 2) + comb(5, 4) * comb(30, 1) + 1) / comb(35, 5)
print(f"  LOTO 5 z 35: 1 in {1 / p35:.1f}   (typical prize 3.30 EUR on a 0.60 EUR ticket)")
