import glob, numpy as np, matplotlib.pyplot as plt

def load_cp(pattern):
    f = sorted(glob.glob(pattern))[-1]
    d = np.loadtxt(f, comments="#")
    x, y, cp = d[:, 0], d[:, 1], 2.0 * d[:, 3]
    yc = np.where(x <= 0.4, 0.125*(0.8*x - x**2), (0.02/0.36)*(0.2 + 0.8*x - x**2))
    up, lo = y >= yc, y < yc
    return x[up][np.argsort(x[up])], cp[up][np.argsort(x[up])], x[lo][np.argsort(x[lo])], cp[lo][np.argsort(x[lo])]

plt.figure(figsize=(8, 5))
for pat, lbl, col, ls in [
    ("runs/naca2412_sst_h1/postProcessing/surfaces/*/p_airfoil.raw", "NACA 2412 - k-omega SST (Case D)", "tab:blue", "-"),
    ("runs/naca2412_sa_h1/postProcessing/surfaces/*/p_airfoil.raw", "NACA 2412 - Spalart-Allmaras (Case E)", "tab:red", "--")]:
    xu, cpu, xl, cpl = load_cp(pat)
    plt.plot(xu, cpu, color=col, linestyle=ls, label=lbl)
    plt.plot(xl, cpl, color=col, linestyle=ls)
plt.gca().invert_yaxis()
plt.xlabel("x/c"); plt.ylabel("Cp"); plt.title("NACA 2412 Surface Pressure Distribution (Re = 6e6, alpha = 4 deg)")
plt.grid(True, alpha=0.3); plt.legend(); plt.tight_layout()
plt.savefig("plots/phase2_cp_comparison.png", dpi=300)
print("Saved plots/phase2_cp_comparison.png")
