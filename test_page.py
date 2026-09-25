import math
M_initial = 1000.0
M_t = 1.0
S_bh = 4 * math.pi * M_t**2
S_rad_coarse = 4 * math.pi * (M_initial**2 - M_t**2) * (4.0/3.0) 
print("S_bh:", S_bh)
print("S_rad_coarse:", S_rad_coarse)
print("min:", min(S_rad_coarse, S_bh))
