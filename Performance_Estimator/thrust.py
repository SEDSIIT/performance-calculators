'''
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
#############################################################################
Multiple rocket motors profiles will be defined here.

The goal is to use Thrustcurve.org's API to get actual thrust curves 
from real motors. The link to API: https://www.thrustcurve.org/info/api.html

For now we are just going to manually define a motor as a placeholder
#############################################################################
'''

def total_thrust (vehicle, flags, time): # to do 
    if (time < 2.75): # these figures are based off of O5289X-PS motor
        thrust = 6227
    elif (2.75 <= time and time < 4.5):
        thrust  = -3560 * (time - 2.75) +  3560
    else:
        flags.MECO = True
        thrust = 0
    return thrust # Newtons
