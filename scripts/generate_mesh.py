"""
Parametric Structured C-Grid Generator for NACA 0012 / NACA 2412 Airfoils.
Generates pure hexahedral (quad-extruded) C-grids compatible with gmshToFoam.
Grid levels:
  h3 (Coarse):        scale = 1.0   (~30,500 hex cells)
  h2 (Medium):        scale = 1.414 (~61,500 hex cells)
  h1 (Fine):          scale = 2.0   (~123,500 hex cells)
  wf (Wall Function): scale = 1.414 (~16,300 hex cells, 30 <= y+ <= 60)
"""

import sys
import numpy as np


def naca4_coordinates(code="0012", n_points=120, chord=1.0):
    m = float(code[0]) / 100.0
    p = float(code[1]) / 10.0
    t = float(code[2:]) / 100.0

    beta = np.linspace(0, np.pi, n_points)
    xc = 0.5 * (1.0 - np.cos(beta))

    # NASA TMR closed trailing edge definition
    yt = 5.0 * t * (
        0.2969 * np.sqrt(xc)
        - 0.1260 * xc
        - 0.3516 * (xc ** 2)
        + 0.2843 * (xc ** 3)
        - 0.1036 * (xc ** 4)
    )

    yc = np.zeros_like(xc)
    dyc_dx = np.zeros_like(xc)

    if m > 0.0 and p > 0.0:
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

    x_upper[0], y_upper[0] = 0.0, 0.0
    x_lower[0], y_lower[0] = 0.0, 0.0
    x_upper[-1], y_upper[-1] = chord, 0.0
    x_lower[-1], y_lower[-1] = chord, 0.0

    return x_upper, y_upper, x_lower, y_lower


def write_geo(filename, airfoil_code="0012", scale=1.0, wall_function=False):
    c = 1.0
    R = 20.0 * c          # Upstream and lateral radius (20c)
    L_wake = 25.0 * c     # Downstream wake distance (25c)
    span_z = 0.01 * c     # 1-cell extrusion in Z

    # Structured grid dimensioning
    N_foil = int(round(80 * scale))      # Nodes along airfoil
    N_wake = int(round(45 * scale))      # Nodes along wake line
    N_normal = int(round(125 * scale))   # Nodes in normal direction

    # Geometric progression factor calibrated for y+ <= 1.0 (dy1 ≈ 1.5e-5 m)
    prog_normal = 1.0 + (0.095 / scale)
    prog_wake = 1.0 + (0.045 / scale)
    prog_outlet = 1.0 + (0.025 / scale)

    if wall_function:
        # Calibrated for 30 <= y+ <= 60 (yp ≈ 2.0e-4 m, mean y+ ≈ 48)
        N_foil = 110
        N_wake = 55
        N_normal = 75
        prog_normal = 1.125
        prog_outlet = 1.060

    x_u, y_u, x_l, y_l = naca4_coordinates(airfoil_code, n_points=N_foil, chord=c)

    with open(filename, "w") as f:
        f.write("// Structured 2D C-Grid for MECH 501 Verification\n")
        f.write("Mesh.MshFileVersion = 2.2;\n\n")

        # 1. Primary Structural Domain Vertices
        f.write(f"Point(1) = {{{c:.7f}, 0.0, 0.0, 1.0}};\n")              # Airfoil TE
        f.write(f"Point(2) = {{0.0, 0.0, 0.0, 1.0}};\n")                  # Airfoil LE
        f.write(f"Point(3) = {{-{R}, 0.0, 0.0, 1.0}};\n")                 # Inflow center
        f.write(f"Point(4) = {{0.0, {R}, 0.0, 1.0}};\n")                  # Top arc end
        f.write(f"Point(5) = {{{c + L_wake}, {R}, 0.0, 1.0}};\n")         # Top-right outlet
        f.write(f"Point(6) = {{{c + L_wake}, 0.0, 0.0, 1.0}};\n")         # Wake outlet center
        f.write(f"Point(7) = {{{c + L_wake}, -{R}, 0.0, 1.0}};\n")        # Bottom-right outlet
        f.write(f"Point(8) = {{0.0, -{R}, 0.0, 1.0}};\n")                 # Bottom arc end

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

        # 4. Airfoil Splines (start at TE (1), end at LE (2))
        f.write(f"\nSpline(1) = {{{', '.join(map(str, upper_ids))}}};\n")
        f.write(f"Spline(2) = {{{', '.join(map(str, lower_ids))}}};\n")

        # 5. Shared Centerline & Wake Curves
        f.write("Line(3) = {2, 3};\n")       # Inflow centerline: LE -> Inlet
        f.write("Line(7) = {1, 6};\n")       # Wake centerline: TE -> Outlet

        # 6. Upper Domain Boundaries
        f.write("Circle(4) = {3, 2, 4};\n")  # Top arc (center at LE)
        f.write("Line(5) = {4, 5};\n")       # Top farfield line
        f.write("Line(6) = {6, 5};\n")       # Top outlet (center -> top)

        # 7. Lower Domain Boundaries
        f.write("Circle(8) = {3, 2, 8};\n")  # Bottom arc (center at LE)
        f.write("Line(9) = {8, 7};\n")       # Bottom farfield line
        f.write("Line(10) = {6, 7};\n")      # Bottom outlet (center -> bottom)

        # 8. Oriented Planar Surfaces (Top and Bottom Halves)
        f.write("\nLine Loop(1) = {3, 4, 5, -6, -7, 1};\n")
        f.write("Plane Surface(1) = {1};\n")

        f.write("Line Loop(2) = {3, 8, 9, -10, -7, 2};\n")
        f.write("Plane Surface(2) = {2};\n")

        # 9. Structured Transfinite Discretization
        f.write("\n// Transfinite Curves - Normal Direction (Progression to wall)\n")
        f.write(f"Transfinite Curve {{3}} = {N_normal} Using Progression {prog_normal:.5f};\n")
        f.write(f"Transfinite Curve {{6}} = {N_normal} Using Progression {prog_outlet:.5f};\n")
        f.write(f"Transfinite Curve {{10}} = {N_normal} Using Progression {prog_outlet:.5f};\n")

        f.write("\n// Transfinite Curves - Streamwise Direction (Natural cosine spline spacing)\n")
        f.write(f"Transfinite Curve {{1, 4}} = {N_foil};\n")
        f.write(f"Transfinite Curve {{2, 8}} = {N_foil};\n")
        f.write(f"Transfinite Curve {{7, 5}} = {N_wake} Using Progression {prog_wake:.5f};\n")
        f.write(f"Transfinite Curve {{9}} = {N_wake} Using Progression {prog_wake:.5f};\n")

        # 10. Recombine into Pure Quads
        f.write("\nTransfinite Surface{1} = {2, 3, 5, 6};\n")
        f.write("Recombine Surface{1};\n")
        f.write("Transfinite Surface{2} = {2, 3, 7, 6};\n")
        f.write("Recombine Surface{2};\n")

        # 11. 1-Cell Extrusion in Z for 2D OpenFOAM
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

        # Merge duplicate interface surfaces along Line 3 (inflow) and Line 7 (wake)
        f.write("// Remove duplicate internal interface surfaces\n")
        f.write("Coherence;\n\n")

        # 12. OpenFOAM Physical Patches
        f.write("Physical Volume(\"internalMesh\") = {out1[1], out2[1]};\n")
        f.write("Physical Surface(\"inlet\") = {out1[3], out1[4], out2[3], out2[4]};\n")
        f.write("Physical Surface(\"outlet\") = {out1[5], out2[5]};\n")
        f.write("Physical Surface(\"airfoil\") = {out1[7], out2[7]};\n")
        f.write("Physical Surface(\"frontAndBack\") = {1, 2, out1[0], out2[0]};\n")

    print(f"Generated structured {filename} (scale={scale}, airfoil={airfoil_code}, wf={wall_function})")


if __name__ == "__main__":
    lvl = sys.argv[1] if len(sys.argv) > 1 else "h3"
    af = sys.argv[2] if len(sys.argv) > 2 else "0012"
    scales = {"h3": 1.0, "h2": 1.414, "h1": 2.0, "wf": 1.414}
    write_geo(
        f"naca_{af}_{lvl}.geo",
        airfoil_code=af,
        scale=scales.get(lvl, 1.0),
        wall_function=(lvl == "wf"),
    )