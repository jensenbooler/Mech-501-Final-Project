# MECH 501: Final Project — Aerodynamic Verification & Validation
**Authors:** Vincenzo Bigattini & Jensen Booler  
**Case:** NACA 0012 Verification & Camber Study  
**Conditions:** $Re_c = 6.0 \times 10^6$, Incompressible ($U_\infty = 1.0\text{ m/s}$), $\alpha = 4.0^\circ$  

---

## Phase 1: Grid Convergence & Numerical Verification (GCI)

### 1. Structured C-Grid Hierarchy & Wall Resolution
Spatial refinement follows a constant grid ratio $r = \sqrt{2} \approx 1.414$, satisfying ASME V&V 20 guidelines. Wall resolution metrics were evaluated directly from converged wall shear stress fields $\tau_w$:

| Grid Level | Mesh File | Hex Cells | Refinement Ratio ($r$) | First Cell ($\Delta y_1$) | Mean $y^+$ | Max $y^+$ | Wall Resolution |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **$h_3$ (Coarse)** | `naca_0012_h3.msh` | 30,504 | Baseline | $1.50 \times 10^{-5}\text{ m}$ | 1.82 | 3.72 | Buffer Layer |
| **$h_2$ (Medium)** | `naca_0012_h2.msh` | 61,600 | 1.414 | $1.06 \times 10^{-5}\text{ m}$ | 1.31 | 2.81 | Buffer / Sublayer |
| **$h_1$ (Fine)**   | `naca_0012_h1.msh` | 123,504 | 1.414 | $0.75 \times 10^{-5}\text{ m}$ | **0.93** | 2.11 | **Sublayer Resolved** |

---

### 2. Aerodynamic Force Coefficients
Simulations were computed with steady-state `simpleFoam` using the wall-resolved $k-\omega$ SST model. Aerodynamic forces were monitored via the `forceCoeffs` function object:

| Grid Level | Iterations | $C_l$ (Lift) | $C_d$ (Total Drag) | $C_{m,\text{pitch}}$ | Convergence State |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$h_3$ (Coarse)** | 2,500 | 0.395056 | 0.040999 | -0.002279 | Residuals $< 10^{-6}$ |
| **$h_2$ (Medium)** | 5,000 | 0.391010 | 0.033308 | -0.000370 | Residuals $< 10^{-5}$ |
| **$h_1$ (Fine)**   | 2,500 | 0.403262 | 0.026992 | 0.000810 | Monotonic Drag Decay |

---

### 3. Numerical Stabilization & Grid Sequencing Protocol
To eliminate startup floating-point exceptions (`sigFpe`) on refined wall-resolved meshes ($y^+ \le 1$):
1. **Under-Relaxation:** Tightened in `system/fvSolution` ($p = 0.2, U = k = \omega = 0.5$, `nNonOrthogonalCorrectors 2;`).
2. **Gradient Limiters:** Applied `cellLimited Gauss linear 1;` in `system/fvSchemes` for velocity and turbulence transport.
3. **Grid Sequencing:** Refined grids were initialized via field mapping from converged coarser solutions:
   ```bash
   mapFields ../naca0012_h2 -sourceTime 5000 -consistent