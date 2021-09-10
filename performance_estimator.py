'''
This is a calculator to estimate the needed ISP and other performance 
metrics required for a rocket to achieve the desired height.

This program is heavily inspired by the OpenRocket technical documentation
link to documentation: http://openrocket.sourceforge.net/techdoc.pdf

To Do:
- better define the rocket 
- fix up drag equations and include them in calculation
- fix thrust for multistaging and easily swap motor profiles
- present calculations better
'''
### Include Start ###
import matplotlib.pyplot as plt
import numpy as np
from ambiance import Atmosphere
### Include End ###

### User Define Start ###
altitude_start = 0 # meters (from sea level)
altitude_end = 9150 # meters
delta_time = 0.01 # time step (sec)
class vehicle:
    # Overall Dimensions
    mass = 30 # mass (kg)
    diameter = 0.127 # overall diameter (m)
    length = 3.60 # overall length (m)

    # Staging
    stage = 1 # number of desired stages (1+)
    stage_altitude = [4000] # target staging altitiude (m)
    stage_mass = [10] # mass of each stage (kg)

    # Surface finish
    surface_roughness = 20e-6 # approximate surface roughness (m)
    fineness_ratio = 1 # ? (For skin drag)
    
    # Staging Configuration
    class staging:
        staging_enabled = True

        class stage0: # Payload
            length = 1.0 # meters
            class mass:
                dry = 10 # empty mass (kg)
                payload = 3.75 # payload (kg)
                avionics = 1 # avionicss (kg)
            # Fin Configuration
            class fin: # Assumes trapezoidal shape
                number_of_fins = 3
                thickness = 3e-3 # thickness of fin (m)
                root_length = 0.3 # root length (m)
                tip_length = 0.15 # tip length (m)
                height = 0.07 # fin height (m)
                edge_type = 1 # 0 for rectangular profile, 1 for rounded edges, 2 for airfoil
            class motor:
                pass
             # Boat Tail Configuration
            class boattail:
                enabled = False
                diameter_top = 0.127 # top diameter (m)
                diameter_bottom = 0.1 # bottom diameter (m)
                height = 0.2 # height (m)

        class stage1: # Booster
            length  = 1.2 # meters
            class mass:
                dry = 10 # kg
                payload = 0 # kg
                avionics = 0.25 # kg
            # Fin Configuration
            class fin: # Assumes trapezoidal shape
                number_of_fins = 3
                thickness = 3e-3 # thickness of fin (m)
                root_length = 0.3 # root length (m)
                tip_length = 0.15 # tip length (m)
                height = 0.07 # fin height (m)
                edge_type = 1 # 0 for rectangular profile, 1 for rounded edges, 2 for airfoil
            class motor:
                pass
            # Boat Tail Configuration
            class boattail:
                enabled = False
                diameter_top = 0.127 # top diameter (m)
                diameter_bottom = 0.1 # bottom diameter (m)
                height = 0.2 # height (m)

    # Nose Cone Configuration
    class nosecone: # Assumes cone shape (for now)
        height = 0.5 # height (m)
        diameter = 0.127 # diameter (m)
        surface_area = np.pi * (diameter/2) * np.sqrt(height**2 + (diameter/2)**2)

    # Other
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

def mach_num(height, velocity):
    properties = Atmosphere(height)
    mach = velocity / properties.speed_of_sound
    return mach

def deg_to_rad(deg):
    rad = deg * np.pi / 180
    return rad

def rad_to_deg(rad):
    deg = rad * 180 / np.pi
    return deg

def drag_nosecone (height, velocity): # to do
    mach = mach_num(height, velocity)
    cone_angle = deg_to_rad(90) - np.arctan(vehicle.nosecone.height / (vehicle.nosecone.diameter/2))
    Cd0 = 0.8 * (np.sin(cone_angle))**2 # 3.86
    a, b = 0.01 # Need to find what these are
    Cd = a * mach**b + Cd0 # 3.87
    return Cd

def drag_skinfriction (height, velocity):
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

    # Total friction drag coefficient (3.85)
    #Cd = C_f *((1 + 1 / (2*fin)))/(vehicle.A_ref)
    return drag

def drag_boattail(Cd_base):
    length_to_height_ratio = vehicle.boattail.height / (vehicle.boattail.diameter_top - vehicle.boattail.diameter_bottom)
    if (length_to_height_ratio <= 1):
        gamma = 1
    elif (length_to_height_ratio > 3 and length_to_height_ratio < 1):
        gamma = (3 - length_to_height_ratio) / 2
    else:
        gamma = 0
    # 3.88
    Cd_boattail = ((np.pi * vehicle.boattail.diameter_top**2) / (np.pi * vehicle.boattail.diameter_top**2)) * gamma
    return Cd_boattail

def drag_base (height, velocity):
    mach = mach_num(height,velocity)
    if (mach < 1): # 3.94
        Cd = 0.12 + 0.13*mach**2
    else:
        Cd = 0.25 / mach
    return Cd

def drag_fin (height, velocity): # Assumes rounded profile (for now)
    mach = mach_num(height, velocity)
    # 3.89
    if (mach < 0.9):
        Cd_le = (1 - mach**2)**-0.147 - 1
    elif (0.9 < mach and mach < 1):
        Cd_le = 1 - 1.785 * (mach - 0.9)
    else:
        Cd_le = 1.214 - (0.502 / mach**2) + (0.1095 / mach**4)
    # 3.92 / 3.94
    if (mach < 1):
        Cd_te = 0.12 + 0.13 * mach**2
    else:
        Cd_te = 0.25 / mach

    Cd = Cd_le + Cd_te # 3.93
    return Cd

def drag_parasitic (): # to do 
    Cd = 1
    return Cd

def total_drag (height, velocity): # to do 
    drag_force = 100
    return drag_force # Newtons

def total_thrust (time): # to do 
    if (time < 2.75): # these figures are based off of O5289X-PS motor
        thrust = 6227
    elif (2.75 <= time and time < 4.5):
        thrust  = -3560 * (time - 2.75) +  3560
    else:
        thrust = 0
    return thrust # Newtons

def total_mass (time):
    mass = vehicle.mass
    return mass
### Function Define End ###

### Setup Start ###
altitude_current = altitude_start
altitude_previous = altitude_current
iteration = 0
time = 0
velocity = 0
velocity_previous = 0

class data:
    time = []
    altitude = []
    velocity = []
    acceleration = []
    thrust = []
    drag = []
### Setup End ###

### Main Start ###
'''
Current method of estimating height is pretty elementary (for now)
Uses basic F = MA to model the flight of the rocket
Assumes: 
 - The rocket goes only straight up
 - gravity remains constant
 - is stable
'''
while (altitude_current < altitude_end):
    drag = total_drag(altitude_current, velocity)
    thrust = total_thrust(time)
    mass = total_mass(time)
    acceleration = ((thrust - drag) / mass) - 9.81 
    velocity = velocity_previous + acceleration * delta_time
    altitude_current = (velocity_previous + velocity) * (delta_time / 2) + altitude_previous

    # Give an update of the calculation to the user
    if ((round(time, 2) % 1) == 0):
        print("Current time : %2.0f sec     Alt: %3.0f m     Vel: %3.0f m/s" % (time, altitude_current, velocity))

    # Stop loop if goal is not achieved
    if (time > 10 and altitude_current <= 0):
        print("WARNING: Objective altitude not achieved!")
        break

    # Save data to display
    data.time.append(time)
    data.altitude.append(altitude_current)
    data.acceleration.append(acceleration)
    data.velocity.append(velocity)
    data.thrust.append(thrust)
    data.drag.append(drag)

    # Time step
    velocity_previous = velocity
    altitude_previous = altitude_current
    time += delta_time

# Show results
fig, ax = plt.subplots()
ax.plot(data.time, data.altitude)

ax.set(xlabel='Time (s)', ylabel='Altitude (m)', title='Rocket Performance')
ax.grid()

plt.show()

### Main End ###