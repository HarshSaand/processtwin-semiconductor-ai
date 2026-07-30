#!/usr/bin/env python3
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from processtwin.data import matrix
from processtwin.model import train_models,targets,save
d=np.load(ROOT/'data/simulated.npz'); rows=[json.loads(x) for x in d['rows']]; idx=[i for i,r in enumerate(rows) if r['split']=='train']; bundle=train_models(matrix([rows[i] for i in idx]),targets([rows[i] for i in idx]),d['profiles'][idx]); (ROOT/'artifacts').mkdir(exist_ok=True); save(bundle,ROOT/'artifacts/surrogate.joblib'); print('saved',ROOT/'artifacts/surrogate.joblib',len(idx))
