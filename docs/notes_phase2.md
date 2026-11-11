# Phase 2 Working Notes — Turbulence Models & Wall Functions
**Branch:** `feature/phase2-turbulence-models`  
**Airfoil & Flow Conditions:** NACA 0012, $c = 1.0\text{ m}$, $b = 0.01\text{ m}$ ($A_{\text{ref}} = 0.01\text{ m}^2$), $Re_c = 6.0 \times 10^6$, $\alpha = 4.0^\circ$, $\nu = 1.666667 \times 10^{-7}\text{ m}^2/\text{s}$

---

## Completed Cases

### Case A: NACA 0012 — $k\text{-}\omega$ SST (Wall-Resolved Baseline)
* **Grid:** $h_1$ fine C-grid ($\sim 123.5\text{k}$ hex cells, $\text{mean } y^+ = 0.93$, $\text{max } y^+ = 2.11$)
* **Status:** Complete (Phase 1 baseline)
* **Converged Metrics ($t = 2500$):**
  * $C_l = 0.4033$
  * $C_d = 0.0270$ *(Note: verify `Aref` scaling on Phase 1 $C_d$ before final `README.md` table)*

### Case B: NACA 0012 — Spalart-Allmaras (Wall-Resolved)
* **Directory:** `runs/naca0012_sa_h1/`
* **Grid:** $h_1$ fine C-grid ($\sim 123.5\text{k}$ hex cells, wall-resolved $y^+ \le 1$)
* **Status:** Complete & committed
* **Converged Aerodynamic Coefficients ($t = 2500$, $A_{\text{ref}} = 0.01\text{ m}^2$):**
  * **$C_l$:** `0.4658`
  * **$C_d$:** `0.004324`
  * **$C_{m,\text{pitch}}$:** `-0.00525`
  * **$L/D$:** `107.7`
* **Convergence & Computational Cost:**
  * Iterations: `3000` (aerodynamic forces converged within $< 0.11\%$ between $t = 2000$ and $t = 2500$)
  * CPU Execution Time (`ExecutionTime`): `~1160 s` ($\sim 19.3\text{ min}$)
  * Wall-Clock Runtime (`ClockTime`): `1277 s` ($\sim 21.3\text{ min}$)
* **Configuration Fixes Applied:**
  * Corrected `Aref` from `1.0` to `0.01` in `system/controlDict` and re-ran `simpleFoam -postProcess`.
  * Enabled `writeCompression on;` and `purgeWrite 2;` to stay within `/home` storage limits.

---

## Next Up

### Case C: NACA 0012 — $k\text{-}\omega$ SST with Wall Functions
* **Target Near-Wall Resolution:** $30 \le y^+ \le 60$
* **Required Boundary Conditions (`0/`):**
  * `0/k`: `kqRWallFunction`
  * `0/omega`: `omegaWallFunction`
  * `0/nut`: `nutkWallFunction`
* **Post-Processing Checklist:**
  * Verify `mean y+` and `max y+` fall inside $30\text{--}60$ using `scripts/compute_yplus.py`
  * Extract final $C_l$, $C_d$, iteration count, and `ClockTime`
  * Merge Cases A, B, and C into the final **Cost vs. Accuracy** table in `README.md`