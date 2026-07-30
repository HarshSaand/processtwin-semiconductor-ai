#!/usr/bin/env python3
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src'))
from processtwin.data import generate
import numpy as np
def main():
 p=argparse.ArgumentParser(); p.add_argument('--samples',type=int,default=6000); p.add_argument('--seed',type=int,default=42); a=p.parse_args(); rows,profiles,depth=generate(a.samples,a.seed); (ROOT/'data').mkdir(exist_ok=True); np.savez_compressed(ROOT/'data/simulated.npz',rows=np.array([json.dumps(r) for r in rows]),profiles=profiles,depth_um=depth); print({s:sum(r['split']==s for r in rows) for s in ('train','val','test','ood')})
if __name__=='__main__': main()
