"""
Settlement of the Euromiliony tickets for the draw of 2026-09-26.

Draw confirmed by two DATED sources before use:
  - pandatip.com, "Sobota 26. septembra 2026"
  - bingoo.sk, "26. 9. 2026 (Sobota)"
Plus the numbers on tipos.sk itself, which are shown WITHOUT a date and so
were not used on their own - they match.
"""
from fractions import Fraction
from math import comb

P, K, E = 33, 7, 6
T = comb(P, K) * E
PAY = {(7,1),(7,0),(6,1),(6,0),(5,1),(5,0),(4,1),(4,0),(3,1),(2,1)}
RANK = {(7,1):1,(7,0):2,(6,1):3,(6,0):4,(5,1):5,(5,0):6,(4,1):7,(4,0):8,(3,1):9,(2,1):10}

DRAW_MAIN, DRAW_EXTRA = {12, 13, 18, 26, 28, 30, 33}, 1
TICKETS = [("Ticket 1", {2, 9, 14, 20, 25, 31, 33}, 6),
           ("Ticket 2", {5, 11, 17, 22, 28, 30, 32}, 3)]

def cnt(k, j): return comb(K,k)*comb(P-K,K-k)*(1 if j else E-1)

print("DRAW 2026-09-26 (Saturday)")
print(f"  main  : {sorted(DRAW_MAIN)}")
print(f"  extra : {DRAW_EXTRA}\n")

won = 0
for name, m, x in TICKETS:
    hit = m & DRAW_MAIN
    k, j = len(hit), 1 if x == DRAW_EXTRA else 0
    pays = (k, j) in PAY
    won += pays
    print(f"{name}: {sorted(m)} + {x}")
    print(f"   main hit : {sorted(hit) or '-'} ({k})   extra: {'hit' if j else 'miss'}")
    if pays:
        p = Fraction(cnt(k, j), T)
        print(f"   -> {k}+{j}  PRIZE, tier {RANK[(k,j)]} of 10  (1 in {1/float(p):,.0f})")
    else:
        print(f"   -> {k}+{j}  no prize")

p_two = Fraction(2_477_047, 12_816_144)
print(f"\n{won} of {len(TICKETS)} tickets won.")
print(f"\nForecast P(any prize, two tickets) = {float(p_two)*100:.5f}%")
print(f"Forecast P(both lose)              = {float(1-p_two)*100:.5f}%  <- what happened")

print("\nTicket 2 landed on 2+0. The lowest paying tier is 2+1, so the single")
print("additional number was the whole difference. As always, 'one away' is")
print("not a tier - 2+0 pays exactly what 0+0 pays.")
print("\nNote the draw's additional number was 1. Neither ticket held it: with")
print("two DIFFERENT additional numbers (6 and 3) we covered 2 of the 6, which")
print("is the configuration that maximises P(any prize) - it trades a lower")
print("chance of hitting the extra at all for never wasting both tickets on")
print("the same one. That trade was correct ex ante and lost ex post.")
