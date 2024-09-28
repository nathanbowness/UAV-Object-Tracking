'''
Created on 22.09.2015

@author: IMST GmbH
'''

'''=============================================================================
@brief:        Class for the radar System Parameters
============================================================================='''
class SysParams():
    def __init__(self):
        self.band =             0x7     # parameter to select the bandwidth (0 - 13), e.g. 0 = 50 MHz, 3 = 250 MHz, ...
        self.t_ramp =           0x4     # ramp time of FMCW chirp
        self.zero_pad =         0x1     # zero-pad factor for smoothing the fft-graph (1, 2, 4, 8)
        self.FFT_data_type =    0x0     # output data type of the fft: 0 -> only magnitudes, 1 -> mag + phase angle, 2 -> real + imag, 3 -> mag + object angle 
        self.frontendEn =       0x1     # enable (1) or disable (0) the frontend power 
        self.powerSaveEn =      0x1     # enable (1) or disable (0) the power switching
        self.norm =             0x0     # distance compensation ON (1) or OFF (0)
        self.active_RX_ch =     0xF     # active Rx channels: e.g. 0000 0000 0000 1011 means Rx1, Rx2 and Rx4 are enabled
        self.advanced =         0x0     # enables/disables the advanced mode, typical not available and also no command ids are available          
        self.freq_points =      0       # only received, number of fft bins (1-512)
        self.tic =              0       # only received, distance bin size [um]
        self.doppler =          0       # only received, doppler bin size [um/s]
        self.freq_bin =         0       # only received, frequency bin [Hz]
        self.minFreq =          24000   # [MHz]
        self.manualBW =         250     # [MHz]        
        self.atten =            7       # Tx attenuation of the radar chip (7 = 9dB)

'''=============================================================================
@brief:        Class for the radar Hardware Parameters
============================================================================='''          
class HwParams(object):
    def __init__(self):        
        self.flashDate =        0      # default
        self.fwVersion =        0
        self.fwRevision =       0
        self.usedHardware =     0
        self.availChannels =    0
        self.availAlgos =       0
        self.radarNumber =      0
        self.sntID =            0
        self.basebandID =       0
        self.frontendID =       0
        self.phaseOffset =      0
        self.microDoppler =     0
        
'''=============================================================================
@brief:        Class for the Human Tracker Parameters
============================================================================='''
class HtParams():
    def __init__(self):
        self.nRefPulses =       50      # number of initial FMCW measurements to calculate a background model
        self.timeInterval =     50      # time interval [ms] between two measurements
        self.nTargets =         5       # maximum number of targets to be detected/tracked (1-10)
        self.backgrFilter =     32      # filter length to estimate the scene background
        self.threshFilter =     100     # filter length to adapt the detection threshold (1-100)
        self.overThreshold =    30      # factor that defines how much a target amplitude has to be greater than the background (1-1000)
        self.minDistance =      0       # minimum target distance in meters        
        self.minSeparation =    5       # minimal distance between to targets in Bins        
        self.enableTracker =    0       # enables (1) or disables (0) the internal tracking algorithm        
        self.maxRangeShift =    5       # maximum assumed target displacement between two measurements        
        self.maxLostDetect =    3       # maximum number of attempts to find a lost targets 
                
'''=============================================================================
                        Several data transport classes
============================================================================='''
class TD_Data():
    def __init__(self):
        self.nValues        = None
        self.time0          = None
        self.time1          = None
        self.data           = []
        
class FD_Data():
    def __init__(self):
        self.datType            = None
        self.time0              = None
        self.time1              = None
        self.time2              = None
        self.overload           = None
        self.maxRxChannels      = 4
        self.nSamples           = None
        self.maxValues          = []
        self.minValues          = []
        self.data               = []
        
    def clear(self):
        self.datType            = None
        self.maxValues          = []
        self.minValues          = []
        self.data               = []
        
        
class HtTargets():
    def __init__(self):
        self.status     = None
        self.nTargets   = None
        self.tPreMeas   = None
        self.tPostMeas  = None
        self.tPreProc   = None
        self.tPostProc  = None
        self.id =       []        
        self.tracked =  []
        self.count =    []
        self.level =    []
        self.dist =     []
        self.angle =    []
        
    def clear(self):
        self.id =       []
        self.tracked =  []
        self.count =    []
        self.level =    []
        self.dist =     []
        self.angle =    []          


