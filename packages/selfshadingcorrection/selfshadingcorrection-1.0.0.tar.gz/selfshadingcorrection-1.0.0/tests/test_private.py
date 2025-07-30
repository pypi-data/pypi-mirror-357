# Go up by 2 directories and import 

import sys
import os.path as path
two_up =  path.abspath(path.join(__file__ ,"../.."))
sys.path.append(two_up)

import selfshadingcorrection as ssc


file_in = '/Users/yw/Local_storage/Fieldwork/R_calibrated_sza.csv'
file_out = '/Users/yw/Local_storage/Fieldwork/R_calibrated_sza_ssc.csv'
start_column = 11
sza_column = 'sza'
radius = 0.05 # in m



ssc.run(file_in, file_out, start_column, sza_column, radius)



'''

def smooth_rrs(x):
    return x + 0.001 * np.exp(-300*x)

import numpy as np
import matplotlib.pyplot as plt

# smooth_rrs(0.002)


rrs_vals = np.linspace(0.0001, 0.01, 30)
adjusted_vals = [smooth_rrs(val) for val in rrs_vals]




# Plot
plt.plot(rrs_vals, adjusted_vals, marker='o', label='Smoothed')
plt.plot(rrs_vals, rrs_vals, linestyle='--', label='Original (y = x)')
plt.xlabel('Original rrs_wl')
plt.ylabel('Adjusted rrs_wl')
plt.title('Smooth Truncation Effect')
plt.legend()
plt.grid(True)
plt.show()


'''




