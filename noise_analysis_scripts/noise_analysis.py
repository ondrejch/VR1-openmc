# ----------------------------------------------------------------------------------------------
# Code review of f724a48 (2026-10-01) and the fixes applied below.  Checked on synthetic timestamp
# trains (Poisson chains with known alpha and Yinf split between A and B, 23% B double triggers at
# +12/13 us); no VR-1 files were available, so the real-data results have not been rerun.
#
#  1. FIXED  --veto left a rate-dependent bias in B.  It compared each pulse only with the one just
#     before it, so a double trigger survived whenever a real pulse fell in between, while real
#     pulses 12-13 us after a pulse were dropped.  feynman_B alpha at 2 / 5 / 20 kcps: old veto
#     648 / 880 / 2264 /s, B without double triggers 508 / 521 / 477.  Now every pulse with any
#     earlier raw pulse 12-13 us before it is dropped, and veto_correction() undoes the known effect
#     of that on Y: 498 / 507 / 526.  An O(q^2) offset remains (q = real-pulse loss, printed); for
#     q > 0.02 use feynman_B+c, which came out unbiased within errors at 20 kcps.
#  2. FIXED  Feynman alpha_err treated the ~34 Y(T) points as independent, but they come from one
#     pulse train and are strongly correlated, so the errors were ~2x too small (scatter between
#     seeds 47 /s, quoted 28 /s).  Feynman errors are now delete-one-segment jackknife errors over
#     JACK_K time segments (55 /s in the same test).  Rossi lag bins are close to independent and
#     its fit error was already right (scatter 39, quoted 35), so it is kept.  chi2/dof is now only
#     a diagnostic.
#  3. FIXED  The Rossi fit had no failure handling and used curve_fit's default 800 calls, so one
#     failed fit stopped the run before alpha_summary.csv was written.  All fits now go through
#     fit_curve() (maxfev 20000, failures recorded) and the CSV is rewritten after every height.
#  4. FIXED  The accidental level divided each channel's full count by the A/B overlap, so the Rossi
#     baseline was overlap^2/(T_A T_B): 0.967 for B starting 1 s late in 30 s, at the edge of the
#     fixed ylim (0.97, 1.06).  The accidental level is now computed per lag from each channel's own
#     rate and the overlap at that lag (baseline 1.000), the fit runs on the normalized ratio, and
#     the y-limits follow the data.  Count rates are printed over each channel's own record.
#  5. FIXED  Unphysical or meaningless fits were saved as good (flat data: rossi alpha 1862 +/- 23013,
#     feynman_diff_AxB alpha 5.7e9).  Each row now has a flag (fit_failed, no_error, amplitude<=0,
#     alpha<=0, amplitude<2sigma, alpha_err>alpha); only 'ok' rows go into alpha_vs_rod.png.
#     feynman_shape no longer gives NaN at alpha = 0.
#  6. FIXED  load(): glob(...)[0] took whichever of several matching files came first and gave a bare
#     IndexError for none, and timestamp order was not checked.  Now exactly one match is required,
#     timestamps must be non-decreasing, and a height that fails to load is skipped with a message.
#  7. FIXED  A channel's Y(T) points were drawn only if its plotted fit succeeded, and each fit curve
#     took the next colour in the cycle instead of the colour of its data.
#  8. FIXED  Minor: the veto window was in ticks but documented in us (now B_VETO_WINDOWS_S, seconds);
#     the CSV 'amplitude' column mixed A/C and Yinf (new amplitude_kind column); method names mixed
#     'AxB' and 'A×B' (now ASCII); the CSV encoding is now UTF-8; the docstring's output list was
#     out of date; main() changed the module-level OUT.
#  9. FIXED  Gate counts built full-length masks and a bincount for every gate; they now use
#     np.searchsorted on the sorted train, which pays for the jackknife (runtime unchanged).  The
#     three copies of the fit code are merged into fit_curve().  np.loadtxt is kept.
#  Checked and correct: the difference-estimator identity Var(n_i - n_{i+1})/2m - 1 = 2Y(T) - Y(2T)
#  (auto and cross), the FFT lag indexing of the cross-correlation, and the Feynman estimators
#  themselves (the new code reproduces the old Y(T) values exactly).
# ----------------------------------------------------------------------------------------------
"""Rossi-alpha (cross-correlation) and Feynman-alpha analysis of the VR-1
approach-to-criticality timestamp files.

Assumptions (verify against the DAQ documentation):
  * timestamps are integer ticks of TICK_S seconds (1 us here; inferred from
    ~100 s acquisitions containing ~1e8 ticks),
  * detectors A and B share one clock.

Input: one file per rod height and detector, *R1-<h>-<A|B>.csv, next to this script.
Outputs (in noise_outputs/ next to this script, noise_outputs_veto/ with --veto):
alpha_summary.csv, rossi_<h>.png, feynman_<h>.png, feynman_diff_<h>.png, alpha_vs_rod.png.
Run with the vr1-openmc conda env (needs scipy).
"""
import argparse
import glob
import os
import warnings

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import OptimizeWarning, curve_fit

HERE = os.path.dirname(os.path.abspath(__file__))
TICK_S = 1e-6
# Channel B double-triggers: ~23% of B pulses are followed by another exactly 12-13 us later
# (independent of count rate, absent in A).  --veto drops every B pulse lying 12-13 us after any
# earlier B pulse and corrects the auto-Y of B for the real pulses this also removes (veto_correction).
B_VETO_WINDOWS_S = [(12e-6, 13e-6)]
HEIGHTS = [0, 200, 350, 425]

# Rossi-alpha settings (ticks)
BIN = 20                # correlation bin width
MAX_LAG = 40_000        # +/- lag window
FIT_MIN_LAG = 100       # skip |tau| below this: electronics ringing / dead time
FIT_MAX_LAG = 30_000
# Feynman-alpha settings
GATES = np.unique(np.logspace(np.log10(200), np.log10(200_000), 40).astype(int))
FEYN_MIN_GATE = 500
JACK_K = 10             # time segments for the delete-one-segment jackknife of Feynman fit errors


def ticks(s):
    return int(round(s / TICK_S))


def load(h, det):
    pattern = f"*R1-{h}-{det}.csv"
    files = sorted(glob.glob(os.path.join(HERE, pattern)))
    if not files:
        raise FileNotFoundError(f"no {pattern} in {HERE}")
    if len(files) > 1:
        raise ValueError(f"several files match {pattern}: {files}")
    t = np.loadtxt(files[0], dtype=np.int64, ndmin=1)
    if len(t) < 2 or np.any(np.diff(t) < 0):
        raise ValueError(f"{files[0]}: need at least 2 timestamps in non-decreasing order")
    return t


def veto_double_triggers(t, windows):
    """Drop every pulse that has *any* earlier raw pulse at a lag inside a (lo, hi) window (ticks,
    inclusive), so a double trigger is caught even when another pulse lies between it and its parent.
    Real pulses that happen to land in a window are dropped too; veto_correction() undoes that in Y."""
    drop = np.zeros(len(t), bool)
    for lo, hi in windows:
        drop |= np.searchsorted(t, t - lo, "right") > np.searchsorted(t, t - hi, "left")
    return t[~drop]


def veto_correction(raw_rate, windows):
    """Effect of veto_double_triggers on an auto-Y estimator, to first order in the fraction
    q = R w of real pulses it removes (R = raw, pre-veto rate per tick; windows of width w, centre d).
    A real pulse is lost when any raw pulse (real or double trigger) precedes it inside a window, so
    the vetoed train has no pairs at those lags, and more pulses are lost from gates with high counts:
        Y_vetoed(T) = (1 - 3q) Y(T) + shift(T),   shift(T) = -2 R w (1 - d/T).
    Returns (shift, 1 - 3q, q).  The factor only rescales Yinf.  A positive O(q^2) offset remains,
    which biases alpha from fits without a constant term once q is a few percent."""
    q = raw_rate * sum(hi - lo + 1 for lo, hi in windows)
    shift = lambda T: -2 * raw_rate * sum((hi - lo + 1) * (1 - (lo + hi) / 2 / np.asarray(T, float))
                                          for lo, hi in windows)
    return shift, 1 - 3 * q, q


def gate_counts(t, t0, T, n):
    """Counts of the sorted train t in the n consecutive gates [t0 + i T, t0 + (i+1) T)."""
    return np.diff(np.searchsorted(t, t0 + T * np.arange(n + 1))).astype(float)


def jack_masks(n):
    """Masks over n consecutive gates, each leaving out one of JACK_K contiguous time segments."""
    seg = np.arange(n) * JACK_K // n
    return [seg != k for k in range(JACK_K)]


def cross_correlation(a, b, dt, max_lag):
    """C[k] = number of (A,B) pairs with t_B - t_A in bin k, via FFT of binned series.
    Returns lag centres (ticks), pair counts, and the accidental expectation per bin:
    rate_A * rate_B * dt * L(tau), each rate over its own record and L(tau) the time over which an
    A pulse at t and a B pulse at t + tau can both have been recorded."""
    t0 = min(a[0], b[0])
    n = int((max(a[-1], b[-1]) - t0) // dt) + 1
    ha = np.bincount((a - t0) // dt, minlength=n).astype(float)
    hb = np.bincount((b - t0) // dt, minlength=n).astype(float)
    N = 1 << int(np.ceil(np.log2(2 * n)))
    c = np.fft.irfft(np.conj(np.fft.rfft(ha, N)) * np.fft.rfft(hb, N), N)
    K = int(max_lag // dt)
    k = np.arange(-K, K + 1)
    tau = k * dt
    L = np.clip(np.minimum(a[-1], b[-1] - tau) - np.maximum(a[0], b[0] - tau), 0, None)
    acc = len(a) / (a[-1] - a[0]) * len(b) / (b[-1] - b[0]) * dt * L
    return tau, np.rint(c[k % N]), acc


def _curve_fit(f, x, y, sig, p0):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", OptimizeWarning)
            return curve_fit(f, x, y, p0=p0, sigma=sig, absolute_sigma=True, maxfev=20000)
    except (RuntimeError, ValueError):
        return None, None


def fit_curve(f, x, y, sig, p0, y_jack=None):
    """Weighted least squares for a model f(x, amplitude, alpha, ...).  Returns (p, err, chi2/dof,
    flag), flag being 'ok' or the reason the result should not be used.  err is the fit error,
    inflated by sqrt(chi2/dof) when that exceeds 1, or, given y_jack (rows: y recomputed with one time
    segment of the data left out), the jackknife error, which also covers correlated points."""
    p, cov = _curve_fit(f, x, y, sig, p0)
    if p is None:
        nan = np.full(len(p0), np.nan)
        return nan, nan, np.nan, "fit_failed"
    chi2 = np.sum(((y - f(x, *p)) / sig) ** 2) / (len(x) - len(p))
    with np.errstate(invalid="ignore"):
        err = np.sqrt(np.diag(cov)) * np.sqrt(max(chi2, 1.0))
    if y_jack is not None:
        pj = [_curve_fit(f, x, yj, sig, p)[0] for yj in y_jack]
        if any(q is None for q in pj):
            err = np.full(len(p), np.nan)
        else:
            pj = np.array(pj)
            err = np.sqrt((len(pj) - 1) / len(pj) * np.sum((pj - pj.mean(0)) ** 2, 0))
    flag = ("no_error" if not np.all(np.isfinite(err)) else
            "amplitude<=0" if p[0] <= 0 else "alpha<=0" if p[1] <= 0 else
            "amplitude<2sigma" if p[0] < 2 * err[0] else "alpha_err>alpha" if err[1] > p[1] else "ok")
    return p, err, chi2, flag


def rossi_model(tau, A, alpha, C):
    return C + A * np.exp(-alpha * np.abs(tau) * TICK_S)


def fit_rossi(tau, c, acc):
    """Fit the coincidence rate normalized to the accidental level, so p[0]/p[2] = A/C."""
    m = (np.abs(tau) >= FIT_MIN_LAG) & (np.abs(tau) <= FIT_MAX_LAG)
    r, sig = c / acc, np.sqrt(np.maximum(c, 1.0)) / acc
    return fit_curve(rossi_model, tau[m], r[m], sig[m], [0.01, 500.0, 1.0]) + (m,)


def feynman_shape(T, Yinf, alpha, c):
    x = np.asarray(alpha * T * TICK_S, float)
    small = np.abs(x) < 1e-6
    xs = np.where(small, 1.0, x)
    with np.errstate(over="ignore", invalid="ignore"):              # alpha < 0 trial points in fits
        g = np.where(small, x / 2 - x ** 2 / 6, 1.0 + np.expm1(-xs) / xs)   # 1 - (1 - e^-x)/x
    return Yinf * g + c


def feynman_Y(t, gates):
    """Variance-to-mean Y(T) with error from the sample-4th-moment estimate, and its JACK_K
    delete-one-segment replicas (rows) for the jackknife; the same for feynman_cross/feynman_diff."""
    Y, dY, Yj = [], [], []
    for T in gates:
        n = gate_counts(t, t[0], T, (t[-1] - t[0]) // T)    # full gates only
        N, m = len(n), n.mean()
        d = n - m
        v = d @ d / (N - 1)
        m4 = np.mean(d ** 4)
        var_v = (m4 - v ** 2 * (N - 3) / (N - 1)) / N
        Y.append(v / m - 1.0)
        dY.append(np.sqrt(max(var_v, 0)) / m)
        Yj.append([np.var(n[s], ddof=1) / n[s].mean() - 1.0 for s in jack_masks(N)])
    return np.array(Y), np.array(dY), np.array(Yj).T


def feynman_cross(a, b, gates):
    """Cross Y: Cov(nA,nB)/sqrt(<nA><nB>) -- free of single-channel dead-time / afterpulsing."""
    t0 = max(a[0], b[0])
    Y, dY, Yj = [], [], []
    for T in gates:
        n = (min(a[-1], b[-1]) - t0) // T
        na, nb = gate_counts(a, t0, T, n), gate_counts(b, t0, T, n)
        da, db = na - na.mean(), nb - nb.mean()
        prod = da * db
        Y.append(prod.sum() / (n - 1) / np.sqrt(na.mean() * nb.mean()))
        dY.append(prod.std(ddof=1) / np.sqrt(n) / np.sqrt(na.mean() * nb.mean()))
        Yj.append([np.cov(na[s], nb[s])[0, 1] / np.sqrt(na[s].mean() * nb[s].mean()) for s in jack_masks(n)])
    return np.array(Y), np.array(dY), np.array(Yj).T


def fit_feynman(gates, Y, dY, Yj=None, gmin=FEYN_MIN_GATE, with_const=False):
    m = gates >= gmin
    if with_const:
        f, p0 = feynman_shape, [max(Y.max(), 1e-3), 500.0, 0.0]
    else:
        f = lambda T, Yinf, alpha: feynman_shape(T, Yinf, alpha, 0.0)
        p0 = [max(Y.max(), 1e-3), 500.0]
    return fit_curve(f, gates[m], Y[m], dY[m], p0, None if Yj is None else Yj[:, m]) + (f,)


def feynman_diff_shape(T, Yinf, alpha):
    """Adjacent-gate-difference estimator: Var(n_i - n_{i+1})/2m - 1 = 2Y(T) - Y(2T)."""
    with np.errstate(invalid="ignore"):
        return 2 * feynman_shape(T, Yinf, alpha, 0.0) - feynman_shape(2 * T, Yinf, alpha, 0.0)


def feynman_diff(a, b, gates):
    """Drift-suppressed Y from non-overlapping gate pairs. b=None: auto-Y of a; else cross-Y of a and b."""
    t0 = max(a[0], b[0]) if b is not None else a[0]
    t1 = min(a[-1], b[-1]) if b is not None else a[-1]
    Y, dY, Yj = [], [], []
    for T in gates:
        n = (t1 - t0) // (2 * T) * 2
        na = gate_counts(a, t0, T, n)
        sa, da = na[0::2] + na[1::2], na[0::2] - na[1::2]
        if b is None:
            Yfun = lambda s: np.mean(da[s] ** 2) / np.mean(sa[s]) - 1.0
            z = da ** 2 / 2 / na.mean()
        else:
            nb = gate_counts(b, t0, T, n)
            sb, db = nb[0::2] + nb[1::2], nb[0::2] - nb[1::2]
            Yfun = lambda s: np.mean(da[s] * db[s]) / np.sqrt(np.mean(sa[s]) * np.mean(sb[s]))
            z = da * db / 2 / np.sqrt(na.mean() * nb.mean())
        Y.append(Yfun(slice(None)))
        dY.append(z.std(ddof=1) / np.sqrt(len(z)))
        Yj.append([Yfun(s) for s in jack_masks(n // 2)])
    return np.array(Y), np.array(dY), np.array(Yj).T


def fit_feynman_diff(gates, Y, dY, Yj=None, gmin=FEYN_MIN_GATE):
    m = gates >= gmin
    return fit_curve(feynman_diff_shape, gates[m], Y[m], dY[m], [max(Y.max(), 1e-3), 500.0],
                     None if Yj is None else Yj[:, m])


def write_summary(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write("R1_mm,method,alpha_per_s,alpha_err,chi2_dof,amplitude,amplitude_kind,flag\n")
        for r in rows:
            fh.write(",".join(str(x) for x in r) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--veto", action="store_true",
                    help="remove channel-B double-trigger pulses (12-13 us after an earlier B pulse)")
    args = ap.parse_args()
    out = os.path.join(HERE, "noise_outputs_veto" if args.veto else "noise_outputs")
    os.makedirs(out, exist_ok=True)
    windows = [(ticks(lo), ticks(hi)) for lo, hi in B_VETO_WINDOWS_S]
    rows = []

    def report(h, method, p, e, chi2, flag, kind, amp):
        print(f"{method:16s}: alpha = {p[1]:8.1f} +/- {e[1]:.1f} 1/s   {kind} = {amp:.4f}   "
              f"chi2/dof = {chi2:.2f}" + ("" if flag == "ok" else f"   [{flag}]"))
        rows.append((h, method, p[1], e[1], chi2, amp, kind, flag))

    for h in HEIGHTS:
        try:
            a, b = load(h, "A"), load(h, "B")
        except (OSError, ValueError) as exc:
            print(f"\n=== R1 = {h} mm: skipped ({exc})")
            continue
        shift, scale = (lambda T: 0.0), 1.0      # auto-Y of vetoed B = scale * Y + shift(T)
        if args.veto:
            nb = len(b)
            shift, scale, q = veto_correction(nb / (b[-1] - b[0]), windows)
            b = veto_double_triggers(b, windows)
            print(f"[veto] removed {nb - len(b)} of {nb} B pulses; real-pulse loss q = {q:.4f}"
                  + ("  (q > 0.02: prefer feynman_B+c)" if q > 0.02 else ""))
        rate = lambda t: len(t) / ((t[-1] - t[0]) * TICK_S)
        overlap = (min(a[-1], b[-1]) - max(a[0], b[0])) * TICK_S
        print(f"\n=== R1 = {h} mm  (A: {len(a)} pulses {rate(a):.0f} cps, "
              f"B: {len(b)} pulses {rate(b):.0f} cps, A/B overlap {overlap:.1f} s)")
        if overlap <= 2 * GATES[-1] * TICK_S:
            print("A and B records do not overlap enough: skipped")
            continue

        # ---- Rossi-alpha: A x B cross-correlation (symmetric exponential)
        tau, c, acc = cross_correlation(a, b, BIN, MAX_LAG)
        p, e, chi2, flag, m = fit_rossi(tau, c, acc)
        report(h, "rossi_AxB", p, e, chi2, flag, "A/C", p[0] / p[2])

        r = c / acc
        ylo, yhi = np.percentile(r[m], [0.5, 99.5])
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.plot(tau * TICK_S * 1e3, r, ".", ms=2, alpha=0.5, label="A×B pairs / accidental")
        if flag != "fit_failed":
            yhi = max(yhi, rossi_model(FIT_MIN_LAG, *p))
            ax.plot(tau[m] * TICK_S * 1e3, rossi_model(tau[m], *p), "r-", lw=1.2,
                    label=f"fit α = {p[1]:.0f} ± {e[1]:.0f} s⁻¹" + ("" if flag == "ok" else f" [{flag}]"))
        pad = 0.15 * (yhi - ylo)
        ax.set(xlabel="τ = t_B − t_A (ms)", ylabel="normalized coincidence rate",
               title=f"Rossi-α cross-correlation, R1 = {h} mm", ylim=(ylo - pad, yhi + pad))
        ax.legend(); fig.tight_layout(); fig.savefig(f"{out}/rossi_{h}.png", dpi=150); plt.close(fig)

        # ---- Feynman-alpha: auto (A, B) and cross; the last fit listed for a channel is plotted
        fig, ax = plt.subplots(figsize=(7, 4))
        for label, (Y, dY, Yj), consts in [("A", feynman_Y(a, GATES), (False, True)),
                                           ("B", feynman_Y(b, GATES), (False, True)),
                                           ("AxB", feynman_cross(a, b, GATES), (False,))]:
            if label == "B":
                Y, dY, Yj = (Y - shift(GATES)) / scale, dY / scale, (Yj - shift(GATES)) / scale
            eb = ax.errorbar(GATES * TICK_S * 1e3, Y, dY, fmt=".", ms=4, label=label.replace("x", "×"))
            for wc in consts:
                p, e, chi2, flag, f = fit_feynman(GATES, Y, dY, Yj, with_const=wc)
                report(h, f"feynman_{label}{'+c' if wc else ''}", p, e, chi2, flag, "Yinf", p[0])
                if wc == consts[-1] and flag != "fit_failed":
                    ax.plot(GATES * TICK_S * 1e3, f(GATES, *p), "-", lw=1, color=eb[0].get_color())
        ax.set(xscale="log", xlabel="gate T (ms)", ylabel="Y(T)",
               title=f"Feynman-α, R1 = {h} mm")
        ax.legend(); fig.tight_layout(); fig.savefig(f"{out}/feynman_{h}.png", dpi=150); plt.close(fig)

        # ---- Feynman-alpha, drift-suppressed (adjacent-gate differences)
        fig, ax = plt.subplots(figsize=(7, 4))
        for label, (x, y) in [("A", (a, None)), ("B", (b, None)), ("AxB", (a, b))]:
            Y, dY, Yj = feynman_diff(x, y, GATES)
            if label == "B":
                sd = 2 * shift(GATES) - shift(2 * GATES)
                Y, dY, Yj = (Y - sd) / scale, dY / scale, (Yj - sd) / scale
            eb = ax.errorbar(GATES * TICK_S * 1e3, Y, dY, fmt=".", ms=4, label=label.replace("x", "×"))
            p, e, chi2, flag = fit_feynman_diff(GATES, Y, dY, Yj)
            report(h, f"feynman_diff_{label}", p, e, chi2, flag, "Yinf", p[0])
            if flag != "fit_failed":
                ax.plot(GATES * TICK_S * 1e3, feynman_diff_shape(GATES, *p), "-", lw=1,
                        color=eb[0].get_color())
        ax.set(xscale="log", xlabel="gate T (ms)", ylabel="Y_diff(T)",
               title=f"Feynman-α (adjacent-gate differences), R1 = {h} mm")
        ax.legend(); fig.tight_layout(); fig.savefig(f"{out}/feynman_diff_{h}.png", dpi=150); plt.close(fig)

        write_summary(f"{out}/alpha_summary.csv", rows)     # after every height, so a crash keeps results

    write_summary(f"{out}/alpha_summary.csv", rows)
    good = [r for r in rows if r[-1] == "ok"]
    fig, ax = plt.subplots(figsize=(6, 4))
    for meth in sorted({r[1] for r in good}):
        rr = [r for r in good if r[1] == meth]
        ax.errorbar([r[0] for r in rr], [r[2] for r in rr], [r[3] for r in rr], fmt="o-", ms=4, label=meth)
    ax.set(xlabel="R1 position (mm)", ylabel="α (1/s)", title="Prompt decay constant vs rod height")
    ax.legend(fontsize=7); fig.tight_layout(); fig.savefig(f"{out}/alpha_vs_rod.png", dpi=150); plt.close(fig)


if __name__ == "__main__":
    main()
