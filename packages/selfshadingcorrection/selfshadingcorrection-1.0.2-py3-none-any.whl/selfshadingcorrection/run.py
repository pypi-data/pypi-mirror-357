# Written by Yulun Wu 
# June 23, 2025


def run(file_in, file_out, start_column, sza_column, radius, to_log = True):
    '''

    Parameters
    ----------
    file_in : string
        Path to input CSV with shaded water-leaving reflectance.
    file_out : string
        Path to output CSV with self-shading-corrected reflectance.
    start_column : integer
        Index of the first reflectance column (0-based).
    sza_column : string
        Name of the column containing solar zenith angle (in degrees).
    radius : float
        Radius of the instrument cone (in meters).
    to_log : boolean, optional
        Whether save metadata/settings and console prints as a TXT file. The default is True.


    '''
    import math, sys, time
    import numpy as np
    import pandas as pd
    
    from scipy.optimize import fsolve
    from importlib.metadata import version
    
    from .model_rrs import model_rrs
    from .find_rrs import find_rrs
    from .find_b_bw import find_b_bw
    from .theta_water import theta_water
    

    ### Print all metadata/settings and save them in a txt file
    
    if to_log: 
        
        # Start logging in txt file
        orig_stdout = sys.stdout
        
        log_file = file_out.replace(".csv", "_log.txt")
        log_file = log_file.replace(".CSV", "_log.txt")
   
        class Logger:
            def __init__(self, filename):
                self.console = sys.stdout
                self.file = open(filename, 'w')
                self.file.flush()
            def write(self, message):
                self.console.write(message)
                self.file.write(message)
            def flush(self):
                self.console.flush()
                self.file.flush()
    
        sys.stdout = Logger(log_file)
    
    
    print('selfshadingcorrection version: ' + str(version('selfshadingcorrection')))
    print('System time: ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    print('file_in: ' + str(file_in))
    print('file_out: ' + str(file_out))
    print('start_column: ' + str(start_column))
    print('sza_column: ' + str(sza_column))
    print('radius: ' + str(radius))


    # Smooth rrs at low reflectance 
    def smooth_rrs(x):
        return x + 0.001 * np.exp(-300*x)

    # Read the CSV file
    df = pd.read_csv(file_in)
    
    # For each spectrum
    for index, row in df.iterrows():
        print('\nRow: ' + str(index) + '/' + str(df.shape[0]))

        # Above water solar zenith to in water solar zenith
        theta_s = df.at[index, sza_column]  # above water
        theta_w = theta_water(theta_s)      # in water
        theta_w_rad = np.radians(theta_w)
        
        # Reflectance
        R = row.iloc[start_column:]
        wavelengths = [float(col[1:]) for col in R.index]  # Remove 'R' and convert to float
        
        # Combine into a numpy array: first column = wavelength, second = reflectance value
        R_array = np.column_stack((wavelengths, R.values))
        
        # Add rrs
        temp_Rrs = R_array[:,1] / np.pi
        temp_rrs = temp_Rrs / (0.52 + 1.7 * temp_Rrs)
        R_array = np.column_stack((R_array, temp_rrs))

        # rrs at various wavelengths 
        rrs_440 = find_rrs(R_array, 440)
        rrs_555 = find_rrs(R_array, 555)
        rrs_750 = find_rrs(R_array, 750)

        # Eq. 10: power-law angstrom for spectral b_bp
        Y = 2 * (1 - 1.2 * math.exp(-0.9 * rrs_440 / rrs_555))
        
        # Absorption of water at 750 nm
        a_w_750 = 2.47 # m-1, Smith and Baker table 1 
        
        # Backscattering of water at 750 nm
        b_bw_750 = find_b_bw(750)
        
        # Error function for particle backscattering at 750 nm
        def error_func(b_bp):
            return model_rrs(a_w_750, b_bw_750, b_bp) - rrs_750

        b_bp_750 = fsolve(error_func, 0.001)[0]

        # For each wavelength         
        for R_wl in R_array:
                        
            wl =        R_wl[0]
            Rw_wl =    R_wl[1] # shaded R
            rrs_wl =    R_wl[2]
            
            print(str(wl) + ' nm')
            
            # Skip np.nan  
            if np.isnan(rrs_wl): 
                print('   nan')
                continue
            
            # Turn negative to np.nan 
            if rrs_wl < 0: 
                print ('   negative')
                df.at[index, 'R' + str(wl)] = np.nan
                continue
            
            # Smooth
            rrs_wl = smooth_rrs(rrs_wl)
            
            # Backscattering of water, particles, and total
            b_bw_wl = find_b_bw(wl)
            b_bp_wl = b_bp_750 * (750 / wl)**Y
            b_b_wl = b_bw_wl + b_bp_wl
            
            # Error function for spectral absorption 
            def error_func(a_wl):
                return model_rrs(a_wl, b_bw_wl, b_bp_wl) - rrs_wl
            a_wl = fsolve(error_func, 0.001)[0]
            
            # Calculate K, Eq. 4
            K = (np.sin(theta_w_rad) + 1.15) * np.exp(-1.57 * b_b_wl) * a_wl + \
                (5.62 * np.sin(theta_w_rad) - 0.23) * np.exp(-0.5 * a_wl) * b_b_wl
            
            # Calculate ep, Eq. 3
            ep = 1 - np.exp(-K * radius / np.tan(theta_w_rad))
            print(f'   ep: {ep:.5f}')
                        
            # Correction 
            df.at[index, 'R' + str(wl)] = Rw_wl / (1 - ep)

    # Stop logging 
    if to_log: sys.stdout = orig_stdout

    # Output
    df.to_csv(file_out, index=False)
