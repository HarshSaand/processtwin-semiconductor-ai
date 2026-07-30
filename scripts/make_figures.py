#!/usr/bin/env python3
from pathlib import Path
import json,sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/'src')); OUT=ROOT/'outputs/figures'; OUT.mkdir(parents=True,exist_ok=True)
from processtwin.data import matrix
from processtwin.model import load,predict,targets
from processtwin.physics import simulate,DEPTH_UM,oxidation_thickness
sns.set_theme(style='whitegrid'); navy='#082B4C'; teal='#00A6A6'; gold='#E4B363'
d=np.load(ROOT/'data/simulated.npz'); rows=[json.loads(x) for x in d['rows']]; b=load(ROOT/'artifacts/surrogate.joblib'); ids=[i for i,r in enumerate(rows) if r['split']=='test']; rr=[rows[i] for i in ids]; y=targets(rr); pr=predict(b,matrix(rr))
fig,axs=plt.subplots(1,2,figsize=(10,4.4));
for ax,i,title,unit in [(axs[0],0,'Oxide thickness','nm'),(axs[1],1,'Junction depth','µm')]:
 ax.scatter(y[:,i],pr['targets'][:,i],s=14,alpha=.6,color=teal); lo=min(y[:,i].min(),pr['targets'][:,i].min()); hi=max(y[:,i].max(),pr['targets'][:,i].max()); ax.plot([lo,hi],[lo,hi],color=navy,ls='--'); ax.set(xlabel=f'Simulator ({unit})',ylabel=f'AI surrogate ({unit})',title=title)
plt.tight_layout(); fig.savefig(OUT/'parity.png',dpi=180); plt.close(fig)

pick=ids[len(ids)//3]; r=rows[pick]; phys=simulate(r); q=predict(b,matrix([r])); fig,ax=plt.subplots(figsize=(7,4.4)); ax.plot(DEPTH_UM,np.log10(np.maximum(phys['profile_cm3'],1e10)),label='Physics',lw=2,color=navy); ax.plot(DEPTH_UM,q['profiles'][0],label='AI surrogate',ls='--',lw=2,color=teal); ax.axhline(np.log10(r['background_cm3']),color=gold,ls=':',label='Background'); ax.set(xlabel='Depth (µm)',ylabel='log10 concentration (cm⁻³)',title='Representative held-out dopant profile'); ax.legend(); plt.tight_layout(); fig.savefig(OUT/'profile_overlay.png',dpi=180); plt.close(fig)

temps=np.linspace(850,1100,80); times=np.linspace(5,180,80); z=np.array([[oxidation_thickness(t,m,'wet') for m in times] for t in temps]); fig,ax=plt.subplots(figsize=(7,4.8)); im=ax.contourf(times,temps,z,levels=18,cmap='viridis'); fig.colorbar(im,ax=ax,label='Oxide thickness (nm)'); ax.axhline(1050,color='white',ls='--',label='Primary domain boundary'); ax.set(xlabel='Oxidation time (min)',ylabel='Temperature (°C)',title='Wet oxidation response surface'); ax.legend(); plt.tight_layout(); fig.savefig(OUT/'oxidation_surface.png',dpi=180); plt.close(fig)

m=json.loads((ROOT/'outputs/metrics.json').read_text()); names=['Oxide MAE\n(nm)','Junction MAE\n(µm)','Profile RMSE\n(log10)']; main=[m['test']['oxide_nm']['mae'],m['test']['junction_um']['mae'],m['test']['profile_log10_rmse']]; base=[m['test']['baseline']['oxide_nm']['mae'],m['test']['baseline']['junction_um']['mae'],m['test']['baseline']['profile_log10_rmse']]; x=np.arange(3); fig,axs=plt.subplots(1,3,figsize=(10,3.8));
for i,ax in enumerate(axs): ax.bar(['Baseline','AI'],[base[i],main[i]],color=[gold,teal]); ax.set_title(names[i]); ax.bar_label(ax.containers[0],fmt='%.3g',padding=2)
fig.suptitle('Held-out recipe-bin performance'); plt.tight_layout(); fig.savefig(OUT/'model_comparison.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(7,7)); ax.axis('off'); boxes=[('1  Process recipe DOE','Oxidation, implant and anneal parameters'),('2  Reduced-order physics','Deal-Grove oxidation + 1D dopant diffusion'),('3  Blocked evaluation','Held-out temperature bins + high-temperature OOD'),('4  AI surrogate','Three MLPs + PCA concentration-profile decoder'),('5  Physical checks','Profiles, dose retention, uncertainty and residuals'),('6  Engineer output','Fast estimates and simulator-verified recipe design')]; ys=np.linspace(.9,.1,len(boxes))
for i,((a,c),yy) in enumerate(zip(boxes,ys)):
 ax.add_patch(plt.Rectangle((.08,yy-.055),.84,.1,facecolor='#EAF4F4',edgecolor=teal,lw=2)); ax.text(.11,yy+.012,a,weight='bold',color=navy,fontsize=11); ax.text(.11,yy-.025,c,color='#334E68',fontsize=9)
 if i<len(boxes)-1: ax.annotate('',(.5,ys[i+1]+.052),(.5,yy-.06),arrowprops=dict(arrowstyle='-|>',color=navy))
ax.set_title('ProcessTwin — implemented system flow',weight='bold',fontsize=15,color=navy); fig.savefig(OUT/'system_flow.png',dpi=180,bbox_inches='tight'); plt.close(fig)
print(OUT)
