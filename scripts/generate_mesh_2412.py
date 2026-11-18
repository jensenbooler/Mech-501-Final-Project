"""
Structured C-Grid Generator for NACA 2412 Airfoil (Phase 2 Camber Study).
Generates pure hexahedral (quad-extruded) C-grids compatible with gmshToFoam.
Default fine grid (h1, scale=2.0) produces 123,504 hex cells matching Phase 1 baseline.
"""

import sys
import numpy as np


def naca2412_coordinates(n_points=160, chord=1.0):
    m = 0.02   # Maximum camber (2%)
    p = 0.40   # Location of maximum camber (40% chord)
    t = 0.12   # Maximum thickness (12%)

    beta = np.linspace(0.0, np.pi, n_points)
    xc = 0.5 * (1.0 - np.cos(beta))

    # NASA TMR closed trailing-edge thickness distribution
    yt = 5.0 * t * (
        0.2969 * np.sqrt(xc)
        - 0.1260 * xc
        - 0.3516 * (xc ** 2)
        + 0.2843 * (xc ** 3)
        - 0.1036 * (xc ** 4)
    )

    yc = np.zeros_like(xc)
    dyc_dx = np.zeros_like(xc)

    idx_fwd = xc <= p
    idx_aft = xc > p

    yc[idx_fwd] = (m / (p ** 2)) * (2.0 * p * xc[idx_fwd] - xc[idx_fwd] ** 2)
    dyc_dx[idx_fwd] = (2.0 * m / (p ** 2)) * (p - xc[idx_fwd])

    yc[idx_aft] = (m / ((1.0 - p) ** 2)) * ((1.0 - 2.0 * p) + 2.0 * p * xc[idx_aft] - xc[idx_aft] ** 2)
    dyc_dx[idx_aft] = (2.0 * m / ((1.0 - p) ** 2)) * (p - xc[idx_aft])

    theta = np.arctan(dyc_dx)

    x_upper = chord * (xc - yt * np.sin(theta))
    y_upper = chord * (yc + yt * np.cos(theta))
    x_lower = chord * (xc + yt * np.sin(theta))
    y_lower = chord * (yc - yt * np.cos(theta))

    # Exact leading and trailing edge closure
    x_upper[0], y_upper[0] = 0.0, 0.0
    x_lower[0], y_lower[0] = 0.0, 0.0
    x_upper[-1], y_upper[-1] = chord, 0.0
    x_lower[-1], y_lower[-1] = chord, 0.0

    return x_upper, y_upper, x_lower, y_lower


def write_geo_2412(filename, scale=2.0):
    c = 1.0
    R = 20.0 * c          # Upstream and lateral radius (20c)
    L_wake = 25.0 * c     # Downstream wake distance (25c)
    span_z = 0.01 * c     # 1-cell extrusion in Z

    N_foil = int(round(80 * scale))      # 160 nodes along airfoil at scale=2.0
    N_wake = int(round(45 * scale))      # 90 nodes along wake line at scale=2.0
    N_normal = int(round(125 * scale))   # 250 nodes in normal direction at scale=2.0

    prog_normal = 1.0 + (0.095 / scale)
    prog_wake = 1.0 + (0.045 / scale)
    prog_outlet = 1.0 + (0.025 / scale)

    x_u, y_u, x_l, y_l = naca2412_coordinates(n_points=N_foil, chord=c)

    with open(filename, "w") as f:
        f.write("// Structured 2D C-Grid for NACA 2412 (MECH 501 Phase 2)\n")
        f.write("Mesh.MshFileVersion = 2.2;\n\n")

        # 1. Primary Domain Vertices
        f.write(f"Point(1) = {{{c:.7f}, 0.0, 0.0, 1.0}};\n")
        f.write("Point(2) = {0.0, 0.0, 0.0, 1.0};\n")
        f.write(f"Point(3) = {{-{R}, 0.0, 0.0, 1.0}};\n")
        f.write(f"Point(4) = {{0.0, {R}, 0.0, 1.0}};\n")
        f.write(f"Point(5) = {{{c + L_wake}, {R}, 0.0, 1.0}};\n")
        f.write(f"Point(6) = {{{c + L_wake}, 0.0, 0.0, 1.0}};\n")
        f.write(f"Point(7) = {{{c + L_wake}, -{R}, 0.0, 1.0}};\n")
        f.write(f"Point(8) = {{0.0, -{R}, 0.0, 1.0}};\n")

        # 2. Upper Airfoil Surface Points (TE -> LE)
        upper_ids = [1]
        pt = 100
        for x, y in zip(reversed(x_u[1:-1]), reversed(y_u[1:-1])):
            f.write(f"Point({pt}) = {{{x:.7f}, {y:.7f}, 0.0, 1.0}};\n")
            upper_ids.append(pt)
            pt += 1
        upper_ids.append(2)

        # 3. Lower Airfoil Surface Points (TE -> LE)
        lower_ids = [1]
        pt = 300
        for x, y in zip(reversed(x_l[1:-1]), reversed(y_l[1:-1])):
            f.write(f"Point({pt}) = {{{x:.7f}, {y:.7f}, 0.0, 1.0}};\n")
            lower_ids.append(pt)
            pt += 1
        lower_ids.append(2)

        # 4. Airfoil Splines
        f.write(f"\nSpline(1) = {{{', '.join(map(str, upper_ids))}}};\n")
        f.write(f"Spline(2) = {{{', '.join(map(str, lower_ids))}}};\n")

        # 5. Centerline & Wake Curves
        f.write("Line(3) = {2, 3};\n")
        f.write("Line(7) = {1, 6};\n")

        # 6. Upper Domain Boundaries
        f.write("Circle(4) = {3, 2, 4};\n")
        f.write("Line(5) = {4, 5};\n")
        f.write("Line(6) = {6, 5};\n")

        # 7. Lower Domain Boundaries
        f.write("Circle(8) = {3, 2, 8};\n")
        f.write("Line(9) = {8, 7};\n")
        f.write("Line(10) = {6, 7};\n")

        # 8. Planar Surfaces
        f.write("\nLine Loop(1) = {3, 4, 5, -6, -7, 1};\n")
        f.write("Plane Surface(1) = {1};\n")

        f.write("Line Loop(2) = {3, 8, 9, -10, -7, 2};\n")
        f.write("Plane Surface(2) = {2};\n")

        # 9. Structured Transfinite Curves
        f.write("\nTransfinite Curve {3} = " + f"{N_normal} Using Progression {prog_normal:.5f};\n")
        f.write(f"Transfinite Curve {{6}} = {N_normal} Using Progression {prog_outlet:.5f};\n")
        f.write(f"Transfinite Curve {{10}} = {N_normal} Using Progression {prog_outlet:.5f};\n")

        f.write(f"Transfinite Curve {{1, 4}} = {N_foil};\n")
        f.write(f"Transfinite Curve {{2, 8}} = {N_foil};\n")
        f.write(f"Transfinite Curve {{7, 5}} = {N_wake} Using Progression {prog_wake:.5f};\n")
        f.write(f"Transfinite Curve {{9}} = {N_wake} Using Progression {prog_wake:.5f};\n")

        # 10. Recombine into Pure Quads
        f.write("\nTransfinite Surface{1} = {2, 3, 5, 6};\n")
        f.write("Recombine Surface{1};\n")
        f.write("Transfinite Surface{2} = {2, 3, 7, 6};\n")
        f.write("Recombine Surface{2};\n")

        # 11. 1-Cell Z-Extrusion
        f.write(f"\nout1[] = Extrude {{0, 0, {span_z}}} {{\n")
        f.write("  Surface{1};\n")
        f.write("  Layers{1};\n")
        f.write("  Recombine;\n")
        f.write("};\n\n")

        f.write(f"out2[] = Extrude {{0, 0, {span_z}}} {{\n")
        f.write("  Surface{2};\n")
        f.write("  Layers{1};\n")
        f.write("  Recombine;\n")
        f.write("};\n\n")

        f.write("Coherence;\n\n")

        # 12. OpenFOAM Physical Patches
        f.write("Physical Volume(\"internalMesh\") = {out1[1], out2[1]};\n")
        f.write("Physical Surface(\"inlet\") = {out1[3], out1[4], out2[3], out2[4]};\n")
        f.write("Physical Surface(\"outlet\") = {out1[5], out2[5]};\n")
        f.write("Physical Surface(\"airfoil\") = {out1[7], out2[7]};\n")
        f.write("Physical Surface(\"frontAndBack\") = {1, 2, out1[0], out2[0]};\n")

    print(f"Generated {filename} (NACA 2412, scale={scale})")


if __name__ == "__main__":
    lvl = sys.argv[1] if len(sys.argv) > 1 else "h1"
    scales = {"h3": 1.0, "h2": 1.414, "h1": 2.0}
    write_geo_2412(f"naca_2412_{lvl}.geo", scale=scales.get(lvl, 2.0))