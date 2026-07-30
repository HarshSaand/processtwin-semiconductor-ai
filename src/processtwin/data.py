from __future__ import annotations
import numpy as np
from .physics import simulate, DEPTH_UM

FEATURES=["oxidation_temp_c","oxidation_time_min","ambient_wet","anneal_temp_c","anneal_time_s","species_p","log10_dose","rp_um","straggle_um","log10_background"]

def generate(n=6000,seed=42):
    rng=np.random.default_rng(seed); rows=[]; profiles=[]
    for i in range(n):
        ood=i>=int(.84*n)
        r={"oxidation_temp_c":float(rng.uniform(850,1050 if not ood else 1150)),"oxidation_time_min":float(rng.uniform(5,180)),"ambient":"wet" if rng.random()<.5 else "dry",
           "anneal_temp_c":float(rng.uniform(800,1050) if not ood else rng.uniform(1055,1150)),"anneal_time_s":float(10**rng.uniform(0.7,3.0)),"species":"P" if rng.random()<.5 else "B",
           "dose_cm2":float(10**rng.uniform(12.5,15.5)),"rp_um":float(rng.uniform(.03,.35)),"straggle_um":float(rng.uniform(.015,.09)),"background_cm3":float(10**rng.uniform(15,17)),"initial_oxide_nm":2.0}
        y=simulate(r); split="ood" if ood else "train"
        rows.append({**r,"oxide_nm":y["oxide_nm"],"junction_um":y["junction_um"],"peak_cm3":y["peak_cm3"],"retained_dose_cm2":y["retained_dose_cm2"],"split":split}); profiles.append(np.log10(np.maximum(y["profile_cm3"],1e10)))
    # Block entire anneal-temperature bins into validation/test to reduce recipe-neighbour leakage.
    normal=np.where(np.array([x["split"]=="train" for x in rows]))[0]
    bins=(np.array([rows[i]["anneal_temp_c"] for i in normal])//25).astype(int)
    for idx,b in zip(normal,bins):
        if b%7==0: rows[idx]["split"]="test"
        elif b%7==1: rows[idx]["split"]="val"
    return rows,np.asarray(profiles,np.float32),DEPTH_UM

def matrix(rows):
    return np.asarray([[r["oxidation_temp_c"],r["oxidation_time_min"],r["ambient"]=="wet",r["anneal_temp_c"],np.log10(r["anneal_time_s"]),r["species"]=="P",np.log10(r["dose_cm2"]),r["rp_um"],r["straggle_um"],np.log10(r["background_cm3"])] for r in rows],float)
