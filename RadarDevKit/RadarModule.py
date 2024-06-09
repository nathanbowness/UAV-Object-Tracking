# Main classes for the Ethernet interface
from RadarDevKit.Interfaces.Ethernet.EthernetConfig import EthernetParams
from RadarDevKit.Interfaces.Ethernet.IPConnection import IPConnection
from RadarDevKit.Interfaces.Ethernet.Commands import IPCommands

from RadarDevKit.ConfigClasses import SysParams

# Parameter and data classes
import RadarDevKit.ConfigClasses as cfgCl

'''
This example class has functions
to connect a Radar Module via an interface specified by the user. It has also
functions to use the basic functions of the Radar Module.  
'''
class RadarModule():
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
Get a configured RadarModule, with functions to retreive data
newSysParms: update system params to be used with the radar to get data
printSettings: if true, will print the updated settings the user has set to the console, otherwise it will not print anything
'''        
def GetRadarModule(updatedSysParams: SysParams = None, 
                   updatedEthernetConfig: EthernetParams = None, 
                   printSettings: bool = True):
                    
    # Get an instance of the main class
    radarModule = RadarModule()
    
    # Update ethernet config if give, otherwise use defaults
    if updatedEthernetConfig is not None:
        radarModule.etherParams = updatedEthernetConfig

    # Specify your interface and try to connect it.
    radarModule.Connect()

    # Read some Radar Module specific parameters
    radarModule.GetHwParams()

    if printSettings:
        # These parameters can be accessed by e.g. main.hwParams.radarNumber
        print("Number of the connected Radar Module: ", radarModule.hwParams.radarNumber)

    # Read the actual system parameters of the Radar Module
    radarModule.GetSysParams()
    
    # Print the original params - for now not required
    # if printSettings:
    #     print("Frequency [MHz]: ", radarModule.sysParams.minFreq)
    #     print("Bandwidth [MHz]: ", radarModule.sysParams.manualBW)
    #     print("Ramp-time [ms]: ", radarModule.sysParams.t_ramp)
    #     print("")
    
    # Change system params if specified, otherwise use defaults
    if updatedSysParams is not None:
        radarModule.sysParams = updatedSysParams
    
    # Check if the frontend is off
    if radarModule.sysParams.frontendEn == 0:
        radarModule.sysParams.frontendEn = 1   # turns it on

    # Send the changed parameters to the Radar Module
    radarModule.SetSysParams()

    # Always read back the system parameters because some read only parameters changed
    radarModule.GetSysParams()
    if printSettings:
        # Verify that the parameters have changed
        print("Frequency [MHz]: ", radarModule.sysParams.minFreq)
        print("Bandwidth [MHz]: ", radarModule.sysParams.manualBW)
        print("Ramp-time [ms]: ", radarModule.sysParams.t_ramp)        
        print("")
        
    print("Connected to the radar.")
    return radarModule