"""
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is used to estimate the max theoretical range we can expect with a RF 
transmitter and reciever
"""
import numpy as np
import matplotlib.pyplot as plt

class system:
    class enviroment:
        fade_margin = 12 # dBm (losses due to atmospheric effects + others) <--- find a more accurate number 
        noise_floor = -120 #dBm (background noise)
    class RF_system:
        RF_Frequency = 433 # MHz
        TX_power = 20 # dBm
        RX_sensitivity = -117 # dBm
        gains = 3 # dBm (gains from antennas)
        losses = 0 # dBm (losses in cables, etc.)<--- Find a more accurate number 

def calc_max_path_loss(system):
    if (system.enviroment.noise_floor > system.RF_system.RX_sensitivity):
        rx_sensitivity = system.enviroment.noise_floor
    else:
        rx_sensitivity = system.RF_system.RX_sensitivity
    max_path_loss = system.RF_system.TX_power - rx_sensitivity + system.RF_system.gains - \
                    system.RF_system.losses - system.enviroment.fade_margin
    return max_path_loss

def calc_RF_range(max_path_loss, RF_frequency):
    RF_range = np.power(10, (max_path_loss - 32.44 - 20*np.log10(RF_frequency))/20)
    return RF_range


def main():
    max_path_loss = calc_max_path_loss(system)
    print("Max Path Loss: %0.2f dBm" % (max_path_loss))
    print("Theoretical Max RF Range: %0.2f Km" % (calc_RF_range(max_path_loss,system.RF_system.RF_Frequency)))
    
    # Try to get an idea of what the range will be like with different parameters
    path_loss = np.arange(70, 130)
    RF_range = calc_RF_range(path_loss,system.RF_system.RF_Frequency)
    plt.figure(1)
    plt.plot(RF_range, path_loss, color="black")
    plt.xlabel("Range (km)")
    plt.ylabel("Maximum path loss (dBm)")
    plt.title("Maximum Path Loss Versus Range for 433MHz")
    plt.grid()
    plt.show()


if (__name__ == "__main__"):
    main()