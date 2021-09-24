'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#############################################################################
The vehicle class will be defined seperately here. 
#############################################################################
'''
pi = 3.14159265359

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
        staging_enabled = False

        class stage0: # Payload + Sustainer
            length = 1.0 # meters
            diameter = 0.127 # meters
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
                # Calculated Parameters
                surface_area = number_of_fins * ((root_length + tip_length)*height + \
                    (tip_length * thickness) + ((root_length-tip_length)**2 + height**2)**(1/2) * thickness)
                #Leading and trailing edge area is an estimation
                base_area = number_of_fins * thickness * height
            class motor:
                pass
             # Boat Tail Configuration
            class boattail:
                enabled = False
                diameter_top = 0.127 # top diameter (m)
                diameter_bottom = 0.1 # bottom diameter (m)
                height = 0.2 # height (m)

        class stage1: # Booster
            length = 1.2 # meters
            diameter = 0.127 # meters
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
                # Calculated Parameters
                surface_area = number_of_fins * ((root_length + tip_length)*height + \
                    (tip_length * thickness) + ((root_length-tip_length)**2 + height**2)**(1/2) * thickness)
                #Leading and trailing edge area is an estimation
                base_area = number_of_fins * thickness * height
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
        surface_area = pi * (diameter/2) * (height**2 + (diameter/2)**2)**(1/2)
        reference_area = pi * (diameter / 2)**2

    # Calculated parameters
    reference_area = pi * (diameter / 2)**2 # m^2
    
    body_surface_area_staged = pi * ((staging.stage0.diameter / 2)**2) * staging.stage0.length +\
                        pi * ((staging.stage1.diameter / 2)**2) * staging.stage1.length
    wetted_area_staged = body_surface_area_staged + nosecone.surface_area + \
                staging.stage0.fin.surface_area + staging.stage1.fin.surface_area

    body_surface_area = pi * ((staging.stage0.diameter / 2)**2) * staging.stage0.length
    wetted_area = body_surface_area + nosecone.surface_area + staging.stage0.fin.surface_area