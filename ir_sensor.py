import numpy as np 
import eseries as eseries

#constants
v_ref = 2.5 # v 
f_beacon = 3333 # hz

#formatting
ljust = 40

### TRANSRESISTOR
# convert current from phototransistor into voltage, with gain 
ltr_scale=2.4e-3 # mA / mW/cm^2s
r_3 = 4.7e3

# calculations 
def get_intensity(V, v_ref=v_ref, sense=ltr_scale, r=r_3):
    return (v_ref-V) / (sense*r)

def transresistor(I, v_ref=v_ref, sense=ltr_scale, r=r_3):
    return v_ref - (sense * I * r)

def scale_intensity(x, x_1=0.2, I_1=0.07352941):
    return I_1 * x_1**2/x**2

def find_by_corner_freq(f, r=None, c=None, r_series = eseries.E24, c_series=eseries.E3):
    # f  = 1/(2*np.pi*c *r )
    if r is None and c is None:
        raise ValueError("either r or c must be provided")
    
    if c is None:
        c = 1/(2*np.pi*r*f)
    c = eseries.find_nearest(c_series, c)

    if r is None:
        r = 1/(2*np.pi*c*f)
    r = eseries.find_nearest(r_series,r)

    f = 1/(2*np.pi*c *r )
    return f, r, c


# est. signal intensity ?????
# I_target = (2.58-2.38)/(ltr_scale*490)
# print(f"target intensity: {I_target}")

# compute values, based on experimental data
# background 
V_bg = 2.32
I_bg = get_intensity(V_bg, r=4.7e3)

# measurement 
V_meas = 1.56
x_meas = .2 
I_meas = get_intensity(V_meas, r=4.7e3)

# extrapolate
I_meas_beacon = I_meas-I_bg
x_targ = np.array([0.5, 1, 2.75])
I_targ_beacon = scale_intensity(x_targ, x_1 = x_meas, I_1=I_meas_beacon)
I_targ = I_targ_beacon + I_bg
A_signal = V_bg - transresistor(I_targ)

sat_x = 0.1 # distance at saturation 
V_max = 0
I_max = get_intensity(V_max, r=4.7e3)

print("TRANSRESISTOR")
print(f"  Background Intensity:".ljust(ljust," "),             f"{I_bg:0.4e} mW/cm^2")
print(f"  Total Intensity at {x_meas}m:".ljust(ljust," "),     f"{I_meas:0.4e} mW/cm^2")
print(f"  Signal Intensity at {x_meas}m:".ljust(ljust," "),    f"{I_meas_beacon:0.4e} mW/cm^2")
print(f"  Est. {x_targ}m Signal:".ljust(ljust," "),            f"{I_targ_beacon} mW/cm^2")
print(f"  Max Intensity:".ljust(ljust," "),                    f"{I_max:0.4e} mW/cm^2")
print()
print(f"  Reference Voltage".ljust(ljust," "),                 f"{v_ref:0.4e} V")
print(f"  Background Voltage:".ljust(ljust," "),               f"{transresistor(I_bg):0.4e} V")
print(f"  Max Int. Voltage:".ljust(ljust," "),                 f"{transresistor(I_max):0.4e} V")
print(f"  Est. {x_targ}m Signal Amplitude:".ljust(ljust," "),       f"{A_signal} V")
print()

### FILTER 1
# ac coupling filter 
f_c1_target = 1000

r_4 = 470e3

f_c1, r_4, c_2 = find_by_corner_freq(f_c1_target, r=r_4)

# c_2 = 470e-12
# r_4 = 470e3
# f_c1 = 1/(2*np.pi*c_2*r_4)

print("AC COUPLING")
print(f"  Target Corner Freq:".ljust(ljust," "), f"{f_c1_target:0.4e} hz")
print(f"  R_4, C_2:".ljust(ljust," "), f"{r_4:0.2e}ohm, {c_2:0.2e}F")
print(f"  Corner Frequency:".ljust(ljust," "), f"{f_c1:0.4e} hz")
print(f"  Reference Voltage:".ljust(ljust," "), f"{v_ref:0.4e} V")
print()

### GAIN 1
# r_5 = 2.2e3
gain1_target = 40
gbw_LM6144 = 10e6 # 10 mhz gain bandwidth
A = gbw_LM6144 / f_beacon # open loop gain

# gain resistors
r_5 = 10
r_6 = (gain1_target-1)*r_5
r_6 = eseries.find_nearest(eseries.E24, r_6)

gain_1 = 1 + r_6/r_5

# output filter 
f_c2_target = 1000
r_7 = 100*r_6
f_c1, r_7, c_3 = find_by_corner_freq(f_c2_target, r=r_7)

A_signal *= gain_1

# ninv: v_g1_out = v_ref + (v_ref-v_g1_in) * r_6/r_5
print("GAIN STAGE 1")
print(f"  Open Loop Gain (ref): ".ljust(ljust," "), f"{20*np.log10(A):0.2f} dB")
print(f"  Target Gain :".ljust(ljust), f"{gain1_target:0.2f}")
print(f"  R_5, R_6:".ljust(ljust," "), f"{r_5:0.2e}ohm, {r_6:0.2e}ohm")
print(f"  Gain1 rel2 {v_ref}v:".ljust(ljust," "), f"{gain_1:0.4e}")
print(f"  Output High-Pass:".ljust(ljust," "), f"{1/(2*np.pi*c_3*r_7):0.4e} hz")
print(f"  R_4, C_2:".ljust(ljust," "), f"{r_7:0.2e}ohm, {c_3:0.2e}F")
print()
print(f"  Est. {x_targ}m Signal Amplitude: ".ljust(ljust," "), f"{abs(A_signal)} V")
print()

### GAIN 2
# r_5 = 2.2e3
gain2_target = 9
gbw_LM6144 = 10e6 # 10 mhz gain bandwidth
A = gbw_LM6144 / f_beacon # open loop gain

# gain resistors
r_8 = 100
r_9 = (gain2_target-1)*r_8
r_9 = eseries.find_nearest(eseries.E24, r_9)

gain_2 = 1 + r_9/r_8

# output filter 
f_c3_target = 500
r_10 = 100*r_9
f_c3, r_10, c_4 = find_by_corner_freq(f_c3_target, r=r_10)

A_signal *= gain_2


# ninv: v_g1_out = v_ref + (v_ref-v_g1_in) * r_6/r_5
print("GAIN STAGE 2")
print(f"  Open Loop Gain (ref): ".ljust(ljust," "), f"{20*np.log10(A):0.2f} dB")
print(f"  Target Gain :".ljust(ljust," "), f"{gain2_target:0.2f}")
print(f"  R_8, R_9:".ljust(ljust," "), f"{r_8:0.2e}ohm, {r_9:0.2e}ohm")
print(f"  Gain2 rel2 {v_ref}v:".ljust(ljust," "), f"{gain_2:0.4e}")
print(f"  Output High-Pass:".ljust(ljust," "), f"{f_c3:0.4e} hz")
print(f"  R_10, C_4:".ljust(ljust," "), f"{r_10:0.2e}ohm, {c_4:0.2e}F")
print()
print(f"  Est. {x_targ}m Signal Amplitude: ".ljust(ljust," "), f"{abs(A_signal)} V")
print()

### Band Pass
# LOW PASS
f_c4_target = 15000
c_5 = 22e-12
f_c4, r_11, c_5 = find_by_corner_freq(f_c4_target,c=c_5)

# print(f"  High-Pass:".ljust(ljust," "), f"{1/(2*np.pi*c_4*r_10):0.4e} hz")
print(f"  Final Low-Pass:".ljust(ljust," "), f"{f_c4:0.4e} hz")
print(f"  R_11, C_5:".ljust(ljust," "), f"{r_11:0.2e}ohm, {c_5:0.2e}F")
