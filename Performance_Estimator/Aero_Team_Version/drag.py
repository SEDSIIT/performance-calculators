'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#############################################################################
These drag equations were heavily inspired by the OpenRocket technical documentation
link to documentation: http://openrocket.sourceforge.net/techdoc.pdf
#############################################################################
'''
import numpy as np


def drag_nosecone (vehicle, air_properties, velocity): # to do
    dynamic_pressure = 0.5 * air_properties.density * velocity**2
    mach = velocity / air_properties.speed_of_sound
    cone_angle = (90*np.pi/180) - np.arctan(vehicle.nosecone.height / (vehicle.nosecone.diameter/2))
    Cd0 = 0.8 * (np.sin(cone_angle))**2 # 3.86
    a, b = 0.01 #  <--------------------- -----------Need to find what these are
    Cd = a * mach**b + Cd0 # 3.87
    drag = Cd * dynamic_pressure * vehicle.nosecone.reference_area
    return drag

def drag_skinfriction (vehicle, velocity,  mach, density, Re): # (done?)
    R_crit = 51 * (vehicle.surface_roughness / vehicle.length)**(-1.039)

    # Calculating skin friction coefficient (3.81)
    if (Re > R_crit):
        C_f = 0.032 * (vehicle.surface_roughness / vehicle.length)**0.2
    elif(Re > 1e4 and Re <= R_crit):
        C_f = 1 / (1.50 * np.log(Re) - 5.6)**2
    else:
        C_f = 1.48 * 10**-2

    # Compressibility corrections
    C_f_roughness = C_f / (1 + 0.18 * mach**2)
    if (mach > 1):
        C_f = C_f / (1 + 0.15 * mach**2)**0.58 # 3.83
    else:
        C_f = C_f * (1 - 0.1 * mach**2) # 3.82
    if (C_f_roughness > C_f): # 3.84 Check if roughness limited
        C_f = C_f_roughness
    '''
    if (flags.booster_seperation == False):
        wetted_area = vehicle.wetted_area_staged
    else:
        wetted_area = vehicle.wetted_area
    '''
    wetted_area = vehicle.wetted_area
    drag = 0.5 * C_f * density * (velocity**2) * wetted_area
    return drag

def drag_boattail(vehicle, Cd_base):
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

def drag_base (vehicle, mach, dynamic_pressure):
    if (mach < 1): # 3.94
        Cd = 0.12 + 0.13*mach**2
    else:
        Cd = 0.25 / mach
    '''
    if (flags.booster_seperation == True):
        pass
    else:
        pass
    '''
    return Cd

def drag_fin (mach): # Assumes rounded profile (for now)
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

def total_drag (vehicle, flags, air_properties, velocity, Re): # to do 
    mach = velocity / air_properties.speed_of_sound
    dynamic_pressure = 0.5 * air_properties.density * velocity**2
    density = air_properties.density
    skin_drag = drag_skinfriction(vehicle, velocity, mach, density, Re)
    
    drag_force = skin_drag #+ drag_base + drag_fin + drag_nosecone
    return drag_force # Newtons