import numpy as np
import matplotlib.pyplot as plt

def naca4(code, n_pts=400):
    m = int(code[0]) / 100.0
    p = int(code[1]) / 10.0
    t = int(code[2:]) / 100.0

    # Cosine spacing for sharp leading-edge resolution
    beta = np.linspace(0, np.pi, n_pts)
    x = 0.5 * (1.0 - np.cos(beta))

    # Closed trailing-edge thickness distribution
    yt = 5.0 * t * (
        0.2969 * np.sqrt(x)
        - 0.1260 * x
        - 0.3516 * x**2
        + 0.2843 * x**3
        - 0.1036 * x**4
    )

    if m == 0 or p == 0:
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
    else:
        yc = np.where(
            x < p,
            (m / p**2) * (2 * p * x - x**2),
            (m / (1 - p)**2) * ((1 - 2 * p) + 2 * p * x - x**2),
        )
        dyc_dx = np.where(
            x < p,
            (2 * m / p**2) * (p - x),
            (2 * m / (1 - p)**2) * (p - x),
        )

    theta = np.arctan(dyc_dx)
    xu, yu = x - yt * np.sin(theta), yc + yt * np.cos(theta)
    xl, yl = x + yt * np.sin(theta), yc - yt * np.cos(theta)

    x_airfoil = np.concatenate([xu[::-1], xl[1:]])
    y_airfoil = np.concatenate([yu[::-1], yl[1:]])
    return x, yc, x_airfoil, y_airfoil

x0, yc0, xa0, ya0 = naca4("0012")
x2, yc2, xa2, ya2 = naca4("2412")

fig, ax = plt.subplots(figsize=(8.5, 3.0), dpi=300)

# Chord line
ax.axhline(0, color="gray", linestyle=":", linewidth=1.0, label="Chord line ($y/c = 0$)")

# NACA 0012
ax.plot(xa0, ya0, color="#2b5c8f", linewidth=2.0, label="NACA 0012 (Symmetric)")
ax.fill(xa0, ya0, color="#2b5c8f", alpha=0.08)

# NACA 2412 + mean camber line
ax.plot(xa2, ya2, color="#c0392b", linestyle="--", linewidth=2.0, label="NACA 2412 (2% camber)")
ax.plot(x2, yc2, color="#c0392b", linestyle="-.", linewidth=1.2, label="Mean camber line")

# Annotate max camber point shifted left away from legend
ax.plot(0.4, 0.02, "o", color="#c0392b", markersize=5)
ax.annotate(
    "Max camber: $2\\%c$ at $x/c = 0.40$",
    xy=(0.4, 0.02),
    xytext=(0.33, 0.105),
    fontsize=8.5,
    color="#c0392b",
    fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#c0392b", lw=1.0),
)

# Flow regime annotation box
ax.text(
    0.02, -0.105,
    r"Test Conditions: $Re_c = 6 \times 10^6$, $\alpha = 4^\circ$, Incompressible RANS (WR \(WR \($y^+ < 1$) WF) WF)",
    fontsize=8.5,
    bbox=dict(boxstyle="round,pad=0.3", facecolor="#f4f6f7", edgecolor="#bdc3c7"),
)

ax.set_aspect("equal")
ax.set_xlim(-0.03, 1.03)
ax.set_ylim(-0.13, 0.145)
ax.set_xlabel("Normalized Chord ($x/c$)", fontsize=10)
ax.set_ylabel("$y/c$", fontsize=10)
ax.set_title("Airfoil Geometry Comparison: Symmetric NACA 0012 vs. Cambered NACA 2412", fontsize=11, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.35)

# Compact legend
ax.legend(
    loc="upper right",
    fontsize=7.0,
    framealpha=0.95,
    labelspacing=0.25,
    handlelength=1.6,
    handletextpad=0.5,
    borderpad=0.35,
)

plt.tight_layout()
plt.savefig("naca_profiles.pdf")
plt.savefig("naca_profiles.png")
print("Saved naca_profiles.pdf and naca_profiles.png")