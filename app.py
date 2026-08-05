from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent; sys.path.insert(0,str(ROOT/'src'))
from processtwin.data import matrix
from processtwin.model import load,predict
from processtwin.physics import simulate,DEPTH_UM

st.set_page_config(page_title='ProcessTwin',layout='wide'); st.title('ProcessTwin — AI Process Surrogate')
st.caption('Educational reduced-order silicon process model. Not calibrated commercial process software or fab-qualified prediction.')
ambient=st.sidebar.selectbox('Oxidation ambient',['dry','wet']); ot=st.sidebar.slider('Oxidation temperature (°C)',850,1150,1000); omin=st.sidebar.slider('Oxidation time (min)',5,180,60)
species=st.sidebar.selectbox('Dopant',['B','P']); dose=10**st.sidebar.slider('log10 dose (cm⁻²)',12.5,15.5,14.0,.1); rp=st.sidebar.slider('Projected range (µm)',.03,.35,.12,.01); sig=st.sidebar.slider('Straggle (µm)',.015,.09,.04,.005)
at=st.sidebar.slider('Anneal temperature (°C)',800,1150,950); ats=10**st.sidebar.slider('log10 anneal time (s)',.7,3.0,2.0,.1); bg=10**st.sidebar.slider('log10 background (cm⁻³)',15.0,17.0,16.0,.1)
r={'oxidation_temp_c':ot,'oxidation_time_min':omin,'ambient':ambient,'anneal_temp_c':at,'anneal_time_s':ats,'species':species,'dose_cm2':dose,'rp_um':rp,'straggle_um':sig,'background_cm3':bg,'initial_oxide_nm':2.0}
if not (ROOT/'artifacts/surrogate.joblib').exists(): st.error('Run scripts/generate_data.py and scripts/train.py first.'); st.stop()
b=load(ROOT/'artifacts/surrogate.joblib'); pr=predict(b,matrix([r])); phys=simulate(r); c1,c2,c3=st.columns(3); c1.metric('AI oxide thickness',f"{pr['targets'][0,0]:.2f} nm"); c2.metric('AI junction depth',f"{pr['targets'][0,1]:.4f} µm"); c3.metric('Ensemble spread',f"{pr['target_std'][0,1]:.4f} µm")
if ot>1050 or at>1050: st.warning('OOD recipe region: temperatures exceed the primary training domain. Treat the surrogate output as review-only.')
fig,ax=plt.subplots(figsize=(8,4)); ax.plot(DEPTH_UM,np.log10(np.maximum(phys['profile_cm3'],1e10)),label='Physics simulator',lw=2); ax.plot(DEPTH_UM,pr['profiles'][0],label='AI surrogate',ls='--'); ax.axhline(np.log10(bg),color='gray',ls=':',label='Background'); ax.set(xlabel='Depth (µm)',ylabel='log10 concentration (cm⁻³)',title='Dopant profile'); ax.legend(); st.pyplot(fig)
st.subheader('Simulator verification'); st.dataframe(pd.DataFrame({'quantity':['oxide_nm','junction_um','retained_dose_cm2'],'physics':[phys['oxide_nm'],phys['junction_um'],phys['retained_dose_cm2']]}),hide_index=True)
st.download_button('Download recipe JSON',json.dumps(r,indent=2),'process_recipe.json')
