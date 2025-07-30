# Written by Yulun Wu 
# June 23, 2025


def model_rrs(a, b_bw, b_bp):
    import math
    
    g_w = 0.113
    g0 = 0.197 
    g1 = 0.636
    g2 = 2.552
    
    b_b = b_bw + b_bp
    
    # Eq. 7
    g_p = g0 * (1 - g1 * math.exp(-g2 * b_bp / (a + b_b)))
    
    # Eq. 6
    rrs_mod = g_w * b_bw / (a + b_b) + g_p * b_bp / (a + b_b)
    
    return(rrs_mod)
    