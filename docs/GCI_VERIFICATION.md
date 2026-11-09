# Phase 1: Simulation Data Handoff

**Case:** NACA 0012 Grid Convergence ($Re_c = 6.0 \times 10^6$, $\alpha = 4.0^\circ$, `simpleFoam`, $k-\omega$ SST)  
**Refinement Ratio:** $r = \sqrt{2} \approx 1.414$

## Converged Force and Mesh Metrics

| Metric / Parameter | Coarse Grid ($h_3$) | Medium Grid ($h_2$) | Fine Grid ($h_1$) |
| :--- | :---: | :---: | :---: |
| **Hex Cells ($N$)** | 30,504 | 61,600 | 123,504 |
| **Mean Airfoil $y^+$** | 1.82 | 1.31 | **0.93** |
| **Max Airfoil $y^+$** | 3.72 | 2.81 | 2.11 |
| **Converged Lift ($C_l$)** | **0.395056** | **0.391010** | **0.403262** |
| **Converged Drag ($C_d$)** | **0.040999** | **0.033308** | **0.026992** |
| **Pressure Drag ($C_{d,p}$)** | 0.034284 | 0.026298 | 0.015512 |
| **Viscous Drag ($C_{d,v}$)** | 0.006716 | 0.007009 | 0.011480 |
| **Pitching Moment ($C_m$)** | -0.002279 | -0.000370 | +0.000810 |