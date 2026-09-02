import json,statistics,random,math
rows=[r['nums'] for r in json.load(open('data/draws_2014_2026.json'))]
N=len(rows)
def lag_prob(draws,lag):
    """P(n in draw t+lag | n in draw t) and the complement"""
    a=b=A=B=0
    for t in range(len(draws)-lag):
        cur=set(draws[t]); nxt=set(draws[t+lag])
        for n in range(1,36):
            if n in cur:
                A+=1; a+= (n in nxt)
            else:
                B+=1; b+= (n in nxt)
    return a/A, b/B
print("=== Serial dependence: does a drawn number come back sooner? ===")
print(f"   independence would give 0.142857 for both columns\n")
print(f"   {'lag':>4s} {'P(back | was drawn)':>20s} {'P(back | not drawn)':>20s} {'diff':>9s}")
real={}
for lag in (1,2,3,4,5):
    p1,p0=lag_prob(rows,lag); real[lag]=p1-p0
    print(f"   {lag:4d} {p1:20.5f} {p0:20.5f} {p1-p0:+9.5f}")

rng=random.Random(7)
print(f"\n   null from 200 simulated fair lotteries of the same length:")
print(f"   {'lag':>4s} {'sim mean diff':>15s} {'sim sd':>10s} {'real z':>9s}")
for lag in (1,2,3,4,5):
    sims=[]
    for _ in range(200):
        d=[rng.sample(range(1,36),5) for _ in range(N)]
        p1,p0=lag_prob(d,lag); sims.append(p1-p0)
    m=statistics.mean(sims); sd=statistics.pstdev(sims)
    print(f"   {lag:4d} {m:+15.5f} {sd:10.5f} {(real[lag]-m)/sd:+9.2f}")
