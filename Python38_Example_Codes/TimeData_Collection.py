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
    # function to get time domain data with or without a previous measurement
    # the parameter 'measurement' specifies the type of measurement    
    # possible values are: "UP-Ramp", "DOWN-Ramp", "CW" or "None"
    def GetTdData(self, measurement="UP-Ramp"):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        # print('========================')
        # print('GetTdData')

        # execute the respective command ID
        try:
            if measurement == "UP-Ramp":
                self.cmd.execute_cmd("CMDID_UP_RMP_TD")                
            elif measurement == "DOWN-Ramp":
                self.cmd.execute_cmd("CMDID_DN_RMP_TD")
            elif measurement == "CW":
                self.cmd.execute_cmd("CMDID_GP_TD")
            elif measurement == None or measurement == "None":
                self.cmd.execute_cmd("CMDID_TDATA")
            else:
                print("No valid measurement type.")
                self.error = True
                return
            
        except:
            print("Error in receiving time domain data.")
            self.error = True
            return
        
        # the received data can be found in TD_Data
    
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
# main.sysParams.tic = 250000 # 0.2499 m # Auto calcualted based off the manualBW frequncy

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
print("Bin Size (Resolution) [m]: ", main.sysParams.tic / 1000000) 
print("")


'--------------------------------------------------------------------------------------------'
'''
Get the Time domain data
'''
measurement_duration = 25  # Duration to collect data in seconds
n_samples = 1024 # always 1024 samples per channel
range_bins = [main.sysParams.tic*(n+1)/main.sysParams.zero_pad/1.0e6 for n in range(n_samples)] # x_data in Meters

channels_1 = {}
channels_2 = {}
channels_3 = {}
channels_4 = {}
timestamps = []

# Initialize dictionaries with range bins as keys
for rb in range_bins:
    channels_1[rb] = []
    channels_2[rb] = []
    channels_3[rb] = []
    channels_4[rb] = []

print("Starting to collect data.")

if main.connected:
    # Specify a measurement type, let the Radar perform it and read the data
    measurement = "UP-Ramp"
    
    start_time = time.time()

    while time.time() - start_time < measurement_duration:
        main.GetTdData(measurement)
        timestamps.append(time.time() - start_time)

        for ch in range(4):  # Iterate over the 4 channels
            ind1 = ch * n_samples
            ind2 = ind1 + n_samples
            td_data = main.TD_Data.data[ind1:ind2]

            # Store data by range bins in the corresponding channel dictionary
            if ch == 0:
                for i, rb in enumerate(range_bins):
                    channels_1[rb].append(td_data[i])
            elif ch == 1:
                for i, rb in enumerate(range_bins):
                    channels_2[rb].append(td_data[i])
            elif ch == 2:
                for i, rb in enumerate(range_bins):
                    channels_3[rb].append(td_data[i])
            elif ch == 3:
                for i, rb in enumerate(range_bins):
                    channels_4[rb].append(td_data[i])

        # time.sleep(1)  # Adjust the sleep time as necessary
            
# Function to plot TD data for each range bin between specified minimum and maximum bins
def plot_td_range_bins(min_bin, max_bin):
    selected_bins = [rb for rb in range_bins if min_bin <= rb <= max_bin]
    num_bins = min(20, len(selected_bins))  # Ensure we only plot up to 20 bins
    
    fig, axs = plt.subplots(4, 5, figsize=(24, 20))  # 4 rows by 5 columns
    
    # Flatten axs array for easy iteration
    axs = axs.flatten()
    
    for i, rb in enumerate(selected_bins[:20]):
        if channels_1[rb]:
            axs[i].plot(timestamps, channels_1[rb], label="Channel 1")
        if channels_2[rb]:
            axs[i].plot(timestamps, channels_2[rb], label="Channel 2")
        if channels_3[rb]:
            axs[i].plot(timestamps, channels_3[rb], label="Channel 3")
        if channels_4[rb]:
            axs[i].plot(timestamps, channels_4[rb], label="Channel 4")
        axs[i].set_title(f"Time-Domain Data for Range Bin {rb:.2f} meters")
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Amplitude")
        axs[i].legend()
        axs[i].grid(True)
    
    # Hide any unused subplots
    for j in range(i + 1, len(axs)):
        fig.delaxes(axs[j])
    
    plt.tight_layout()
    plt.show()

# Specify the range of bins to plot
min_bin = 0.25  # Example minimum range bin value in meters
max_bin = 4.5  # Example maximum range bin value in meters
plot_td_range_bins(min_bin, max_bin)

print("done")





























# Function to plot data for range bins up to a specified maximum bin
# def plot_range_bin_data_below_max(max_bin):
#     plt.figure(figsize=(12, 8))
#     for rb in range_bins:
#         if rb <= max_bin:
#             if channels_1[rb]:
#                 plt.plot(timestamps, channels_1[rb], label=f"Channel 1 - Range Bin {rb:.2f}")
#             if channels_2[rb]:
#                 plt.plot(timestamps, channels_2[rb], label=f"Channel 2 - Range Bin {rb:.2f}")
#             if channels_3[rb]:
#                 plt.plot(timestamps, channels_3[rb], label=f"Channel 3 - Range Bin {rb:.2f}")
#             if channels_4[rb]:
#                 plt.plot(timestamps, channels_4[rb], label=f"Channel 4 - Range Bin {rb:.2f}")
#     plt.title(f"Time-Domain Data for Range Bins up to {max_bin} meters")
#     plt.xlabel("Range Bins (m)")
#     plt.ylabel("Amplitude")
#     plt.legend()
#     plt.show()
    