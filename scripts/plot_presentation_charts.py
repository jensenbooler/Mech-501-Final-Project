import os
import numpy as np
import matplotlib.pyplot as plt

# Ensure output directory exists
os.makedirs("plots", exist_ok=True)

# Global styling for clean presentation slides
plt.rcParams.update({
    "font.size": 11.5,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11.5,
    "legend.fontsize": 10,
    "xtick.labelsize": 10.5,
    "ytick.labelsize": 10.5,
    "figure.dpi": 300,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--",
})

# Plot 1: Phase 1 ASME V&V 20 Grid Convergence (Cl and Cd vs. Grid Spacing h/h1)
def plot_phase1_gci():
    h_norm = np.array([1.0, np.sqrt(2), 2.0])  # h1, h2, h3
    labels = ["$h_1$ (Fine)\n123.5k", "$h_2$ (Med)\n61.6k", "$h_3$ (Coarse)\n30.5k"]

    cl_vals = np.array([0.403262, 0.391010, 0.395056])
    cd_vals = np.array([0.026992, 0.033308, 0.040999])

    cl_mean = 0.397136
    delta_osc = 0.006126
    cd_ext_formal = 0.020676

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))

    # Panel A: Lift Coefficient (Oscillatory)
    ax1.plot(h_norm, cl_vals, "o-", color="#1f77b4", linewidth=2.4, markersize=8.5, label="Simulated $C_l$")
    ax1.axhspan(cl_mean - delta_osc, cl_mean + delta_osc, color="#1f77b4", alpha=0.15,
                label="Oscillatory Envelope ($\\pm 1.52\\%$)")
    ax1.axhline(cl_mean, color="#1f77b4", linestyle=":", linewidth=1.4, label=f"Mean $C_l = {cl_mean:.4f}$")

    for x, y in zip(h_norm, cl_vals):
        offset = 0.0018 if y > cl_mean else -0.0030
        ax1.annotate(f"{y:.4f}", (x, y + offset), ha="center", fontsize=10, fontweight="bold")

    ax1.set_title("Lift Coefficient ($C_l$) — Oscillatory Convergence")
    ax1.set_xlabel("Normalized Grid Spacing ($h / h_1$)")
    ax1.set_ylabel("$C_l$")
    ax1.set_xticks(h_norm)
    ax1.set_xticklabels(labels)
    ax1.set_xlim(0.75, 2.2)
    ax1.set_ylim(0.382, 0.420)
    ax1.legend(loc="upper right", frameon=True, facecolor="white", framealpha=0.9)

    # Panel B: Drag Coefficient (Monotonic)
    C_formal = (cd_vals[1] - cd_vals[0]) / (h_norm[1]**2 - h_norm[0]**2)
    h_smooth = np.linspace(0.0, 2.05, 100)
    cd_smooth = cd_ext_formal + C_formal * (h_smooth**2)

    ax2.plot(h_smooth, cd_smooth, "--", color="#d62728", alpha=0.75, linewidth=1.8,
             label="Asymptotic Fit ($p_{\\mathrm{formal}} = 2.0$)")
    ax2.plot(h_norm, cd_vals, "s-", color="#d62728", linewidth=2.4, markersize=8.5, label="Simulated $C_d$")
    ax2.plot(0.0, cd_ext_formal, "*", color="#2ca02c", markersize=14, zorder=5,
             label=f"Infinite-Grid Extrapolation ($C_{{d,\\mathrm{{ext}}}} = {cd_ext_formal:.4f}$)")

    for x, y in zip(h_norm, cd_vals):
        ax2.annotate(f"{y:.4f}", (x, y + 0.0015), ha="center", fontsize=10, fontweight="bold")

    ax2.set_title("Total Drag ($C_d$) — Monotonic Decay ($R = +0.82$)")
    ax2.set_xlabel("Normalized Grid Spacing ($h / h_1$)")
    ax2.set_ylabel("$C_d$")
    ax2.set_xticks([0.0, 1.0, np.sqrt(2), 2.0])
    ax2.set_xticklabels(["$h \\to 0$\n(Exact)", "$h_1$ (Fine)\n123.5k", "$h_2$ (Med)\n61.6k", "$h_3$ (Coarse)\n30.5k"])
    ax2.set_xlim(-0.2, 2.2)
    ax2.set_ylim(0.017, 0.046)
    ax2.legend(loc="upper left", frameon=True, facecolor="white", framealpha=0.9)

    fig.suptitle("Phase 1: ASME V&V 20 Grid Convergence Verification (NACA 0012, $Re = 6\\times 10^6, \\alpha = 4^\\circ$)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig("plots/phase1_gci_convergence.png", bbox_inches="tight")
    plt.close()
    print("Saved plots/phase1_gci_convergence.png")

# Plot 2: Phase 2 Cost vs. Accuracy
def plot_phase2_cost_accuracy():
    cases = ["Case A\n$k$-$\\omega$ SST (WR)\n$y^+ = 0.93$",
             "Case B\nSpalart-Allmaras (WR)\n$y^+ = 0.24$",
             "Case C\n$k$-$\\omega$ SST (WF)\n$y^+ = 47.1$"]
    clock_min = [1785 / 60.0, 1277 / 60.0, 199 / 60.0]
    cells_k = [123.504, 123.504, 24.124]
    cl_vals = [0.4033, 0.4658, 0.4192]
    cd_vals = [0.02699, 0.00432, 0.02796]

    x = np.arange(len(cases))
    width = 0.34

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.8, 5.8))

    # Panel A: Computational Cost (Wall-Clock Minutes & Cell Count)
    bars = ax1.bar(x, clock_min, width=0.46, color=["#2b5c8f", "#4a89dc", "#2ca02c"],
                   edgecolor="black", linewidth=1.1, alpha=0.92)
    for bar, mins, cells in zip(bars, clock_min, cells_k):
        ax1.annotate(f"{mins:.1f} min\n({cells:.1f}k cells)",
                     xy=(bar.get_x() + bar.get_width() / 2, mins),
                     xytext=(0, 7), textcoords="offset points",
                     ha="center", va="bottom", fontsize=10.5, fontweight="bold")

    ax1.annotate("9.0x Speedup\n(-88.8% runtime)",
                 xy=(2, clock_min[2] + 8.5), ha="center", fontsize=10.5, fontweight="bold",
                 color="#1b7837", bbox=dict(boxstyle="round,pad=0.4", fc="#e5f5e0", ec="#2ca02c", lw=1.2))

    ax1.set_title("Computational Cost (Serial Wall-Clock Runtime)", pad=12)
    ax1.set_ylabel("Wall-Clock Time (Minutes)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(cases)
    ax1.set_ylim(0, 38)

    # Panel B: Aerodynamic Accuracy (Cl and Cd)
    ax2_twin = ax2.twinx()
    ax2_twin.grid(False)

    b1 = ax2.bar(x - width / 2, cl_vals, width, label="$C_l$ (Left Axis)",
                 color="#1f77b4", edgecolor="black", linewidth=1.1)
    b2 = ax2_twin.bar(x + width / 2, cd_vals, width, label="$C_d$ (Right Axis)",
                      color="#ff7f0e", edgecolor="black", linewidth=1.1)

    ax2.axhspan(0.44, 0.46, color="#1f77b4", alpha=0.14, label="NASA TMR / Wind Tunnel $C_l$ (~0.45)")

    for bar in b1:
        h = bar.get_height()
        ax2.annotate(f"{h:.4f}", (bar.get_x() + bar.get_width() / 2, h + 0.010),
                     ha="center", fontsize=9.8, fontweight="bold", color="#1f77b4")
    for bar in b2:
        h = bar.get_height()
        ax2_twin.annotate(f"{h:.5f}", (bar.get_x() + bar.get_width() / 2, h + 0.0009),
                          ha="center", fontsize=9.8, fontweight="bold", color="#c85a00")

    ax2.set_title("Aerodynamic Force Predictions ($C_l$ & $C_d$)", pad=12)
    ax2.set_ylabel("Lift Coefficient ($C_l$)", color="#1f77b4")
    ax2_twin.set_ylabel("Drag Coefficient ($C_d$)", color="#c85a00")
    ax2.set_xticks(x)
    ax2.set_xticklabels(cases)
    ax2.set_ylim(0, 0.58)
    ax2_twin.set_ylim(0, 0.037)

    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc="upper right", frameon=True, facecolor="white", framealpha=0.9)

    fig.suptitle("Phase 2: Turbulence Closure & Wall-Function Cost vs. Accuracy (NACA 0012, $\\alpha = 4^\\circ$)",
                 fontsize=14.5, fontweight="bold", y=1.02)
    plt.tight_layout(w_pad=3.0)
    plt.savefig("plots/phase2_cost_vs_accuracy.png", bbox_inches="tight")
    plt.close()
    print("Saved plots/phase2_cost_vs_accuracy.png")

# Plot 3: Unified Camber Comparison (Cases A-E)
def plot_phase2_camber_summary():
    cases = ["Case A\n0012 SST", "Case B\n0012 SA", "Case C\n0012 WF", "Case D\n2412 SST", "Case E\n2412 SA"]
    cl_vals = [0.4033, 0.4658, 0.4192, 0.6879, 0.7454]
    cm_vals = [0.00081, -0.00525, -0.00334, -0.05944, -0.06385]
    colors = ["#4c72b0", "#55a868", "#8172b3", "#dd8452", "#c44e52"]

    x = np.arange(len(cases))
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 4.8))

    # Panel A: Lift Coefficient
    bars1 = ax1.bar(x, cl_vals, width=0.52, color=colors, edgecolor="black", linewidth=1.1)
    for bar, val in zip(bars1, cl_vals):
        ax1.annotate(f"{val:.4f}", (bar.get_x() + bar.get_width() / 2, val + 0.015),
                     ha="center", fontsize=10, fontweight="bold")

    ax1.set_title("Lift Coefficient ($C_l$) — Symmetric vs. Cambered", pad=10)
    ax1.set_ylabel("Lift Coefficient ($C_l$)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(cases)
    ax1.set_ylim(0, 0.85)

    # Panel B: Pitching Moment
    bars2 = ax2.bar(x, cm_vals, width=0.52, color=colors, edgecolor="black", linewidth=1.1)
    ax2.axhline(0, color="black", linewidth=1.1)
    for bar, val in zip(bars2, cm_vals):
        offset = 0.0025 if val >= 0 else -0.0055
        ax2.annotate(f"{val:+.4f}", (bar.get_x() + bar.get_width() / 2, val + offset),
                     ha="center", fontsize=9.8, fontweight="bold")

    ax2.set_title("Pitching Moment ($C_{m,\\mathrm{pitch}}$) — Nose-Down Camber Shift", pad=10)
    ax2.set_ylabel("$C_{m,\\mathrm{pitch}}$")
    ax2.set_xticks(x)
    ax2.set_xticklabels(cases)
    ax2.set_ylim(-0.078, 0.014)

    fig.suptitle("Phase 2 Synthesis: Effect of 2% Camber (NACA 0012 vs. NACA 2412 at $\\alpha = 4^\\circ$)",
                 fontsize=14, fontweight="bold", y=1.02)
    plt.tight_layout(w_pad=2.5)
    plt.savefig("plots/phase2_camber_comparison.png", bbox_inches="tight")
    plt.close()
    print("Saved plots/phase2_camber_comparison.png")


if __name__ == "__main__":
    plot_phase1_gci()
    plot_phase2_cost_accuracy()
    plot_phase2_camber_summary()