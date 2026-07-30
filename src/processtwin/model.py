from __future__ import annotations
import numpy as np, joblib
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.linear_model import Ridge
from sklearn.neural_network import MLPRegressor
from sklearn.decomposition import PCA
from sklearn.compose import TransformedTargetRegressor

TARGETS=["oxide_nm","junction_um","log10_peak"]

def targets(rows): return np.asarray([[r["oxide_nm"],r["junction_um"],np.log10(r["peak_cm3"])] for r in rows],float)

def train_models(X,y,profiles,seed=42):
    pca=PCA(n_components=10,random_state=seed).fit(profiles); z=pca.transform(profiles); yz=np.c_[y,z]
    baseline=make_pipeline(StandardScaler(),PolynomialFeatures(2,include_bias=False),Ridge(alpha=1.0)).fit(X,yz)
    ensemble=[]
    for s in range(3):
        core=make_pipeline(StandardScaler(),MLPRegressor(hidden_layer_sizes=(128,128,64),activation="relu",early_stopping=True,validation_fraction=.12,max_iter=350,random_state=seed+s,batch_size=128,learning_rate_init=1e-3))
        mdl=TransformedTargetRegressor(regressor=core,transformer=StandardScaler()).fit(X,yz)
        ensemble.append(mdl)
    return {"baseline":baseline,"ensemble":ensemble,"pca":pca}

def predict(bundle,X):
    members=np.stack([m.predict(X) for m in bundle["ensemble"]]); mean=members.mean(0); std=members.std(0)
    profile=bundle["pca"].inverse_transform(mean[:,3:]); baseline=bundle["baseline"].predict(X)
    return {"targets":mean[:,:3],"target_std":std[:,:3],"profiles":profile,"baseline_targets":baseline[:,:3],"baseline_profiles":bundle["pca"].inverse_transform(baseline[:,3:])}

def save(bundle,path): joblib.dump(bundle,path)
def load(path): return joblib.load(path)
