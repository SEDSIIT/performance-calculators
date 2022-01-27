'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

INFO:
Calculates fin flutter speeds at varying altitudes and based off of this 
documentation: https://apogeerockets.com/education/downloads/Newsletter291.pdf

WARNING:
Assumes fin is a trapizoidal shape
Simulated flight data was exported directly from OpenRocket

HOW TO USE:
Need to only edit where the arrows (<---) are to change parameters for
different fins/rockets the rest can be left unchanged. Run the script then
a plot should show.

Written By: Michael Gromski
'''
from ntpath import join
from ambiance import Atmosphere
import matplotlib.pyplot as plt
import numpy as np
import csv
import os.path

class fin: # <---------------- Edit fin dimensions here
    root_chord = 6.900 # inches
    tip_chord = 2.953 # inches
    height = 2.953 # inches
    thickness = 0.157 # inches
    shear_modulus = 280000 # PSI 

class flight_sim_data: # <----- Edit sim file name here
    class sustainer:
        filename = 'Big_Red_Sustainer.csv'
        altitude = []
        speed = []
    class booster:
        filename = 'Big_Red_Booster.csv'
        altitude = []
        speed = []

def calc_flutter_velocity(altitude):
    altitude = altitude * 0.3048 # Convert to meters because of ambiance library
    flightlevel = Atmosphere(altitude)

    S = 0.5 * (fin.root_chord + fin.tip_chord) * fin.height
    AR = (fin.height)**2 / S
    LAMBDA = fin.tip_chord / fin.root_chord
    speed_of_sound = flightlevel.speed_of_sound * 3.28084 # convert to ft/s
    air_pressure = flightlevel.pressure / 6895 # convert to psi
    
    num_1 = fin.shear_modulus
    num_2 = 1.337 * air_pressure * (LAMBDA + 1) * AR**3
    den_1 = 2 * (AR + 2) * (fin.thickness / fin.root_chord)**3
    den_2 = num_2 / den_1
    flutter_speed = speed_of_sound * np.sqrt(num_1 / den_2)
    return flutter_speed

def get_flight_data(filepath):
    file = open(filepath)
    type(file)
    fileobject = csv.reader(file)
    alt = []
    speed = []
    for row in fileobject:
        alt.append(float(row[0]) * 3.281)
        speed.append(float(row[1]) * 3.281)
    file.close()
    return alt, speed

def main(): 
    ### Setup Start ###
    altitude = 0 # <------------- Edit calc range here
    max_altitude = 35000 # feet
    altitude_step = 100

    PATH = os.path.dirname(__file__)
    filepath_sustainer_flight = join(PATH,flight_sim_data.sustainer.filename)
    filepath_booster_flight = join(PATH, flight_sim_data.booster.filename)

    flight_sim_data.sustainer.altitude, flight_sim_data.sustainer.speed = get_flight_data(filepath_sustainer_flight)
    flight_sim_data.booster.altitude, flight_sim_data.booster.speed = get_flight_data(filepath_booster_flight)
    flutter_data = []
    altitude_data = []
    ### Setup End ###

    ### Main Loop Start ###
    while(altitude<max_altitude):
        flutter_data.append(calc_flutter_velocity(altitude))
        altitude_data.append(altitude)
        altitude = altitude + altitude_step
    ### Main Loop End ###

    # Create plot of data
    plt.figure()
    plt.plot(altitude_data, flutter_data, color="red", label="Flutter Speed")
    plt.plot(flight_sim_data.sustainer.altitude, flight_sim_data.sustainer.speed, color="blue", label="Sustainer Stage")
    plt.plot(flight_sim_data.booster.altitude, flight_sim_data.booster.speed, color="green", label="Booster Stage")
    plt.title("Fin Flutter Speed Versus Altitude")
    plt.xlabel("Altitude (ft)")
    plt.ylabel("Speed (ft/s)")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
