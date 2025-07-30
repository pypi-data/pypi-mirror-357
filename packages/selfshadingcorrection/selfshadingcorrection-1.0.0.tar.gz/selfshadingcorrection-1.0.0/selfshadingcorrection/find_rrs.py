# Written by Yulun Wu 
# June 23, 2025


def find_rrs(R_array, wl):
    import numpy as np

    # Compute distances from target wavelength
    distances = np.abs(R_array[:, 0] - wl)
    
    # Get indices sorted by proximity to wl
    sorted_indices = np.argsort(distances)

    # Loop through sorted indices to find the first non-nan rrs
    for idx in sorted_indices:
        rrs = R_array[idx, 2]
        if not np.isnan(rrs):
            return rrs
