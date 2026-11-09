#!/usr/bin/env python3
import os
import sys
import numpy as np

def compute_yplus(case_dir, time_dir, nu=1.666667e-07, yp=3.75e-06):
    file_path = os.path.join(case_dir, str(time_dir), "wallShearStress")
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    with open(file_path, "r") as f:
        lines = f.readlines()

    in_airfoil = False
    stresses = []
    for line in lines:
        if "airfoil" in line and "patch" not in line and "{" not in line:
            in_airfoil = True
            continue
        if in_airfoil:
            if "}" in line:
                break
            line_str = line.strip()
            if line_str.startswith("(") and line_str.endswith(")"):
                parts = line_str.replace("(", "").replace(")", "").split()
                if len(parts) == 3:
                    try:
                        tau_x = float(parts[0])
                        tau_y = float(parts[1])
                        mag_tau = np.sqrt(tau_x**2 + tau_y**2)
                        stresses.append(mag_tau)
                    except ValueError:
                        continue

    if not stresses:
        print(f"Warning: Could not parse airfoil shear stress in {file_path}")
        return

    tau_w = np.array(stresses)
    u_tau = np.sqrt(tau_w)
    y_plus = u_tau * yp / nu

    print(f"=== Wall Resolution Metrics: {case_dir} (Time = {time_dir}) ===")
    print(f"  First cell centroid (yp): {yp:.3e} m")
    print(f"  Kinematic viscosity (nu): {nu:.3e} m^2/s")
    print(f"  Airfoil boundary faces:   {len(y_plus)}")
    print(f"  Min   tau_w/rho = {np.min(tau_w):.6e} m^2/s^2  --> Min   y+ = {np.min(y_plus):.4f}")
    print(f"  Max   tau_w/rho = {np.max(tau_w):.6e} m^2/s^2  --> Max   y+ = {np.max(y_plus):.4f}")
    print(f"  Mean  tau_w/rho = {np.mean(tau_w):.6e} m^2/s^2  --> Mean  y+ = {np.mean(y_plus):.4f}")

if __name__ == "__main__":
    case = sys.argv[1] if len(sys.argv) > 1 else "runs/naca0012_h1"
    time = sys.argv[2] if len(sys.argv) > 2 else "2500"
    yp_val = float(sys.argv[3]) if len(sys.argv) > 3 else 3.75e-06
    compute_yplus(case, time, yp=yp_val)