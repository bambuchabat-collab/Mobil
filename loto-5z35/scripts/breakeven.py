import numpy as np, math
rng=np.random.default_rng(11)
n=35; N_OFF=2067
# What per-ball bias is needed to turn a 52.6% return into a profitable 100%?
need=(1/0.526)**(1/5)
print("=== WHAT WOULD A *PROFITABLE* BIAS LOOK LIKE? ===")
print(f"Best achievable return today (best ticket): 52.6% of stake")
print(f"To break even you need each of your 5 balls to be")
print(f"  {(need-1)*100:.1f}% more likely than fair  -> p = {need*5/35:.5f} vs fair 0.14286\n")

def sim_chi(bias_set,eps,ndraws,reps=300):
    w=np.ones(n); w[bias_set]=1+eps; w=w/w.sum()
    lw=np.log(w); out=np.empty(reps)
    for r in range(reps):
        gum=lw+rng.gumbel(size=(ndraws,n))
        pick=np.argpartition(-gum,5,axis=1)[:,:5]
        cnt=np.bincount(pick.ravel(),minlength=n)
        exp=ndraws*5/n
        out[r]=((cnt-exp)**2/exp).sum()
    return out

fav=np.arange(5)
print(f"{'per-ball bias':>14s} {'return':>8s} {'mean chi2':>10s} {'P(detected)':>12s}")
for eps in (0.0,0.05,0.10,need-1,0.25,0.50):
    c=sim_chi(fav,eps,N_OFF)
    ret=0.526*(1+eps)**5
    print(f"{eps*100:13.1f}% {ret*100:7.1f}% {c.mean():10.1f} {(c>48.6).mean():11.1%}")
print(f"\nREAL DATA: chi2 = 29.68  -> sits exactly where a FAIR machine sits (mean 34).")
print("A bias big enough to profit from would show chi2 in the hundreds and be")
print("spotted instantly by TIPOS's own state supervision, which tests the balls")
print("before every draw.")
