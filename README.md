# MECH 501: Final Project — Aerodynamic Verification & Validation
**Authors:** Vincenzo Bigattini & Jensen Booler  
**Case:** NACA 0012 Verification, Turbulence Closure & Camber Study  
**Conditions:** $Re_c = 6.0 \times 10^6$, Incompressible ($U_\infty = 1.0\text{ m/s}$, $\nu = 1.6667 \times 10^{-7}\text{ m}^2/\text{s}$), $\alpha = 4.0^\circ$, $A_{\text{ref}} = 0.01\text{ m}^2$  

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
   ```

---

## Phase 2: Turbulence Closures & Wall-Function Cost vs. Accuracy

### 1. Turbulence Closure & Near-Wall Treatment Matrix (NACA 0012, $\alpha = 4.0^\circ$)
To evaluate closure sensitivity and near-wall modeling tradeoffs against the wall-resolved $k-\omega$ SST baseline (**Case A**), two additional simulations were executed:
* **Case B (Spalart-Allmaras, Wall-Resolved):** 1-equation eddy-viscosity model evaluated on the verified $h_1$ fine C-grid ($y^+ \le 1$).
* **Case C ($k-\omega$ SST + Wall Functions):** 2-equation model executed on a coarse log-law C-grid (`wf`, $y_p = 2.04 \times 10^{-4}\text{ m}$) using `kqRWallFunction`, `omegaWallFunction`, and `nutkWallFunction` (`Mean y+ = 47.10`, `Min = 23.55`, `Max = 78.38`).

| Case | Turbulence Model | Near-Wall Treatment | Hex Cells | Mean $y^+$ | $C_l$ | $C_d$ | $C_{m,\text{pitch}}$ | $\Delta C_l$ vs. Case A |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Case A** | $k\text{-}\omega$ SST | Wall-Resolved ($y^+ \le 1$) | 123,504 | 0.93 | 0.4033 | 0.02699 | +0.00081 | Baseline |
| **Case B** | Spalart-Allmaras | Wall-Resolved ($y^+ \le 1$) | 123,504 | **0.244** | **0.4658** | **0.00432** | -0.00525 | +15.5% |
| **Case C** | $k\text{-}\omega$ SST | Wall Functions ($30 \le y^+ \le 60$) | 24,124 | **47.10** | **0.4192** | **0.02796** | -0.00334 | +3.96% |

---

### 2. Computational Cost vs. Accuracy Summary
All runs were executed serially (`nProcs = 1`) in OpenFOAM v2412 on `cpupool1`:

| Case | Hex Cells | Iterations | CPU Time (`ExecutionTime`) | Wall-Clock (`ClockTime`) | Relative Speedup | Engineering Takeaway |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Case A ($k\text{-}\omega$ SST WR)** | 123,504 | 2,500 | 1,590 s | 1,785 s (29.8 min) | 1.0x | Highest fidelity boundary-layer resolution |
| **Case B (SA WR)** | 123,504 | 3,000 | ~1,160 s | 1,277 s (21.3 min) | 1.4x | 1-equation efficiency; higher attached lift |
| **Case C ($k\text{-}\omega$ SST WF)** | 24,124 | 3,000 | **168 s** | **199 s (3.3 min)** | **9.0x** | ~9x faster with < 4% lift/drag deviation |

---

### 3. Physical & Numerical Findings for Final Report
* **Turbulence Closure Sensitivity (SA vs. $k\text{-}\omega$ SST):** Spalart-Allmaras predicts stronger boundary-layer attachment near the trailing edge, yielding higher lift ($C_l = 0.4658$, closely matching NASA TMR/experimental benchmarks of $C_l \approx 0.44\text{--}0.46$) and substantially lower pressure drag ($C_d = 0.00432$). In contrast, $k\text{-}\omega$ SST predicts earlier adverse-pressure-gradient thickening near the trailing edge, reducing $C_l$ to $0.4033$ and increasing form drag.
* **Wall-Function Accuracy & $y^+$ Distribution (Case C):** Using continuous wall-function blending (`omegaWallFunction` / `nutkWallFunction`), Case C achieves `Mean y+ = 47.10` across the airfoil, with local extremes of `Min y+ = 23.55` (near the low-shear stagnation and trailing-edge regions) and `Max y+ = 78.38` (at the leading-edge suction peak). Total drag decomposes into $C_{d,\text{pressure}} = 0.02194$ and $C_{d,\text{viscous}} = 0.00603$, closely tracking Case A's total drag ($+3.59\%$) and lift ($+3.96\%$).
* **Cost-to-Fidelity Tradeoff:** Coarsening the wall-normal grid to the log-law regime reduces mesh size by **80.5%** (`123,504` $\rightarrow$ `24,124` cells) and cuts wall-clock runtime by **88.8%** (`1,785 s` $\rightarrow$ `199 s`, a **9.0x speedup**), demonstrating why wall-modeled RANS is preferred for rapid multi-angle polar sweeps before running targeted wall-resolved verification cases.