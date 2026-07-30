#!/usr/bin/env python3
import json,sys,time
from pathlib import Path
import numpy as np
from sklearn.metrics import mean_absolute_error,mean_squared_error,r2_score
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from processtwin.data import matrix
from processtwin.model import load,predict,targets
from processtwin.physics import simulate
def section(rows,profiles,bundle):
 X=matrix(rows); y=targets(rows); t=time.perf_counter(); pr=predict(bundle,X); latency=(time.perf_counter()-t)/len(rows)*1e6
 t=time.perf_counter(); [simulate(r) for r in rows]; physics_latency=(time.perf_counter()-t)/len(rows)*1e6
 def met(a,b): return {'mae':float(mean_absolute_error(a,b)),'rmse':float(mean_squared_error(a,b)**.5),'r2':float(r2_score(a,b))}
 names=['oxide_nm','junction_um','log10_peak']; out={n:met(y[:,i],pr['targets'][:,i]) for i,n in enumerate(names)}; out['profile_log10_rmse']=float(np.sqrt(np.mean((profiles-pr['profiles'])**2))); out['inference_us_per_recipe']=latency; out['physics_us_per_recipe']=physics_latency; out['measured_speedup']=physics_latency/max(latency,1e-9)
 out['baseline']={n:met(y[:,i],pr['baseline_targets'][:,i]) for i,n in enumerate(names)}; out['baseline']['profile_log10_rmse']=float(np.sqrt(np.mean((profiles-pr['baseline_profiles'])**2)))
 # empirical 90% ensemble interval coverage (small ensemble, prototype evidence)
 out['ensemble_90_coverage']={n:float(np.mean(np.abs(y[:,i]-pr['targets'][:,i])<=1.645*np.maximum(pr['target_std'][:,i],1e-9))) for i,n in enumerate(names)}
 return out
def main():
 d=np.load(ROOT/'data/simulated.npz'); allrows=[json.loads(x) for x in d['rows']]; b=load(ROOT/'artifacts/surrogate.joblib'); out={}
 for split in ('test','ood'):
  ids=[i for i,r in enumerate(allrows) if r['split']==split]; out[split]={'n':len(ids),**section([allrows[i] for i in ids],d['profiles'][ids],b)}
 (ROOT/'outputs').mkdir(exist_ok=True); (ROOT/'outputs/metrics.json').write_text(json.dumps(out,indent=2)); print(json.dumps(out,indent=2))
if __name__=='__main__': main()
