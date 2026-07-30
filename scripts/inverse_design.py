#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, least_squares
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from processtwin.data import matrix
from processtwin.model import load,predict
from processtwin.physics import simulate
def main():
 p=argparse.ArgumentParser(); p.add_argument('--target-oxide-nm',type=float,default=120); p.add_argument('--target-junction-um',type=float,default=.32); a=p.parse_args(); b=load(ROOT/'artifacts/surrogate.joblib')
 base={'ambient':'wet','species':'B','dose_cm2':1e14,'rp_um':.12,'straggle_um':.04,'background_cm3':1e16,'initial_oxide_nm':2.0}
 def recipe(x): return {**base,'oxidation_temp_c':x[0],'oxidation_time_min':x[1],'anneal_temp_c':x[2],'anneal_time_s':10**x[3]}
 def loss(x):
  q=predict(b,matrix([recipe(x)]))['targets'][0]; return ((q[0]-a.target_oxide_nm)/max(a.target_oxide_nm,1))**2+((q[1]-a.target_junction_um)/max(a.target_junction_um,.01))**2
 res=differential_evolution(loss,[(850,1050),(5,180),(800,1050),(.7,3)],seed=42,popsize=8,maxiter=35); candidate=recipe(res.x); pre=simulate(candidate)
 def residual(x):
  q=simulate(recipe(x)); return [(q['oxide_nm']-a.target_oxide_nm)/max(a.target_oxide_nm,1),(q['junction_um']-a.target_junction_um)/max(a.target_junction_um,.01)]
 refined=least_squares(residual,res.x,bounds=([850,5,800,.7],[1050,180,1050,3]),max_nfev=80); r=recipe(refined.x); verified=simulate(r)
 out={'surrogate_candidate':candidate,'surrogate_objective':float(res.fun),'candidate_solver_check':{'oxide_nm':pre['oxide_nm'],'junction_um':pre['junction_um']},'refined_recipe':r,'refined_solver_verified':{'oxide_nm':verified['oxide_nm'],'junction_um':verified['junction_um']},'targets':vars(a)}; (ROOT/'outputs/inverse_design.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
