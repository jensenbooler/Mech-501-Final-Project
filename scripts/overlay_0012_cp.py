import os
import xml.etree.ElementTree as ET
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

# 1. Locate Jensen's existing PNG on main
img_path = (
    "plots/phase2_cp_comparison.png"
    if os.path.exists("plots/phase2_cp_comparison.png")
    else "figures/phase2_cp_comparison.png"
)
out_path = "plots/phase2_cp_comparison_with_0012.png"

# 2. Parse NACA 0012 (Case A: k-omega SST) ASCII VTK surface
root = ET.parse("runs/naca0012_h1/VTK/naca0012_h1_2500/boundary/airfoil.vtp").getroot()
piece = root.find(".//Piece")
pts = np.fromstring(piece.find("Points/DataArray").text, sep=" ").reshape(-1, 3)
p_arr = piece.find("PointData/DataArray[@Name='p']")

if p_arr is None:
    p = np.fromstring(piece.find("CellData/DataArray[@Name='p']").text, sep=" ")
    conn = np.fromstring(piece.find("Polys/DataArray[@Name='connectivity']").text, sep=" ", dtype=int)
    offs = np.fromstring(piece.find("Polys/DataArray[@Name='offsets']").text, sep=" ", dtype=int)
    starts = np.r_[0, offs[:-1]]
    pts = np.array([pts[conn[s:e]].mean(axis=0) for s, e in zip(starts, offs)])
else:
    p = np.fromstring(p_arr.text, sep=" ")

xy = np.round(pts[:, :2], 7)
uniq_xy, inv = np.unique(xy, axis=0, return_inverse=True)
p_mean = np.bincount(inv, weights=p) / np.bincount(inv)

x, y, cp = uniq_xy[:, 0], uniq_xy[:, 1], 2.0 * p_mean
up, lo = y >= 0.0, y < 0.0
xu, cpu = x[up][np.argsort(x[up])], cp[up][np.argsort(x[up])]
xl, cpl = x[lo][np.argsort(x[lo])], cp[lo][np.argsort(x[lo])]

# 3. Auto-detect exact black axes border and erase Jensen's old legend right up to the border
img = mpimg.imread(img_path).copy()
h, w = img.shape[:2]
gray = img[:, :, :3].mean(axis=2)

# Find exact pixel row/column of the black top and right axes spines (avoiding the title region)
col_spine = int(0.95 * w) + np.argmin(gray[int(0.50 * h), int(0.95 * w) : int(0.99 * w)])
row_top_spine = int(0.065 * h) + np.argmin(gray[int(0.065 * h) : int(0.105 * h), int(0.25 * w)])

# Copy a clean 1-pixel-tall horizontal strip (with exact vertical grid lines) from y = 0.245*h over the old legend
y_top = row_top_spine + 3
y_bot = int(0.220 * h)
x_left = int(0.550 * w)
x_right = col_spine - 2  # stops cleanly inside the anti-aliased right black border
clean_row = img[int(0.245 * h) : int(0.245 * h) + 1, x_left:x_right, :]
img[y_top:y_bot, x_left:x_right, :] = clean_row

# Restore the horizontal y = -1.5 grid line across that same x-range using its clean left segment
row_m15 = int(0.12 * h) + np.argmin(gray[int(0.12 * h) : int(0.18 * h), int(0.30 * w)])
img[row_m15 - 1 : row_m15 + 2, x_left:x_right, :] = img[
    row_m15 - 1 : row_m15 + 2, int(0.30 * w) : int(0.30 * w) + (x_right - x_left), :
]

fig = plt.figure(figsize=(w / 200, h / 200), dpi=200)
ax_bg = fig.add_axes([0, 0, 1, 1])
ax_bg.imshow(img)
ax_bg.axis("off")

# Mask old title cleanly above the top axes spine
ax_bg.add_patch(
    Rectangle((0.12 * w, 0.005 * h), 0.80 * w, row_top_spine - 0.010 * h, facecolor="white", edgecolor="none", zorder=2)
)

# Overlay axis aligned to x/c = [0.0, 1.0] and Cp = [-1.7, 1.6]
ax = fig.add_axes([0.0975, 0.118, 0.874, 0.812], frameon=False)
ax.set_xlim(-0.048, 1.048)
ax.set_ylim(1.56, -1.76)
ax.set_xticks([])
ax.set_yticks([])

# Plot NACA 0012 (Case A)
ax.plot(xu, cpu, color="tab:green", linestyle="-.", linewidth=2.0, zorder=4)
ax.plot(xl, cpl, color="tab:green", linestyle="-.", linewidth=2.0, zorder=4)

# Unified 3-curve legend
handles = [
    Line2D([0], [0], color="tab:blue", linestyle="-", linewidth=1.8, label="NACA 2412 - k-omega SST (Case D)"),
    Line2D([0], [0], color="tab:red", linestyle="--", linewidth=1.8, label="NACA 2412 - Spalart-Allmaras (Case E)"),
    Line2D([0], [0], color="tab:green", linestyle="-.", linewidth=2.0, label="NACA 0012 - k-omega SST (Case A)"),
]
leg = ax.legend(
    handles=handles,
    loc="upper right",
    bbox_to_anchor=(0.996, 0.988),
    frameon=True,
    facecolor="white",
    framealpha=1.0,
    fontsize=10.0,
    handlelength=2.2,
    borderpad=0.5,
)
leg.get_frame().set_edgecolor("#cccccc")

# Clean updated title
ax_bg.text(
    0.535 * w,
    0.036 * h,
    "Surface Pressure Distribution: NACA 0012 vs. NACA 2412 (Re = 6e6, alpha = 4 deg)",
    ha="center",
    va="center",
    fontsize=11.5,
    color="black",
    zorder=5,
)

os.makedirs("plots", exist_ok=True)
fig.savefig(out_path, dpi=200, bbox_inches="tight", pad_inches=0.06)
print(f"Saved {out_path}")