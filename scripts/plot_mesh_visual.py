import os
import re
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

def parse_openfoam_list(filepath):
    # Strips OpenFOAM header/comments and returns the body inside
    with open(filepath, "r") as f:
        text = f.read()
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    text = re.sub(r"//.*", "", text)
    match = re.search(r"(\d+)\s*\(", text)
    if not match:
        raise ValueError(f"Could not parse list count in {filepath}")
    count = int(match.group(1))
    start = match.end()
    return count, text[start:]

def load_openfoam_2d_edges(polymesh_dir):
    # 1. Parse points
    n_pts, pts_text = parse_openfoam_list(os.path.join(polymesh_dir, "points"))
    raw_pts = re.findall(r"\(\s*([eE0-9.+\-]+)\s+([eE0-9.+\-]+)\s+([eE0-9.+\-]+)\s*\)", pts_text)
    points = [(float(x), float(y), float(z)) for x, y, z in raw_pts[:n_pts]]

    # 2. Parse faces
    n_faces, faces_text = parse_openfoam_list(os.path.join(polymesh_dir, "faces"))
    raw_faces = re.findall(r"(\d+)\s*\(([^)]+)\)", faces_text)
    
    segments = []
    for count_str, indices_str in raw_faces[:n_faces]:
        if int(count_str) == 4:
            idxs = [int(i) for i in indices_str.split()]
            pts = [points[i] for i in idxs]
            # Keep only the z > 0 symmetry plane (frontAndBack)
            if all(p[2] > 0 for p in pts):
                for j in range(4):
                    p1 = (pts[j][0], pts[j][1])
                    p2 = (pts[(j + 1) % 4][0], pts[(j + 1) % 4][1])
                    segments.append([p1, p2])
    return segments

print("Reading h1 wall-resolved mesh...")
seg_h1 = load_openfoam_2d_edges("runs/naca0012_h1/constant/polyMesh")
print(f"Loaded {len(seg_h1)} edges for h1.")

print("Reading wf wall-function mesh...")
seg_wf = load_openfoam_2d_edges("runs/naca0012_sst_wf/constant/polyMesh")
print(f"Loaded {len(seg_wf)} edges for wf.")

fig, axes = plt.subplots(1, 2, figsize=(12.5, 4.8), dpi=300)

# Panel 1: Wall-Resolved h1 Leading Edge Zoom
axes[0].add_collection(LineCollection(seg_h1, colors="#1f77b4", linewidths=0.28))
axes[0].set_xlim(-0.04, 0.25)
axes[0].set_ylim(-0.08, 0.12)
axes[0].set_aspect("equal")
axes[0].set_title("Wall-Resolved $h_1$ (123.5k cells, Mean $y^+ = 0.93$)", fontweight="bold", pad=10)
axes[0].set_xlabel("$x / c$")
axes[0].set_ylabel("$y / c$")

# Panel 2: Wall-Function wf Leading Edge Zoom
axes[1].add_collection(LineCollection(seg_wf, colors="#2ca02c", linewidths=0.50))
axes[1].set_xlim(-0.04, 0.25)
axes[1].set_ylim(-0.08, 0.12)
axes[1].set_aspect("equal")
axes[1].set_title("Wall-Function Grid (24.1k cells, Mean $y^+ = 47.1$)", fontweight="bold", pad=10)
axes[1].set_xlabel("$x / c$")
axes[1].set_ylabel("$y / c$")

plt.suptitle("Near-Wall Mesh Resolution Comparison (NACA 0012 Leading Edge)", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout(w_pad=2.5)
os.makedirs("plots", exist_ok=True)
plt.savefig("plots/mesh_topology_comparison.png", bbox_inches="tight")
print("Saved plots/mesh_topology_comparison.png")