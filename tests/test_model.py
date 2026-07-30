import numpy as np
from processtwin.data import generate,matrix
from processtwin.model import train_models,targets,predict
def test_small_training_prediction_shapes():
 rows,p,d=generate(120,1); ids=[i for i,r in enumerate(rows) if r['split']=='train']; b=train_models(matrix([rows[i] for i in ids]),targets([rows[i] for i in ids]),p[ids],seed=1); q=predict(b,matrix(rows[:3])); assert q['targets'].shape==(3,3) and q['profiles'].shape==(3,len(d))
