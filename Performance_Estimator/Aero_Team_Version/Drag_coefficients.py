# -*- coding: utf-8 -*-
"""
Created on Sun Oct 24 16:50:04 2021

@author: bisha
"""

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

     #Almost Done!
def drag_nosecone (vehicle, air_properties, velocity):  
    #please go to appendix B to solve for this depending on the type of nose cone
    #height = 0.5 m
    #diameter = 0.127 m
    cone_angle = (90*np.pi/180) - np.arctan(vehicle.nosecone.height / (vehicle.nosecone.diameter/2))
    Cd0 = 0.8 * (np.sin(cone_angle))**2 # Equation 3.86
    #Subsonic
    dynamic_pressure = 0.5 * air_properties.density * velocity**2
    mach = velocity / air_properties.speed_of_sound
    half_appex_angle = np.degrees(np.arctan((0.127/2)/0.5))
    appex_angle = 2*half_appex_angle
    Cd0 = 0.8 * (np.sin(cone_angle))**2 # Equation 3.86
    
    
    #a, b = 0.01 #  <--------------------- -----------Need to find what these are)
    #I think a and b can calculated from M=0.995, Cd = 0.1 and M=0.99 and Cd=0.095.
    #These values are approximated from experimental data for nose cone with fineness=3.
    #https://ntrs.nasa.gov/api/citations/19930087953/downloads/19930087953.pdf
    
    #Fineness ratio: 0.5/0.127 = 3.937
    
    #For 1<mach<1.3
    if (1<mach and mach<1.3):
    #From polynomial interpolation
       Cd = 0.142807 - 0.0168189*mach
    
    #Drag coefficient for M>=1.3
    elif (mach >= 1.3):
       halfappex_angle = np.degrees(np.arctan((0.127/2)/0.5))
       Cd = 2.1*np.sin(2*(halfappex_angle)) + (0.5*np.sin(halfappex_angle))/np.sqrt(mach**2-1)
    
    else:
        a = -0.676301
        b = -1.45158
        if (mach <= 0): # divide by zero patch
            mach = 1e-8
        Cd = a * mach**b + Cd0 # Equation 3.87 
    
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



#drag_boattail is based on drag_base and I think its okay; it is stated that the 
#equations for the boattail drag in the documentation are primarly used for subsonic regime, 
#however, they use the same for the supersonic regime. The only difference for the supersonic regime is that a warning 
#may be generated for transonic speeds.

def drag_boattail(vehicle, Cd_base):
    length_to_height_ratio = vehicle.boattail.height / (vehicle.boattail.diameter_top - vehicle.boattail.diameter_bottom)
    if (length_to_height_ratio <= 1):
        gamma = 1
    elif (length_to_height_ratio > 3 and length_to_height_ratio < 1):
        gamma = (3 - length_to_height_ratio) / 2
    else:
        gamma = 0
    #Equation 3.88
    Cd_boattail = ((np.pi * vehicle.boattail.diameter_top**2) / (np.pi * vehicle.boattail.diameter_top**2)) * gamma
    return Cd_boattail



def drag_base (vehicle, mach, dynamic_pressure):
    if (mach < 1): # Equation 3.94
        Cd = 0.12 + 0.13*mach**2
    else:
        Cd = 0.25 / mach
    '''
    if (flags.booster_seperation == True):
        pass
    else:
        pass
    '''
    Base_area=np.pi*(0.127**2)/4
    drag=Cd * dynamic_pressure * Base_area
    return drag

def drag_fin (mach,dynamic_pressure): # Assumes rounded profile 

    # Equation 3.89
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

    Cd = Cd_le + Cd_te # Equation 3.93
    
    #Stage 0 fin dimensions: tip chord=0.08m, root chord=0.2m, height=0.08m, reference area = 0.0112m^2.
    #Stage 1 fin reference area: 0.0089125m^2. 
    
    Reference_area0 = 0.0112
    Reference_area1 = 0.0089125
    
    drag = 3*(Cd*dynamic_pressure*Reference_area0) + 3*(Cd*dynamic_pressure*Reference_area1)
    return drag

    

def drag_parasitic (mach,dynamic_pressure): 
    
    if (mach < 1):
        Cd = 1*(1+ (mach**2)/4 + (mach**2)/40)*0.85
    else:
        Cd = 1*(1.84 - 0.76/(mach)**2 + 0.166/(mach)**4 + 0.035/(mach)**6)*0.85
    return Cd

    A_parasitic = np.pi*0.0075**2
    drag = 2*(Cd*dynamic_pressure*A_parasitic)
    return drag

#In the OpenRocket Documentation, it mentions that source of parasitic drag in model rockets
#are the launch guides that protrude from the rocket body. Alternatives to launch lugs
#include replacing the tube with metal wire loops or attaching rail pins that
#hold the rocket on a launch rail. 

    

def total_drag (vehicle,flags,air_properties,velocity,Re): # to do 
     mach = velocity / air_properties.speed_of_sound
     dynamic_pressure = 0.5 * air_properties.density * velocity**2
     density = air_properties.density
     skin_drag = drag_skinfriction(vehicle, velocity, mach, density, Re)
     drag_cone = drag_nosecone (vehicle, air_properties, velocity)
     drag_base_=drag_base (vehicle, mach, dynamic_pressure)
     drag_fin_=drag_fin (mach,dynamic_pressure)
     drag_parasitic_=drag_parasitic (mach,dynamic_pressure)
    
     drag_force = skin_drag+drag_base_+drag_fin_+drag_cone+drag_parasitic_
     return drag_force
   
     print(drag_force)
    

    