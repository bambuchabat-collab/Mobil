import numpy as np, json, math
rng=np.random.default_rng(2026)
wx=json.load(open('data/weather_bratislava_20260902.json'))
T,RH,P = wx['T'], wx['RH'], wx['P']
print("="*76)
print("PHYSICAL SIMULATION OF THE BALL MACHINE - Bratislava, 02.09.2026, 18:00")
print("="*76)
print(f"Measured draw-time conditions: T={T} C, RH={RH} %, p={P} hPa\n")

n=35
D=0.038; M0=2.7e-3; TOL=0.005
mass=M0*(1+rng.normal(0,TOL/3,n))
uptake=1e-5*(RH/100.0)
mass=mass+uptake*(1+rng.normal(0,0.15,n))
Rd=287.058; Rv=461.495
psat=611.2*math.exp(17.67*T/(T+243.5))
pv=(RH/100)*psat; pd=P*100-pv
rho=pd/(Rd*(T+273.15))+pv/(Rv*(T+273.15))
print(f"Derived air density at draw time: rho = {rho:.4f} kg/m^3")
A=math.pi*(D/2)**2; Cd=0.47; g=9.81
vt=np.sqrt(2*mass*g/(rho*Cd*A))
print(f"Ball mass spread: {mass.min()*1e3:.4f} - {mass.max()*1e3:.4f} g  ({(mass.max()/mass.min()-1)*100:.2f}% spread)")
print(f"Terminal-velocity spread: {vt.min():.3f} - {vt.max():.3f} m/s  ({(vt.max()/vt.min()-1)*100:.2f}%)")

def weights(k):
    w=vt**(-k); return w/w.sum()

print("\n--- how much bias does this physics actually produce? ---")
print(f"{'coupling k':>11s} {'max p (fair=0.1429)':>21s} {'bias':>9s} {'EV gain on 5 balls':>20s}")
for k in (0,1,2,5,10):
    w=weights(k)*5
    print(f"{k:11d} {w.max():21.5f} {(w.max()/(5/35)-1)*100:+8.2f}% {((w.max()/(5/35))**5-1)*100:+19.1f}%")

def sim_chi(w,ndraws,reps):
    out=np.empty(reps); lw=np.log(w)
    for r in range(reps):
        gum=lw+rng.gumbel(size=(ndraws,n))
        pick=np.argpartition(-gum,5,axis=1)[:,:5]
        cnt=np.bincount(pick.ravel(),minlength=n)
        exp=ndraws*5/n
        out[r]=((cnt-exp)**2/exp).sum()
    return out

N_OFF=2067; CHI_OBS=29.68; CRIT=48.60
print(f"\n--- can the {N_OFF}-draw record hide such a bias? ---")
print(f"real observed chi2 = {CHI_OBS:.2f}   (a fair machine averages 34.0)")
print(f"{'coupling k':>11s} {'mean chi2':>10s} {'P(test fires)':>14s} {'P(chi2<=29.68)':>16s}")
for k in (0,1,2,5,10):
    c=sim_chi(weights(k),N_OFF,200)
    print(f"{k:11d} {c.mean():10.1f} {(c>CRIT).mean():13.1%} {(c<=CHI_OBS).mean():15.1%}")

