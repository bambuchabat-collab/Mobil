"""Chi-square upper tail without a scipy dependency."""

from math import exp, log, lgamma


def _gser(a, x):
    ap, s, d = a, 1.0 / a, 1.0 / a
    for _ in range(2000):
        ap += 1
        d *= x / ap
        s += d
        if abs(d) < abs(s) * 1e-15:
            break
    return s * exp(-x + a * log(x) - lgamma(a))


def _gcf(a, x):
    tiny = 1e-300
    b, c, d = x + 1 - a, 1 / tiny, 1 / (x + 1 - a)
    h = d
    for i in range(1, 2000):
        an = -i * (i - a)
        b += 2
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1 / d
        delta = d * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return exp(-x + a * log(x) - lgamma(a)) * h


def chi2_sf(chi2, df):
    """P(X > chi2) for a chi-square with df degrees of freedom."""
    a, x = df / 2.0, chi2 / 2.0
    if x <= 0:
        return 1.0
    return 1.0 - _gser(a, x) if x < a + 1 else _gcf(a, x)


def normal_sf(z):
    """P(Z > z) for a standard normal, via erfc."""
    from math import erfc, sqrt
    return 0.5 * erfc(z / sqrt(2))
