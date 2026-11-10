import numpy as np

def run_gci(name, phi1, phi2, phi3, r=np.sqrt(2)):
    e21 = phi2 - phi1
    e32 = phi3 - phi2
    R = e21 / e32
    ea21 = abs(e21 / phi1)
    
    print(f"\n{'='*40}")
    print(f" {name}")
    print(f"{'='*40}")
    print(f"  h3 (Coarse) : {phi3:10.6f}")
    print(f"  h2 (Medium) : {phi2:10.6f}")
    print(f"  h1 (Fine)   : {phi1:10.6f}")
    print(f"  Ratio (R)   : {R:+10.4f}")
    
    if R < 0:
        delta_osc = 0.5 * abs(phi1 - phi2)
        pct = (delta_osc / abs(phi1)) * 100.0
        print(f"  Regime      : Oscillatory Convergence")
        print(f"  Uncertainty : +/- {pct:.2f}% (delta = {delta_osc:.6f})")
    else:
        p_obs = np.log(abs(e32 / e21)) / np.log(r)
        gci_obs = (1.25 * ea21) / (r**p_obs - 1.0) * 100.0
        gci_formal = (1.25 * ea21) / (r**2.0 - 1.0) * 100.0
        print(f"  Regime      : Monotonic Convergence")
        print(f"  Apparent p  : {p_obs:.2f}")
        print(f"  GCI (obs)   : {gci_obs:.1f}%")
        print(f"  GCI (formal): {gci_formal:.1f}% (p = 2.0)")

if __name__ == "__main__":
    run_gci("Lift Coefficient (Cl)", phi1=0.403262, phi2=0.391010, phi3=0.395056)
    run_gci("Drag Coefficient (Cd)", phi1=0.027000, phi2=0.033300, phi3=0.041000)