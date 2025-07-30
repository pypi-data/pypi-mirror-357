# Written by Yulun Wu 
# June 23, 2025


# freshwater backscattering, 300-1000 nm, from WOPP, Röttgers et al., 2016
# https://calvalportal.ceos.org/tools

def find_b_bw(wl):
    
    import numpy as np
    import warnings
    
    if wl < 300 or wl > 1000:
        raise ValueError(f"Input wavelength {wl} nm is out of valid range (300–1000 nm).")

    log_b_w = -1.818 * np.log(wl) + 8.6027
    b_w = 10 ** log_b_w
    return b_w/2
    