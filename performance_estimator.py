'''
This is a calculator to estimate the needed ISP and other performance 
metrics required for a rocket to achieve the desired height.

This program is heavily inspired by the OpenRocket technical documentation
link to documentation: http://openrocket.sourceforge.net/techdoc.pdf
'''
### Include Start ###
import matplotlib.pyplot as plt
import numpy as np
from ambiance import Atmosphere
### Include End ###

### User Define Start ###
altitude_start = 0 # meters (from sea level)
altitude_end = 9150 # meters
class vehicle:
    mass = 30 # mass (kg)
    diameter = 0.127 # overall diameter (m)
    length = 3.60 # overall length (m)
    stage = 1 # number of desired stages (1+)
    stage_altitude = [4000] # target staging altitiude (m)
    stage_mass = [10] # mass of each stage (kg)
    surface_roughness = 20e-6 # approximate surface roughness (m)
    A_ref = np.pi * (diameter / 2)**2 # m^2
    A_wet =  2 * np.pi * diameter * length # approximate rocket area as cylinder
### User Define End ###

### Function Define Start ###
def reynolds_num(height, velocity):
    properties = Atmosphere(height)
    density = properties.density
    dynamic_viscosity = properties.dynamic_viscosity
    RE = (density * velocity * vehicle.length) / dynamic_viscosity
    return RE

def skin_friction_drag(height, velocity):
    properties = Atmosphere(height)
    density = properties.density
    R_crit = 51 * (vehicle.surface_roughness / vehicle.length)**(-1.039)
    Re = reynolds_num(height,velocity)

    # Calculating skin friction coefficient (3.81)
    if (Re > R_crit):
        C_f = 0.032 * (vehicle.surface_roughness / vehicle.length)**0.2
    elif(Re > 1e4 and Re <= R_crit):
        C_f = 1 / (1.50 * np.log(Re) - 5.6)**2
    else:
        C_f = 1.48 * 10**-2

    # Compressibility corrections
    mach = velocity / properties.speed_of_sound 
    C_f_roughness = C_f / (1 + 0.18 * mach**2)
    if (mach > 1):
        C_f = C_f / (1 + 0.15 * mach**2)**0.58 # 3.83
    else:
        C_f = C_f * (1 - 0.1 * mach**2) # 3.82
    if (C_f_roughness > C_f): # 3.84 Check if roughness limited
        C_f = C_f_roughness
    
    
    drag = 0.5 * C_f * density * (velocity**2) * vehicle.A_wet 
    return drag
### Function Define End ###

### Setup Start ###
### Setup End ###

### Main Start ###
drag = skin_friction_drag(5000, 200)
print(drag)
'''
t = np.arange(0.0, 2.0, 0.01)
s = 1 + np.sin(2 * np.pi * t)

fig, ax = plt.subplots()
ax.plot(t, s)

ax.set(xlabel='time (s)', ylabel='Y', title='Title')
ax.grid()

plt.show()
'''
### Main End ###