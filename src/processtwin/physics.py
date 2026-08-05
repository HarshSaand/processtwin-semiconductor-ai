"""Reduced-order silicon thermal oxidation and dopant diffusion physics.

This module is intentionally transparent and educational. It is not calibrated
commercial process software and does not model segregation, clustering, implant damage or TED.
"""
from __future__ import annotations
import numpy as np

KB = 8.617333262e-5  # eV/K
DEPTH_UM = np.linspace(0.0, 1.2, 121)

# Reference Deal-Grove constants at 1000 C; values are literature-scale
# engineering coefficients exposed here so assumptions are auditable.
OX = {
    "dry": {"B_ref": 0.0117, "BA_ref": 0.039, "E_B": 1.23, "E_BA": 2.00},
    "wet": {"B_ref": 0.287, "BA_ref": 0.68, "E_B": 0.78, "E_BA": 2.05},
}
DIFF = {
    "B": {"D0": 0.76, "Ea": 3.46},
    "P": {"D0": 10.5, "Ea": 3.69},
}

def _arrhenius_from_ref(value_ref: float, energy: float, temp_c: float, ref_c: float = 1000.0) -> float:
    t, tr = temp_c + 273.15, ref_c + 273.15
    return value_ref * np.exp(-energy / KB * (1.0 / t - 1.0 / tr))

def oxidation_thickness(temp_c: float, time_min: float, ambient: str, initial_nm: float = 2.0) -> float:
    """Deal-Grove oxide thickness in nm using x^2 + A x = B(t+tau)."""
    p = OX[ambient]
    B = _arrhenius_from_ref(p["B_ref"], p["E_B"], temp_c)  # um2/h
    BA = _arrhenius_from_ref(p["BA_ref"], p["E_BA"], temp_c)  # um/h
    A = B / max(BA, 1e-12); x0 = initial_nm / 1000.0
    rhs = x0*x0 + A*x0 + B*(time_min/60.0)
    x = (-A + np.sqrt(A*A + 4*rhs))/2
    return float(x*1000.0)

def diffusivity(species: str, temp_c: float) -> float:
    """Intrinsic diffusivity in cm2/s from an Arrhenius approximation."""
    p=DIFF[species]; return float(p["D0"]*np.exp(-p["Ea"]/(KB*(temp_c+273.15))))

def dopant_profile(species: str, dose_cm2: float, rp_um: float, straggle_um: float,
                   anneal_temp_c: float, anneal_time_s: float, depth_um=DEPTH_UM) -> np.ndarray:
    """Dose-conserving Gaussian implant broadened by 1D constant-D diffusion."""
    D_um2_s = diffusivity(species, anneal_temp_c) * 1e8
    sigma = np.sqrt(straggle_um**2 + 2*D_um2_s*anneal_time_s)
    depth_cm = np.asarray(depth_um)*1e-4; sigma_cm=sigma*1e-4; rp_cm=rp_um*1e-4
    return dose_cm2/(np.sqrt(2*np.pi)*sigma_cm)*np.exp(-0.5*((depth_cm-rp_cm)/sigma_cm)**2)

def junction_depth(depth_um: np.ndarray, concentration: np.ndarray, background_cm3: float) -> float:
    """Deepest concentration/background crossing, in micrometres."""
    idx=np.where(concentration>=background_cm3)[0]
    if not len(idx): return 0.0
    i=int(idx[-1])
    if i==len(depth_um)-1: return float(depth_um[i])
    x0,x1=depth_um[i],depth_um[i+1]; y0,y1=np.log10(concentration[i]),np.log10(max(concentration[i+1],1.0)); target=np.log10(background_cm3)
    return float(x0+(x1-x0)*(target-y0)/(y1-y0)) if y1!=y0 else float(x0)

def simulate(recipe: dict) -> dict:
    profile=dopant_profile(recipe["species"],recipe["dose_cm2"],recipe["rp_um"],recipe["straggle_um"],recipe["anneal_temp_c"],recipe["anneal_time_s"])
    return {"oxide_nm":oxidation_thickness(recipe["oxidation_temp_c"],recipe["oxidation_time_min"],recipe["ambient"],recipe.get("initial_oxide_nm",2.0)),
            "profile_cm3":profile,"junction_um":junction_depth(DEPTH_UM,profile,recipe["background_cm3"]),
            "peak_cm3":float(profile.max()),"retained_dose_cm2":float(np.trapezoid(profile,DEPTH_UM*1e-4))}
