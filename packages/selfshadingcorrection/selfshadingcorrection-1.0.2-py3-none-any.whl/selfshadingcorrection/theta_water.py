# Written by Yulun Wu 
# June 23, 2025

# Above water solar zenith to in water solar zenith
def theta_water(theta_s_deg, n_w=1.34):
    
    import numpy as np
    
    theta_s_rad = np.radians(theta_s_deg)
    theta_w_rad = np.arcsin(np.sin(theta_s_rad) / n_w)
    theta_w_deg = np.degrees(theta_w_rad)
    
    return theta_w_deg
