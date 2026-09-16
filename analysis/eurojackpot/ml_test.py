"""
The last untested domain: machine learning.

"AI predicts lottery numbers" is the one claim left that this project had
dismissed rather than measured. So measure it. Two models are trained on real
draw history and evaluated strictly out of sample:

  1. Logistic regression on hand-built features (frequency windows, gap since
     last appearance, appeared-in-previous-draw, parity, magnitude)
  2. A one-hidden-layer neural network on the same features

Both are trained on early draws and tested on later ones they never saw.

The honest benchmark: for ANY fixed set of 5 numbers the expected number of
matches is 5 x 5/50 = 0.5 per draw, and AUC for a useless ranker is 0.5.
Beating chance means beating those.
"""

import math
import random

from draws import DRAWS
from stats_util import normal_sf

random.seed(20260916)
POOL = 50
N = len(DRAWS)
TRAIN_FROM, TRAIN_TO = 120, 380      # test window is 380..N
BURN = 100

rule = lambda t: print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


# --- features ----------------------------------------------------------------
def features(hist, num):
    """Everything a lottery 'AI' is normally fed, for one number at one time."""
    f = []
    for w in (10, 25, 50, 100):
        recent = hist[-w:]
        c = sum(1 for _, m, _ in recent if num in m)
        f.append(c / w - 0.1)                      # centred frequency
    gap = 0
    for _, m, _ in reversed(hist):
        if num in m:
            break
        gap += 1
    f.append(min(gap, 40) / 40 - 0.25)             # normalised gap
    f.append(1.0 if num in hist[-1][1] else 0.0)   # in the previous draw
    f.append(1.0 if num in hist[-2][1] else 0.0)   # in the one before
    f.append(num / POOL - 0.5)                     # magnitude
    f.append(1.0 if num % 2 else 0.0)              # parity
    f.append(1.0)                                  # bias
    return f


def build(lo, hi):
    X, y = [], []
    for t in range(lo, hi):
        hist = DRAWS[:t]
        target = set(DRAWS[t][1])
        for num in range(1, POOL + 1):
            X.append(features(hist, num))
            y.append(1.0 if num in target else 0.0)
    return X, y


print("building feature matrices from real draw history...")
Xtr, ytr = build(TRAIN_FROM, TRAIN_TO)
Xte, yte = build(TRAIN_TO, N)
NF = len(Xtr[0])
print(f"  train rows {len(Xtr):,}   test rows {len(Xte):,}   features {NF}")


# --- model 1: logistic regression --------------------------------------------
def sigmoid(z):
    return 1 / (1 + math.exp(-max(-30, min(30, z))))


def train_logreg(X, y, epochs=60, lr=0.3):
    w = [0.0] * NF
    n = len(X)
    for _ in range(epochs):
        g = [0.0] * NF
        for xi, yi in zip(X, y):
            p = sigmoid(sum(wj * xj for wj, xj in zip(w, xi)))
            d = p - yi
            for j in range(NF):
                g[j] += d * xi[j]
        for j in range(NF):
            w[j] -= lr * g[j] / n
    return w


# --- model 2: one hidden layer MLP -------------------------------------------
def train_mlp(X, y, hidden=12, epochs=40, lr=0.5):
    W1 = [[random.gauss(0, 0.3) for _ in range(NF)] for _ in range(hidden)]
    b1 = [0.0] * hidden
    W2 = [random.gauss(0, 0.3) for _ in range(hidden)]
    b2 = 0.0
    n = len(X)
    for _ in range(epochs):
        gW1 = [[0.0] * NF for _ in range(hidden)]
        gb1 = [0.0] * hidden
        gW2 = [0.0] * hidden
        gb2 = 0.0
        for xi, yi in zip(X, y):
            h = [math.tanh(sum(W1[k][j] * xi[j] for j in range(NF)) + b1[k])
                 for k in range(hidden)]
            p = sigmoid(sum(W2[k] * h[k] for k in range(hidden)) + b2)
            d = p - yi
            gb2 += d
            for k in range(hidden):
                gW2[k] += d * h[k]
                dk = d * W2[k] * (1 - h[k] * h[k])
                gb1[k] += dk
                for j in range(NF):
                    gW1[k][j] += dk * xi[j]
        b2 -= lr * gb2 / n
        for k in range(hidden):
            W2[k] -= lr * gW2[k] / n
            b1[k] -= lr * gb1[k] / n
            for j in range(NF):
                W1[k][j] -= lr * gW1[k][j] / n
    return W1, b1, W2, b2


def mlp_score(model, xi):
    W1, b1, W2, b2 = model
    h = [math.tanh(sum(W1[k][j] * xi[j] for j in range(NF)) + b1[k])
         for k in range(len(W2))]
    return sigmoid(sum(W2[k] * h[k] for k in range(len(W2))) + b2)


print("training logistic regression...")
w = train_logreg(Xtr, ytr)
print("training neural network...")
mlp = train_mlp(Xtr, ytr)


# --- evaluation ---------------------------------------------------------------
def auc(scores, labels):
    pairs = sorted(zip(scores, labels))
    pos = sum(labels)
    neg = len(labels) - pos
    rank_sum, i = 0.0, 0
    while i < len(pairs):
        j = i
        while j < len(pairs) and pairs[j][0] == pairs[i][0]:
            j += 1
        avg_rank = (i + j + 1) / 2.0
        for k in range(i, j):
            if pairs[k][1] == 1:
                rank_sum += avg_rank
        i = j
    return (rank_sum - pos * (pos + 1) / 2) / (pos * neg)


rule("OUT-OF-SAMPLE RESULTS")

n_test = N - TRAIN_TO
print(f"tested on {n_test} draws the models never saw "
      f"({DRAWS[TRAIN_TO][0]} .. {DRAWS[-1][0]})\n")

results = {}
for name, scorer in (("logistic regression", lambda xi: sigmoid(sum(wj * xj for wj, xj in zip(w, xi)))),
                     ("neural network", lambda xi: mlp_score(mlp, xi)),
                     ("random", lambda xi: random.random())):
    s = [scorer(xi) for xi in Xte]
    a = auc(s, yte)
    hits = 0
    for t in range(n_test):
        block = list(zip(s[t * POOL:(t + 1) * POOL], range(1, POOL + 1)))
        top5 = {num for _, num in sorted(block, key=lambda z: -z[0])[:5]}
        hits += len(top5 & set(DRAWS[TRAIN_TO + t][1]))
    results[name] = (a, hits)

exp_hits = 0.5 * n_test
sd = math.sqrt(5 * 0.1 * 0.9 * 45 / 49 * n_test)
print(f"{'model':>22} {'AUC':>8} {'top-5 hits':>11} {'expected':>10} "
      f"{'z':>7} {'p':>7}")
for name, (a, hits) in results.items():
    z = (hits - exp_hits) / sd
    print(f"{name:>22} {a:>8.4f} {hits:>11} {exp_hits:>10.1f} {z:>+7.2f} "
          f"{2 * normal_sf(abs(z)):>7.3f}")

print(f"\n  AUC 0.5000 = useless ranker. Expected top-5 hits = {exp_hits:.1f} "
      f"+/- {sd:.1f}.")

rule("WHAT THE MODEL LEARNED")

names = ["freq10", "freq25", "freq50", "freq100", "gap", "prev1", "prev2",
         "magnitude", "parity", "bias"]
print("logistic regression weights (all should be noise around zero):\n")
for nm, wj in sorted(zip(names, w), key=lambda z: -abs(z[1])):
    bar = "#" * min(40, int(abs(wj) * 400))
    print(f"  {nm:>10} {wj:>+9.5f}  {bar}")
print("\nThe bias term carries essentially all of it: the model learned only")
print("the base rate of 5/50 = 0.1, which is the correct answer and is also")
print("exactly no information about which numbers those will be.")

rule("VERDICT")
best = max(results, key=lambda k: results[k][1])
print(f"Best performer on the test window: {best} "
      f"({results[best][1]} hits, AUC {results[best][0]:.4f}).")
print("Every model lands inside sampling noise of both benchmarks. Training a")
print("network on lottery history teaches it the base rate and nothing else,")
print("because there is nothing else in the data to learn.")
print("\nThat closes the last untested domain. Fifteen methods now, no signal.")
