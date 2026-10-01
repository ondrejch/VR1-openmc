"""Rossi-alpha (cross-correlation) and Feynman-alpha analysis of the VR-1
approach-to-criticality timestamp files.

Assumptions (verify against the DAQ documentation):
  * timestamps are integer ticks of TICK_S seconds (1 us here; inferred from
    ~100 s acquisitions containing ~1e8 ticks),
  * detectors A and B share one clock.

Outputs (in ./noise_outputs): alpha_summary.csv, rossi_<h>.png, feynman_<h>.png,
alpha_vs_rod.png.  Run with the vr1-openmc conda env (needs scipy).
"""
import argparse
import glob
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "noise_outputs")
# Channel B double-triggers: ~23% of B pulses are followed by another exactly 12-13 us later
# (independent of count rate, absent in A).  --veto drops the trailing pulse of such pairs.
B_VETO_WINDOWS = [(12, 13)]
TICK_S = 1e-6
HEIGHTS = [0, 200, 350, 425]

# Rossi-alpha settings (ticks)
BIN = 20                # correlation bin width
MAX_LAG = 40_000        # +/- lag window
FIT_MIN_LAG = 100       # skip |tau| below this: electronics ringing / dead time
FIT_MAX_LAG = 30_000
# Feynman-alpha settings
GATES = np.unique(np.logspace(np.log10(200), np.log10(200_000), 40).astype(int))
FEYN_MIN_GATE = 500


def load(h, det):
    f = glob.glob(os.path.join(HERE, f"*R1-{h}-{det}.csv"))[0]
    return np.loadtxt(f, dtype=np.int64)


def veto_double_triggers(t, windows):
    """Drop pulses whose interval to the preceding raw pulse falls in any (lo, hi) window (ticks, inclusive)."""
    d = np.diff(t)
    drop = np.zeros(len(d), bool)
    for lo, hi in windows:
        drop |= (d >= lo) & (d <= hi)
    return np.concatenate([t[:1], t[1:][~drop]])


def cross_correlation(a, b, dt, max_lag):
    """C[k] = number of (A,B) pairs with t_B - t_A in bin k, via FFT of binned series.
    Returns lag centres (ticks), pair counts, and the accidental expectation per bin."""
    t0 = min(a[0], b[0])
    span = min(a[-1], b[-1]) - max(a[0], b[0])
    n = int((max(a[-1], b[-1]) - t0) // dt) + 1
    ha = np.bincount((a - t0) // dt, minlength=n).astype(float)
    hb = np.bincount((b - t0) // dt, minlength=n).astype(float)
    N = 1 << int(np.ceil(np.log2(2 * n)))
    c = np.fft.irfft(np.conj(np.fft.rfft(ha, N)) * np.fft.rfft(hb, N), N)
    K = int(max_lag // dt)
    k = np.arange(-K, K + 1)
    acc = len(a) * len(b) * dt / span
    return k * dt, np.rint(c[k % N]), acc


def rossi_model(tau, A, alpha, C):
    return C + A * np.exp(-alpha * np.abs(tau) * TICK_S)


def fit_rossi(tau, c):
    m = (np.abs(tau) >= FIT_MIN_LAG) & (np.abs(tau) <= FIT_MAX_LAG)
    x, y = tau[m], c[m]
    sig = np.sqrt(np.maximum(y, 1.0))
    p0 = [0.01 * y.mean(), 500.0, y.mean()]
    p, cov = curve_fit(rossi_model, x, y, p0=p0, sigma=sig, absolute_sigma=True)
    chi2 = np.sum(((y - rossi_model(x, *p)) / sig) ** 2) / (len(x) - 3)
    err = np.sqrt(np.diag(cov)) * np.sqrt(max(chi2, 1.0))   # inflate if chi2/dof>1
    return p, err, chi2, m


def feynman_shape(T, Yinf, alpha, c):
    aT = alpha * T * TICK_S
    return Yinf * (1.0 - (1.0 - np.exp(-aT)) / aT) + c


def feynman_Y(t, gates):
    """Variance-to-mean Y(T) with error from the sample-4th-moment estimate."""
    Y, dY = [], []
    for T in gates:
        n = np.bincount((t - t[0]) // T)[:-1].astype(float)   # drop partial last gate
        N, m = len(n), n.mean()
        d = n - m
        v = d @ d / (N - 1)
        m4 = np.mean(d ** 4)
        var_v = (m4 - v ** 2 * (N - 3) / (N - 1)) / N
        Y.append(v / m - 1.0)
        dY.append(np.sqrt(max(var_v, 0)) / m)
    return np.array(Y), np.array(dY)


def feynman_cross(a, b, gates):
    """Cross Y: Cov(nA,nB)/sqrt(<nA><nB>) -- free of single-channel dead-time / afterpulsing."""
    t0 = max(a[0], b[0])
    Y, dY = [], []
    for T in gates:
        n = int((min(a[-1], b[-1]) - t0) // T)
        na = np.bincount((a - t0)[a >= t0] // T, minlength=n + 1)[:n].astype(float)
        nb = np.bincount((b - t0)[b >= t0] // T, minlength=n + 1)[:n].astype(float)
        da, db = na - na.mean(), nb - nb.mean()
        prod = da * db
        Y.append(prod.sum() / (n - 1) / np.sqrt(na.mean() * nb.mean()))
        dY.append(prod.std(ddof=1) / np.sqrt(n) / np.sqrt(na.mean() * nb.mean()))
    return np.array(Y), np.array(dY)


def fit_feynman(gates, Y, dY, gmin=FEYN_MIN_GATE, with_const=False):
    m = gates >= gmin
    if with_const:
        f, p0 = feynman_shape, [max(Y.max(), 1e-3), 500.0, 0.0]
    else:
        f = lambda T, Yinf, alpha: feynman_shape(T, Yinf, alpha, 0.0)
        p0 = [max(Y.max(), 1e-3), 500.0]
    p, cov = curve_fit(f, gates[m], Y[m], p0=p0, sigma=dY[m], absolute_sigma=True, maxfev=20000)
    r = (Y[m] - f(gates[m], *p)) / dY[m]
    chi2 = np.sum(r ** 2) / (m.sum() - len(p))
    err = np.sqrt(np.diag(cov)) * np.sqrt(max(chi2, 1.0))
    return p, err, chi2, f


def feynman_diff_shape(T, Yinf, alpha):
    """Adjacent-gate-difference estimator: Var(n_i - n_{i+1})/2m - 1 = 2Y(T) - Y(2T)."""
    return 2 * feynman_shape(T, Yinf, alpha, 0.0) - feynman_shape(2 * T, Yinf, alpha, 0.0)


def feynman_diff(a, b, gates):
    """Drift-suppressed Y from non-overlapping gate pairs. b=None: auto-Y of a; else cross-Y of a and b."""
    t0 = max(a[0], b[0]) if b is not None else a[0]
    t1 = min(a[-1], b[-1]) if b is not None else a[-1]
    Y, dY = [], []
    for T in gates:
        n = int((t1 - t0) // (2 * T)) * 2
        na = np.bincount((a - t0)[(a >= t0) & (a < t0 + n * T)] // T, minlength=n)[:n].astype(float)
        da = na[0::2] - na[1::2]
        if b is None:
            z = da ** 2 / 2 / na.mean() - 1.0
        else:
            nb = np.bincount((b - t0)[(b >= t0) & (b < t0 + n * T)] // T, minlength=n)[:n].astype(float)
            z = da * (nb[0::2] - nb[1::2]) / 2 / np.sqrt(na.mean() * nb.mean())
        Y.append(z.mean())
        dY.append(z.std(ddof=1) / np.sqrt(len(z)))
    return np.array(Y), np.array(dY)


def fit_feynman_diff(gates, Y, dY, gmin=FEYN_MIN_GATE):
    m = gates >= gmin
    p, cov = curve_fit(feynman_diff_shape, gates[m], Y[m], p0=[max(Y.max(), 1e-3), 500.0],
                       sigma=dY[m], absolute_sigma=True, maxfev=20000)
    chi2 = np.sum(((Y[m] - feynman_diff_shape(gates[m], *p)) / dY[m]) ** 2) / (m.sum() - 2)
    return p, np.sqrt(np.diag(cov)) * np.sqrt(max(chi2, 1.0)), chi2


def main():
    global OUT
    ap = argparse.ArgumentParser()
    ap.add_argument("--veto", action="store_true", help="remove channel-B 12-13 us double-trigger pulses")
    args = ap.parse_args()
    if args.veto:
        OUT += "_veto"
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for h in HEIGHTS:
        a, b = load(h, "A"), load(h, "B")
        if args.veto:
            nb = len(b)
            b = veto_double_triggers(b, B_VETO_WINDOWS)
            print(f"[veto] removed {nb - len(b)} of {nb} B pulses")
        dur = (min(a[-1], b[-1]) - max(a[0], b[0])) * TICK_S
        print(f"\n=== R1 = {h} mm  (A: {len(a)} pulses {len(a)/dur:.0f} cps, "
              f"B: {len(b)} pulses {len(b)/dur:.0f} cps, {dur:.1f} s)")

        # ---- Rossi-alpha: A x B cross-correlation (symmetric exponential)
        tau, c, acc = cross_correlation(a, b, BIN, MAX_LAG)
        p, e, chi2, m = fit_rossi(tau, c)
        print(f"Rossi X-corr : alpha = {p[1]:8.1f} +/- {e[1]:.1f} 1/s   "
              f"A/C = {p[0]/p[2]:.4f}   chi2/dof = {chi2:.2f}")
        rows.append((h, "rossi_AxB", p[1], e[1], chi2, p[0] / p[2]))

        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(tau * TICK_S * 1e3, c / acc, ".", ms=2, alpha=0.5, label="A×B pairs / accidental")
        ax.plot(tau[m] * TICK_S * 1e3, rossi_model(tau[m], *p) / acc, "r-", lw=1.2,
                label=f"fit α = {p[1]:.0f} ± {e[1]:.0f} s⁻¹")
        ax.set(xlabel="τ = t_B − t_A (ms)", ylabel="normalized coincidence rate",
               title=f"Rossi-α cross-correlation, R1 = {h} mm", ylim=(0.97, 1.06))
        ax.legend(); fig.tight_layout(); fig.savefig(f"{OUT}/rossi_{h}.png", dpi=150); plt.close(fig)

        # ---- Feynman-alpha: auto (A, B) and cross
        fig, ax = plt.subplots(figsize=(7, 4))
        for label, Yfun in [("A", lambda: feynman_Y(a, GATES)), ("B", lambda: feynman_Y(b, GATES)),
                            ("A×B", lambda: feynman_cross(a, b, GATES))]:
            Y, dY = Yfun()
            for wc in (False, True):
                if label == "A×B" and wc:
                    continue
                try:
                    p, e, chi2, f = fit_feynman(GATES, Y, dY, with_const=wc)
                except RuntimeError:
                    print(f"Feynman {label:3s} const={wc}: fit failed"); continue
                tag = f"feynman_{label}{'+c' if wc else ''}"
                print(f"Feynman {label:3s} const={int(wc)}: alpha = {p[1]:8.1f} +/- {e[1]:.1f} 1/s   "
                      f"Yinf = {p[0]:.4f}   chi2/dof = {chi2:.2f}")
                rows.append((h, tag, p[1], e[1], chi2, p[0]))
                if wc == (label != "A×B"):
                    ax.errorbar(GATES * TICK_S * 1e3, Y, dY, fmt=".", ms=4, label=label)
                    ax.plot(GATES * TICK_S * 1e3, f(GATES, *p), "-", lw=1)
        ax.set(xscale="log", xlabel="gate T (ms)", ylabel="Y(T)",
               title=f"Feynman-α, R1 = {h} mm")
        ax.legend(); fig.tight_layout(); fig.savefig(f"{OUT}/feynman_{h}.png", dpi=150); plt.close(fig)

        # ---- Feynman-alpha, drift-suppressed (adjacent-gate differences)
        fig, ax = plt.subplots(figsize=(7, 4))
        for label, (x, y) in [("A", (a, None)), ("B", (b, None)), ("A×B", (a, b))]:
            Y, dY = feynman_diff(x, y, GATES)
            try:
                p, e, chi2 = fit_feynman_diff(GATES, Y, dY)
            except RuntimeError:
                print(f"FeynmanDiff {label:3s}: fit failed"); continue
            print(f"FeynmanDiff {label:3s}      : alpha = {p[1]:8.1f} +/- {e[1]:.1f} 1/s   "
                  f"Yinf = {p[0]:.4f}   chi2/dof = {chi2:.2f}")
            rows.append((h, f"feynman_diff_{label}", p[1], e[1], chi2, p[0]))
            ax.errorbar(GATES * TICK_S * 1e3, Y, dY, fmt=".", ms=4, label=label)
            ax.plot(GATES * TICK_S * 1e3, feynman_diff_shape(GATES, *p), "-", lw=1)
        ax.set(xscale="log", xlabel="gate T (ms)", ylabel="Y_diff(T)",
               title=f"Feynman-α (adjacent-gate differences), R1 = {h} mm")
        ax.legend(); fig.tight_layout(); fig.savefig(f"{OUT}/feynman_diff_{h}.png", dpi=150); plt.close(fig)

    with open(f"{OUT}/alpha_summary.csv", "w") as fh:
        fh.write("R1_mm,method,alpha_per_s,alpha_err,chi2_dof,amplitude\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")

    fig, ax = plt.subplots(figsize=(6, 4))
    for meth in sorted({r[1] for r in rows}):
        rr = [r for r in rows if r[1] == meth]
        ax.errorbar([r[0] for r in rr], [r[2] for r in rr], [r[3] for r in rr], fmt="o-", ms=4, label=meth)
    ax.set(xlabel="R1 position (mm)", ylabel="α (1/s)", title="Prompt decay constant vs rod height")
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{OUT}/alpha_vs_rod.png", dpi=150)


if __name__ == "__main__":
    main()
