'''
Created on 11.03.2016

@author: IMST GmbH
'''

'''===========================================================================
This script shows an example code which explains how to
        - connect a Radar Module with the desired interface
        - read some Radar specific parameters
        - setup the Radar Module
        - perform a frequency domain (FD) measurement and read the data
        - show the read data in a simple plot

In the first part an example class is shown which contains the basic functions
to communicate and measure with the Radar Module.
In the lower part it is shown how to handle this class in some examples. 
==========================================================================='''


'''
Imports
'''
# Main classes for the Ethernet interface
from Interfaces.Ethernet.EthernetConfig import EthernetParams
from Interfaces.Ethernet.IPConnection import IPConnection
from Interfaces.Ethernet.Commands import IPCommands

# Parameter and data classes
import ConfigClasses as cfgCl

# To create a simple plot
import matplotlib.pyplot as plt

import numpy as np
from time import time, sleep
import time

from sklearn.cluster import DBSCAN


'''
This example class loads all necessary parameter and data classes. It has functions
to connect a Radar Module via an interface specified by the user. It has also
functions to use the basic functions of the Radar Module.  
'''
class Main():
    def __init__(self):
        
        # initialize needed parameters classes
        self.hwParams = cfgCl.HwParams()
        self.sysParams = cfgCl.SysParams()
        self.htParams = cfgCl.HtParams()
        
        # initialize needed data classes
        self.FD_Data = cfgCl.FD_Data()
        self.TD_Data = cfgCl.TD_Data()
        self.HT_Targets = cfgCl.HtTargets()
        
        # load the Ethernet parameters and change them
        self.etherParams = EthernetParams()
        self.etherParams.ip = "10.0.0.59"
        self.etherParams.port = 1024
        
        self.myInterface = None
        self.connected = False
        self.error = False
        
        
    '--------------------------------------------------------------------------------------------'
    # function to connect to a specified interface
    def Connect(self):
        
        print('========================')
        print('Connect')

        self.myInterface = IPConnection(self)
        
        # try to connect
        if not self.myInterface.connect():
            print("Connection to "+self.etherParams.ip+":"+str(self.etherParams.port)+" failed.")
            self.error = True
            return
        
        # if the connection has been established, load the command class
        self.cmd = IPCommands(connection=self.myInterface, main_win=self)
        self.connected = True
            
    '--------------------------------------------------------------------------------------------'
    # function to get the Radar specific parameters
    def GetHwParams(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('GetHwParams')
        
        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_SEND_INFO")
        except:
            print("Error in receiving hardware parameters.")
            self.error = True
            return
        
        # if no error occurred, the received data can be found in hwParams
        
    '--------------------------------------------------------------------------------------------'
    # function to get the Radar system parameters
    def GetSysParams(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('GetSysParams')
        
        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_SEND_PARAMS")
        except:
            print("Error in receiving system parameters.")
            self.error = True
            return
        
        # if no error occurred, the received data can be found in sysParams
        
    '--------------------------------------------------------------------------------------------'
    # function to set the Radar system parameters
    def SetSysParams(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('SetSysParams')
        
        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_SETUP")
        except:
            print("Error in setting system parameters.")
            self.error = True
            return
        
    '--------------------------------------------------------------------------------------------'    
    # function to get frequency domain data with or without a previous measurement
    # the parameter 'measurement' specifies the type of measurement    
    # possible values are: "UP-Ramp", "DOWN-Ramp", "CW" or "None"
    def GetFdData(self, measurement="UP-Ramp"):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        # print('========================')
        # print('GetFdData')
        
        # execute the respective command ID
        try:
            if measurement == "UP-Ramp":
                self.cmd.execute_cmd("CMDID_UP_RMP_FD")                
            elif measurement == "DOWN-Ramp":
                self.cmd.execute_cmd("CMDID_DN_RMP_FD")
            elif measurement == "CW":
                self.cmd.execute_cmd("CMDID_GP_FD")
            elif measurement == None or measurement == "None":
                self.cmd.execute_cmd("CMDID_FDATA")
            else:
                print("No valid measurement type.")
                self.error = True
                return
            
        except:
            print("Error in receiving frequency domain data.")
            self.error = True
            return
        
        # the received data can be found in FD_Data
    
    '--------------------------------------------------------------------------------------------'
    # function to disconnect the connected interface
    def Disconnect(self):
        # do nothing if not connected
        if not self.connected:
            return
    
        print('========================')
        print('Disconnect')
        
        self.myInterface.disconnect()
            
        self.connected = False
            
'=================================================================================================='        
            
        
'''
/// Main Part ///

In the following it is shown how the Main class is used to connect a Radar
Module and to read/change some parameters.  
Later one of three examples can be chosen by setting the "if 0:" to "if 1:".
These examples are using some of the Main class functions to read measurement 
data and to plot it. 
'''
                
# Get an instance of the main class
main = Main()

# Specify your interface and try to connect it.
main.Connect()

# Read some Radar Module specific parameters
main.GetHwParams()

# These parameters can be accessed by e.g. main.hwParams.radarNumber
print("Number of the connected Radar Module: ", main.hwParams.radarNumber)

# Change some of the system parameters, e.g.
main.sysParams.minFreq = 24000
main.sysParams.manualBW = 600
main.sysParams.t_ramp = 7
main.sysParams.active_RX_ch = 15
main.sysParams.freq_points = 40 # Total distance, tic * freq_points

# Check if the frontend is off
if main.sysParams.frontendEn == 0:
    main.sysParams.frontendEn = 1   # turns it on

# Send the changed parameters to the Radar Module
main.SetSysParams()

# Always read back the system parameters because some read only parameters changed
main.GetSysParams()
# Verify that the parameters have changed
print("Frequency [MHz]: ", main.sysParams.minFreq)
print("Bandwidth [MHz]: ", main.sysParams.manualBW)
print("Ramp-time [ms]: ", main.sysParams.t_ramp)
print("Number Points: ", main.sysParams.freq_points)      
print("Bin Size (Resolution) [m]: ", main.sysParams.tic / 1000000)
print("")


'--------------------------------------------------------------------------------------------'
'''
Get the Time domain data
'''
measurement_duration = 25  # Duration to collect data in seconds
# Initialize dictionaries to store data for each range bin
channels_fd_I1 = {}
channels_fd_Q1 = {}
channels_fd_I2 = {}
channels_fd_Q2 = {}
timestamps = []

n_samples = 1024  # Number of samples per channel

# Initialize range bins starting from the first index (1) rather than 0
range_bins = [main.sysParams.tic*n/main.sysParams.zero_pad/1.0e6 for n in range(main.sysParams.freq_points)]

# Initialize dictionaries with range bins as keys
for rb in range_bins:
    channels_fd_I1[rb] = []
    channels_fd_Q1[rb] = []
    channels_fd_I2[rb] = []
    channels_fd_Q2[rb] = []
    
print("Starting to collect data.")

if main.connected:
    # Specify a measurement type, let the Radar perform it and read the data
    measurement = "UP-Ramp"
    start_time = time.time()

    while time.time() - start_time < measurement_duration:
        main.GetFdData(measurement)
        timestamps.append(time.time() - start_time)
        
        # Process the FD data based on the data type
        if main.sysParams.FFT_data_type == 0:  # only magnitudes were transmitted
            mag_data = main.FD_Data.data
        elif main.sysParams.FFT_data_type == 2:  # real/imaginary 
            comp_data = [complex(float(main.FD_Data.data[n]), float(main.FD_Data.data[n + 1])) for n in range(0, len(main.FD_Data.data), 2)]
            mag_data = np.abs(comp_data)
        elif main.sysParams.FFT_data_type in [1, 3]:  # magnitudes/phase or magnitudes/object angle
            mag_data = [main.FD_Data.data[n] for n in range(0, len(main.FD_Data.data), 2)]
        
        # Convert to dBm
        min_dbm = -60  # [dBm]
        for n in range(len(mag_data)):
            try:
                mag_data[n] = 20 * np.log10(mag_data[n] / 2.**21)
            except:
                mag_data[n] = min_dbm
        
        # Sort for active channels
        fd_data = []
        n = 0
        for ch in range(4):  # maximum possible channels = 4
            if main.sysParams.active_RX_ch & (1 << ch):
                ind1 = n * main.FD_Data.nSamples
                ind2 = ind1 + main.FD_Data.nSamples
                n += 1
                fd_data.append(mag_data[ind1:ind2])
            else:
                fd_data.append([0] * main.FD_Data.nSamples)
        
        # Store data by range bins in the corresponding channel dictionary
        for i, rb in enumerate(range_bins):
            channels_fd_I1[rb].append(fd_data[0][i])
            channels_fd_Q1[rb].append(fd_data[1][i])
            channels_fd_I2[rb].append(fd_data[2][i])
            channels_fd_Q2[rb].append(fd_data[3][i])

        # time.sleep(1)  # Adjust the sleep time as necessary
    
# Function to plot FD data for each range bin between specified minimum and maximum bins
def plot_fd_range_bins_in_grid(min_bin, max_bin):
    selected_bins = [rb for rb in range_bins if min_bin <= rb <= max_bin]
    num_bins = min(20, len(selected_bins))  # Ensure we only plot up to 20 bins
    
    fig, axs = plt.subplots(5, 4, figsize=(28, 20))  # 4 rows by 5 columns
    
    # Flatten axs array for easy iteration
    axs = axs.flatten()
    
    for i, rb in enumerate(selected_bins[:20]):
        previous_bin = selected_bins[i-1] if i > 0 else None
        if previous_bin:
            title = f"FD for Range {previous_bin:.2f}m - {rb:.2f}m"
        else:
            title = f"FD for Range Bin {rb:.2f} meters"
        
        if channels_fd_I1[rb]:
            axs[i].plot(timestamps, channels_fd_I1[rb], label="I1")
        if channels_fd_Q1[rb]:
            axs[i].plot(timestamps, channels_fd_Q1[rb], label="Q1")
        if channels_fd_I2[rb]:
            axs[i].plot(timestamps, channels_fd_I2[rb], label="I2")
        if channels_fd_Q2[rb]:
            axs[i].plot(timestamps, channels_fd_Q2[rb], label="Q2")
        axs[i].set_title(title)
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Magnitude [dBm]")
        axs[i].legend()
        axs[i].grid(True)
    
    # Hide any unused subplots
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])
    
    plt.tight_layout()
    plt.show()

# Specify the range of bins to plot
min_bin = 0.23 # Example minimum range bin value in meters
max_bin = 4.5 # Example maximum range bin value in meters
plot_fd_range_bins_in_grid(min_bin, max_bin)

print("done")





























    