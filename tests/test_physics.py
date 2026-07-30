import numpy as np
from processtwin.physics import oxidation_thickness,dopant_profile,diffusivity,DEPTH_UM,junction_depth
def test_oxidation_monotonic_time_and_wet_faster():
 assert oxidation_thickness(1000,60,'dry')>oxidation_thickness(1000,30,'dry')
 assert oxidation_thickness(1000,60,'wet')>oxidation_thickness(1000,60,'dry')
def test_diffusivity_increases_with_temperature(): assert diffusivity('B',1050)>diffusivity('B',900)
def test_diffusion_broadens_and_nearly_conserves_dose():
 p1=dopant_profile('B',1e14,.15,.04,900,10); p2=dopant_profile('B',1e14,.15,.04,1050,1000)
 assert p2.max()<p1.max(); assert .85e14<np.trapezoid(p1,DEPTH_UM*1e-4)<1.05e14
def test_junction_positive():
 p=dopant_profile('P',1e14,.12,.04,950,100); assert junction_depth(DEPTH_UM,p,1e16)>.12
