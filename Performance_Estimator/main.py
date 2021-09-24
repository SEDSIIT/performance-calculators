'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#############################################################################
This is a calculator to estimate the needed ISP and other performance 
metrics required for a rocket to achieve the desired height.

This program is heavily inspired by the OpenRocket technical documentation
link to documentation: http://openrocket.sourceforge.net/techdoc.pdf

Drag, thrust, and vehicle were moved to seperate files to improve readability

To Do:
- better define the rocket in vehicle.py
- fix up drag equations
- fix thrust for multistaging and easily swap motor profiles
- adjust EOMs to include unit vectors for 3 or 6 DOFs
- present results in a nicer format
#############################################################################
'''

### Include Start ###
import matplotlib.pyplot as plt
import numpy as np
from ambiance import Atmosphere
from drag import total_drag
from thrust import total_thrust
from vehicle import vehicle
### Include End ###

### User Define Start ###
altitude_start = 0 # meters (from sea level)
altitude_end = 9150 # meters
delta_time = 0.01 # time step (sec)
### User Define End ###

### Function Define Start ###
def mach_num(height, velocity):
    properties = Atmosphere(height)
    mach = velocity / properties.speed_of_sound
    return mach

def reynolds_num(height, velocity):
    properties = Atmosphere(height)
    density = properties.density
    dynamic_viscosity = properties.dynamic_viscosity
    RE = (density * velocity * vehicle.length) / dynamic_viscosity
    return RE

def total_mass (time): # to do
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

class flags:
    MECO = False
    booster_seperation = False
    SECO = False
    max_q = False
    apogee = False
    class drogue_deploy:
        sustainer = False
        booster = False
    class main_deploy:
        sustainer = False
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
    air_properties = Atmosphere(altitude_current)
    Re = reynolds_num(altitude_current, velocity)
    drag = total_drag(vehicle, flags, air_properties, velocity, Re)
    thrust = total_thrust(vehicle, flags, time)
    mass = total_mass(time)
    acceleration = ((thrust - drag) / mass) - 9.81  # Need to fix calc error (drag force always downwards)
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

#ax.plot(data.time, data.drag)
#ax.set(xlabel='Time (s)', ylabel='Drag Force (N)', title='Rocket Performance')

ax.plot(data.time, data.altitude)
ax.set(xlabel='Time (s)', ylabel='Altitude (m)', title='Rocket Performance')
ax.grid()

plt.show()
### Main End ###