# Written by Yulun Wu 
# June 23, 2025

# # Go up by 2 directories and import 
# import sys
# import os.path as path
# two_up =  path.abspath(path.join(__file__ ,"../.."))
# sys.path.append(two_up)


import selfshadingcorrection as ssc

file_in = 'Rw_shaded.csv'
file_out = 'Rw_corrected.csv'
start_column = 10
sza_column = 'sza'
radius = 0.05 # in m

ssc.run(file_in, file_out, start_column, sza_column, radius)
