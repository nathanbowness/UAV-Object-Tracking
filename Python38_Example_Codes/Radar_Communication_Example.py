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
        
        print('========================')
        print('GetFdData')
        
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
    # function to get time domain data with or without a previous measurement
    # the parameter 'measurement' specifies the type of measurement    
    # possible values are: "UP-Ramp", "DOWN-Ramp", "CW" or "None"
    def GetTdData(self, measurement="UP-Ramp"):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('GetTdData')

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
    # function to get the Human Tracker parameters
    def GetHtParams(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('GetHtParams')

        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_SEND_HT_PARAMS")
        except:
            print("Error in receiving Human Tracker parameters.")
            self.error = True
            return
        
        # the received parameters can be found in htParams
        
    '--------------------------------------------------------------------------------------------'
    # function to set the Human Tracker parameters
    # Note that the Radar Module will perform some initial measurements, so it will be waited some time
    def SetHtParams(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('SetHtParams')

        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_HT_PARAMS")            
        except:
            print("Error in setting Human Tracker parameters.")
            self.error = True
            return
    
    '--------------------------------------------------------------------------------------------'
    # function that triggers a Human Tracker measurement
    def HtMeasurement(self):
        # do nothing if not connected or an error has occurred
        if not self.connected or self.error:
            return
        
        print('========================')
        print('HtMeasurement')

        # execute the respective command ID
        try:
            self.cmd.execute_cmd("CMDID_DO_HT")            
        except:
            print("Error in receiving Human Tracker data.")
            self.error = True
            return
        
        # the received data can be found in HT_Targets
    
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

# Read the actual system parameters of the Radar Module
main.GetSysParams()
# Print an example
print("Frequency [MHz]: ", main.sysParams.minFreq)
print("Bandwidth [MHz]: ", main.sysParams.manualBW)
print("Ramp-time [ms]: ", main.sysParams.t_ramp)
print("")

# Change some of the system parameters, e.g.
main.sysParams.minFreq = 24000
main.sysParams.manualBW = 250
main.sysParams.t_ramp = 1
main.sysParams.active_RX_ch = 15
main.sysParams.freq_points = 20


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
print("")


'--------------------------------------------------------------------------------------------'
'''
Frequency domain example
'''
if 0:
    if main.connected:
        # Specify a measurement type, let the Radar perform it and read the data
        measurement = "UP-Ramp"
        main.GetFdData(measurement)
        
        # Plot the measured data dependent on the activated channels
        # Only magnitude data will be plotted
        mag_data = []
        
        if main.sysParams.FFT_data_type == 0:   # only magnitudes were transmitted
            mag_data = main.FD_Data.data
            
        if main.sysParams.FFT_data_type == 2:   # real/imaginary 
            comp_data = [complex(float(main.FD_Data.data[n]), float(main.FD_Data.data[n+1])) for n in range(0, len(main.FD_Data.data), 2)]
            mag_data = np.abs(comp_data)
        
        if main.sysParams.FFT_data_type == 1 or main.sysParams.FFT_data_type == 3:      # magnitudes/phase or magnitudes/object angle
            mag_data = [main.FD_Data.data[n] for n in range(0, len(main.FD_Data.data), 2)]
            
        # Convert to dBm
        min_dbm = -60   # [dBm]
        for n in range(len(mag_data)):
            try:
                mag_data[n] = 20*np.log10(mag_data[n]/2.**21)
            except:
                mag_data[n] = min_dbm
    
        # Sort for active channels
        fd_data = []
        n = 0
        for ch in range(4):     # maximum possible channels = 4
            if main.sysParams.active_RX_ch & (1<<ch):
                ind1 = n * main.FD_Data.nSamples
                ind2 = ind1 + main.FD_Data.nSamples
                n += 1
                fd_data.append(mag_data[ind1:ind2])
            else:
                fd_data.append([0]*main.FD_Data.nSamples)   
                
        # Generate x-axis data, here the distance in [m] 
        x_data = [main.sysParams.tic*n/main.sysParams.zero_pad/1.0e6 for n in range(main.FD_Data.nSamples)]
        
        # Add the data as lines to the plot
        plt.plot(x_data, fd_data[0], 'b',  
                 x_data, fd_data[1], 'g',
                 x_data, fd_data[2], 'c',
                 x_data, fd_data[3], 'm')
        
        plt.grid(True)
        plt.title("Frequency domain data plot")
        plt.xlabel("Distance [m]")
        plt.ylabel("Magnitude [dBm]")
        
        # Show the plot
        plt.show()
        
'--------------------------------------------------------------------------------------------'
'''
Time domain example
'''
if 0:
    if main.connected:
        # Specify a measurement type, let the Radar perform it and read the data
        measurement = "UP-Ramp"
        main.GetTdData(measurement)
        
        # Plot the measured data dependent on the activated channels
        td_data = []
        n = 0
        n_samples = 1024         # always 1024 samples per channel
        for ch in range(4):      # maximum possible channels = 4
            if main.sysParams.active_RX_ch & (1<<ch):
                ind1 = n*n_samples
                ind2 = ind1 + n_samples
                n += 1
                td_data.append(main.TD_Data.data[ind1:ind2])
            else:
                td_data.append([0]*n_samples)
                
        # Generate x-axis data, here the measurement time in [ms]
        step = float(main.sysParams.t_ramp)/n_samples
        x_data = [n*step for n in range(n_samples)]
        
        # Add the data as lines to the plot
        plt.plot(x_data, td_data[0], 'b',  
                 x_data, td_data[1], 'g',
                 x_data, td_data[2], 'c',
                 x_data, td_data[3], 'm')
        
        plt.grid(True)
        plt.title("Time domain data plot")
        plt.xlabel("Time [m]")
        plt.ylabel("Signal Amplitude")
        
        # Show the plot
        plt.show()
        
def deduplicate_data(target_data, eps_distance=0.1, eps_angle=1, min_samples=2):
    processed_data = {}

    for target_id, coords in target_data.items():
        # Prepare data for clustering
        X = np.array(list(zip(coords['distances'], coords['angles'])))

        # Apply DBSCAN
        db = DBSCAN(eps=max(eps_distance, eps_angle), min_samples=min_samples).fit(X)
        labels = db.labels_

        # Find indices of core samples
        unique_labels = set(labels)
        clusters = {label: [] for label in unique_labels if label != -1}  # exclude noise points

        # Aggregate data points by cluster
        for label, point in zip(labels, X):
            if label != -1:  # ignore noise
                clusters[label].append(point)

        # Compute centroids of clusters
        centroid_distances = []
        centroid_angles = []
        times = []  # Assuming each cluster's time is the average of times of its points
        for label, points in clusters.items():
            points = np.array(points)
            centroid_distances.append(np.mean(points[:, 0]))
            centroid_angles.append(np.mean(points[:, 1]))
            # Extract times for these points (average or middle)
            time_indices = [i for i, l in enumerate(labels) if l == label]
            times.append(np.mean([coords['times'][i] for i in time_indices]))

        processed_data[target_id] = {'times': times, 'distances': centroid_distances, 'angles': centroid_angles}

    return processed_data

def simple_deduplicate(target_data, dist_threshold=0.1, angle_threshold=1):
    processed_data = {}

    for target_id, coords in target_data.items():
        # Initialize lists for storing processed data
        processed_times = []
        processed_distances = []
        processed_angles = []

        # Iterate over all data points for this target
        for time, dist, angle in zip(coords['times'], coords['distances'], coords['angles']):
            # Check if the current point is close to any of the already processed points
            is_duplicate = False
            for p_dist, p_angle in zip(processed_distances, processed_angles):
                if abs(dist - p_dist) <= dist_threshold and abs(angle - p_angle) <= angle_threshold:
                    is_duplicate = True
                    break

            # If no close point was found, add the current point to the processed lists
            if not is_duplicate:
                processed_times.append(time)
                processed_distances.append(dist)
                processed_angles.append(angle)

        # Store processed data for the current target
        processed_data[target_id] = {
            'times': processed_times,
            'distances': processed_distances,
            'angles': processed_angles
        }

    return processed_data
        
'--------------------------------------------------------------------------------------------'
'''
Human Tracker example
'''
# Initialize data storage
target_data = {}
if 1:
    # Get the actual Human Tracker parameters
    main.GetHtParams()
    
    # Change some of the Human Tracker parameters
    main.htParams.minDistance = 0
    main.htParams.nRefPulses = 100
    # main.htParams.maxLostDetect = 10
    main.htParams.overThreshold = 30
    # ...
    
    # Send the changed parameters to the Radar Module
    print("Radar Module is performing %d initial measurements."%(main.htParams.nRefPulses)) 
    print("Please wait for %.2f seconds.\n"%(main.htParams.timeInterval*main.htParams.nRefPulses/1000.))
    main.SetHtParams()
    
    time_interval = 50     # [ms]
    n_measurements = 500    # Number of measurements
    start_time = time()     # Record the overall start time
    
    # Perform a number of measurements specified by n_measurements e.g. in a specified time interval 
    for n in range(n_measurements):
        t_start = time()
        
        main.HtMeasurement()
                
        dt = time() - t_start
        
        # Measurement was faster than the specified time interval? -> wait to fulfill it
        if dt < time_interval:
            sleep((time_interval - dt)/1000.)
            
        measurement_time = time() - start_time    # Time since start in seconds
        
        # Print some of the measured results
        print("Finished Human Tracker measurement No.: %d"%(n+1))
        print("Number of targets found: %d"%(main.HT_Targets.nTargets))
        for m in range(main.HT_Targets.nTargets):
            # Collect data for processing
            target_id = main.HT_Targets.id[m]
            if target_id not in target_data:
                target_data[target_id] = {'times': [], 'distances': [], 'angles': []}
            target_data[target_id]['times'].append(measurement_time)
            target_data[target_id]['distances'].append(main.HT_Targets.dist[m])
            target_data[target_id]['angles'].append(main.HT_Targets.angle[m])
            
            print("-------------------")
            print("Target No.: %d"%(main.HT_Targets.id[m]))
            print("Distance: %.3f m"%(main.HT_Targets.dist[m]))
            print("Angle: %.2f deg"%(main.HT_Targets.angle[m]))
            print("Level: %.2f dBm"%(20*np.log10(main.HT_Targets.level[m]/2.**21)))
            print("Tracked: %d"%(main.HT_Targets.tracked[m]))
            print("Count: %d"%(main.HT_Targets.count[m]))
        print("==========================================")
    
    # Process the data using the clustering-based deduplication method
    processed_target_data = simple_deduplicate(target_data)
    
    # Plot Distance vs. Time and Angle vs. Time
    plt.figure(figsize=(12, 10))

    # Distance vs. Time
    plt.subplot(2, 1, 1)  # 2 rows, 1 column, first plot
    for target_id, coords in processed_target_data.items():
        plt.plot(coords['times'], coords['distances'], marker='o', linestyle='-', label=f'Target {target_id}')
    plt.title('Distance vs. Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Distance (m)')
    plt.grid(True)
    plt.legend()

    # Angle vs. Time
    plt.subplot(2, 1, 2)  # 2 rows, 1 column, second plot
    for target_id, coords in processed_target_data.items():
        plt.plot(coords['times'], coords['angles'], marker='o', linestyle='-', label=f'Target {target_id}')
    plt.title('Angle vs. Time')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Angle (degrees)')
    plt.grid(True)
    plt.legend()

    plt.tight_layout()  # Adjust layout to prevent overlap
    plt.show()

# At the end disconnect the interface
main.Disconnect()
print("Disconnected.")
print("End.")
# End

