import numpy as np

def analyze_gci(name, phi1, phi2, phi3, r=np.sqrt(2), p_formal=2.0, Fs=1.25):
    """
    ASME V&V 20 Standard Grid Convergence Index (GCI) Analysis.
    phi1: Fine (h1)
    phi2: Medium (h2)
    phi3: Coarse (h3)
    r: Grid refinement ratio (r21 = r32)
    """
    e21 = phi2 - phi1
    e32 = phi3 - phi2
    R = e21 / e32

    ea21 = abs(e21 / phi1)
    ea32 = abs(e32 / phi2)

    print(f"==================================================")
    print(f" Variable: {name}")
    print(f"==================================================")
    print(f"  Coarse (h3): {phi3:12.6f}")
    print(f"  Medium (h2): {phi2:12.6f}")
    print(f"  Fine   (h1): {phi1:12.6f}")
    print(f"  Relative spacing (r): {r:.4f}")
    print(f"  Convergence ratio (R): {R:+.4f}")

    if R < 0:
        # Oscillatory Convergence
        delta_osc = 0.5 * abs(phi1 - phi2)
        pct_osc = (delta_osc / abs(phi1)) * 100.0
        print(f"  Regime: Oscillatory Convergence (R < 0)")
        print(f"  Oscillatory Uncertainty (delta_osc): {delta_osc:.6f}")
        print(f"  Normalized Uncertainty Bound:        +/- {pct_osc:.2f}%")
        print(f"  Note: Solution fluctuates within a narrow asymptotic band.")
        print(f"        Formal Richardson extrapolation is undefined (ln(R) < 0).")
    elif 0 < R < 1:
        # Monotonic Convergence
        p_obs = np.log(abs(e32 / e21)) / np.log(r)
        
        # Observed order GCI
        phi_ext_obs = phi1 + (phi1 - phi2) / (r**p_obs - 1.0)
        gci21_obs = (Fs * ea21) / (r**p_obs - 1.0) * 100.0
        
        # Formal order GCI (ASME V&V 20 / Roache limit when p_obs is depressed)
        phi_ext_formal = phi1 + (phi1 - phi2) / (r**p_formal - 1.0)
        gci21_formal = (Fs * ea21) / (r**p_formal - 1.0) * 100.0

        print(f"  Regime: Monotonic Convergence (0 < R < 1)")
        print(f"  Apparent Order (p_obs):              {p_obs:.2f}")
        print(f"  Extrapolated Value (phi_ext, obs):   {phi_ext_obs:12.6f}")
        print(f"  Fine Grid GCI (observed p):          {gci21_obs:.2f}%")
        print(f"  --- Dual Reporting (Formal Order p = {p_formal:.1f}) ---")
        print(f"  Extrapolated Value (phi_ext, formal):{phi_ext_formal:12.6f}")
        print(f"  Fine Grid GCI (formal p):            {gci21_formal:.2f}%")
    else:
        print(f"  Regime: Divergence (R > 1)")

# Execute for NACA 0012 Triad
print("\n" + "#"*50)
print(" ASME V&V 20 DISCRETIZATION ERROR VERIFICATION")
print("#"*50 + "\n")

# Lift Coefficient (Cl)
analyze_gci("Lift Coefficient (Cl)", phi1=0.403262, phi2=0.391010, phi3=0.395056)

print()
# Drag Coefficient (Cd)
analyze_gci("Drag Coefficient (Cd)", phi1=0.0270, phi2=0.0333, phi3=0.0410)