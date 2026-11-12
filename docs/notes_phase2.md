# Phase 2 Working Notes — Turbulence Models & Wall Functions
**Branch:** `feature/phase2-turbulence-models`  
**Airfoil & Flow Conditions:** NACA 0012, $c = 1.0\text{ m}$, $b = 0.01\text{ m}$ ($A_{\text{ref}} = 0.01\text{ m}^2$), $Re_c = 6.0 \times 10^6$, $\alpha = 4.0^\circ$, $\nu = 1.666667 \times 10^{-7}\text{ m}^2/\text{s}$

---

## Completed Cases

### Case A: NACA 0012 — $k\text{-}\omega$ SST (Wall-Resolved Baseline)
- **Directory:** `runs/naca0012_h1/`
- **Grid:** $h_1$ fine C-grid (`123,504` hex cells, $\text{mean } y^+ = 0.93$, $\text{max } y^+ = 2.11$)
- **Status:** Complete (Phase 1 baseline; confirmed `Aref = 0.01` in `system/controlDict`)
- **Converged Metrics ($t = 2500$, $A_{\text{ref}} = 0.01\text{ m}^2$):**
  - **$C_l$:** `0.4033`
  - **$C_d$:** `0.026992`
  - **$C_{m,\text{pitch}}$:** `+0.000810`
- **Computational Cost:** `2,500` iterations | `ExecutionTime = 1589.66 s` | `ClockTime = 1785 s` ($\sim 29.8\text{ min}$)

### Case B: NACA 0012 — Spalart-Allmaras (Wall-Resolved)
- **Directory:** `runs/naca0012_sa_h1/` | **Tracked Setup:** `setup/naca0012_sa_h1/`
- **Grid:** $h_1$ fine C-grid (`123,504` hex cells, $\text{mean } y^+ = 0.244$, $\text{min } y^+ = 0.126$, $\text{max } y^+ = 2.677$)
- **Status:** Complete & committed
- **Converged Aerodynamic Coefficients ($t = 2500$, $A_{\text{ref}} = 0.01\text{ m}^2$):**
  - **$C_l$:** `0.4658` (+15.5% vs. Case A)
  - **$C_d$:** `0.004324`
  - **$C_{m,\text{pitch}}$:** `-0.00525`
  - **$L/D$:** `107.7`
- **Convergence & Computational Cost:**
  - Iterations: `3000` (aerodynamic forces converged within $< 0.11\%$ between $t = 2000$ and $t = 2500$)
  - CPU Execution Time (`ExecutionTime`): `~1160 s` ($\sim 19.3\text{ min}$)
  - Wall-Clock Runtime (`ClockTime`): `1277 s` ($\sim 21.3\text{ min}$)
- **Configuration Fixes Applied:**
  - Corrected `Aref` from `1.0` to `0.01` in `system/controlDict` and re-ran `simpleFoam -postProcess`.
  - Enabled `writeCompression on;` and `purgeWrite 2;` to stay within `/home` storage limits.

### Case C: NACA 0012 — $k\text{-}\omega$ SST with Wall Functions
- **Directory:** `runs/naca0012_sst_wf/` | **Tracked Setup:** `setup/naca0012_sst_wf/`
- **Grid:** Coarse log-law C-grid (`wf`, `24,124` hex cells, $y_p = 2.04 \times 10^{-4}\text{ m}$)
- **Status:** Complete
- **Boundary Conditions (`0/`):**
  - `0/k`: `kqRWallFunction`
  - `0/omega`: `omegaWallFunction`
  - `0/nut`: `nutkWallFunction`
- **Wall Resolution ($t = 3000$):**
  - **Mean $y^+$:** `47.10` (target $30 \le y^+ \le 60$)
  - **Min / Max $y^+$:** `23.55` (stagnation/TE) / `78.38` (LE suction peak)
- **Converged Metrics ($t = 3000$, $A_{\text{ref}} = 0.01\text{ m}^2$):**
  - **$C_l$:** `0.419224` (+3.96% vs. Case A)
  - **$C_d$:** `0.027962` (+3.59% vs. Case A; pressure: `0.021936`, viscous: `0.006026`)
  - **$C_{m,\text{pitch}}$:** `-0.003337`
- **Computational Cost:** `3,000` iterations | `ExecutionTime = 168.26 s` | `ClockTime = 199 s` ($\sim 3.3\text{ min}$, **9.0x speedup** over Case A)

---

## Phase 2 Comparison Tables

### 1. Aerodynamic Force & Wall Resolution Matrix
| Case | Turbulence Model | Near-Wall Treatment | Hex Cells | Mean $y^+$ | $C_l$ | $C_d$ | $C_{m,\text{pitch}}$ | $\Delta C_l$ vs. Case A |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Case A** | $k\text{-}\omega$ SST | Wall-Resolved ($y^+ \le 1$) | 123,504 | 0.93 | 0.4033 | 0.02699 | +0.00081 | Baseline |
| **Case B** | Spalart-Allmaras | Wall-Resolved ($y^+ \le 1$) | 123,504 | **0.244** | **0.4658** | **0.00432** | -0.00525 | +15.5% |
| **Case C** | $k\text{-}\omega$ SST | Wall Functions ($30 \le y^+ \le 60$) | 24,124 | **47.10** | **0.4192** | **0.02796** | -0.00334 | +3.96% |

### 2. Computational Cost vs. Accuracy Summary
| Case | Hex Cells | Iterations | CPU Time (`ExecutionTime`) | Wall-Clock (`ClockTime`) | Relative Speedup | Engineering Takeaway |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Case A ($k\text{-}\omega$ SST WR)** | 123,504 | 2,500 | 1,590 s | 1,785 s (29.8 min) | 1.0x | Highest fidelity boundary-layer resolution |
| **Case B (SA WR)** | 123,504 | 3,000 | ~1,160 s | 1,277 s (21.3 min) | 1.4x | 1-equation efficiency; higher attached lift |
| **Case C ($k\text{-}\omega$ SST WF)** | 24,124 | 3,000 | **168 s** | **199 s (3.3 min)** | **9.0x** | ~9x faster with < 4% lift/drag deviation |

---

## Summary & Engineering Takeaways
- **Closure Sensitivity:** Spalart-Allmaras maintains stronger trailing-edge attachment, predicting higher lift ($C_l = 0.4658$, closely matching NASA TMR/experimental benchmarks of $C_l \approx 0.44\text{--}0.46$) and lower form drag ($C_d = 0.004324$).
- **Wall-Function Tradeoff:** Coarsening the mesh to log-law spacing ($30 \le y^+ \le 60$) reduces cell count by **80.5%** (`123,504` $\rightarrow$ `24,124`) and wall-clock time by **88.8%** (`1,785 s` $\rightarrow$ `199 s`, a **9.0x speedup**) while remaining within **3.96%** of Case A's lift and **3.59%** of Case A's total drag.