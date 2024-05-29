# -*- coding: cp1252 -*-
'''

Interface-independent base class for commands

Created on 18.01.2016

@author: hubert kronenberg
'''
import time
import numpy as np
from Interfaces import ConversionFuncs as conv
from time import time as currenttime


'''===============================================================================
=Constants
==============================================================================='''

# requested type of FD data
DT_MAGN = 0
DT_MAGN_PHASE = 1
DT_REAL_IMAG = 2
DT_MAGN_ANGLE = 3

MAX_CHANNELS = 4
TD_SAMPLES = 1024
FD_SAMPLES = 513

'''=============================================================================
@brief:         Class with command list for every supported command of the radar
                module.
@note:          Functions can be entered by an execute function. The command names
                are the same as in the firmware.
============================================================================='''
class Commands(object):

    '''====================================================================
        @brief: Constructor for Command Base Class
                
        @param single_transfer:
                    True:   The entire command has to be transferred in
                            one packet
                    False:  The command transfer can be split into several
                            packets
    ===================================================================='''  
    def __init__(self, single_transfer):
        self.single_transfer = single_transfer
        self.delay_set_sys_params = 0
        # dictionary with command IDs, command codes and command functions
        self.cmd_list = {}
        # System Commands
        self.cmd_list["CMDID_PING"]                  = (0x0000, self.cmd_ping)
        self.cmd_list["CMDID_GETTIME"]               = (0x0001, self.cmd_getTime)
        self.cmd_list["CMDID_SETTIME"]               = (0x0002, self.cmd_setTime)
        self.cmd_list["CMDID_SEND_INFO"]             = (0x0012, self.cmd_get_sys_info)
        self.cmd_list["CMDID_SELF_TEST"]             = (0x0013, self.cmd_do_cbit)
        self.cmd_list["CMDID_RST_PARAMS"]            = (0x0027, self.cmd_rst_sys_params)
        self.cmd_list["CMDID_SETUP"]                 = (0x0028, self.cmd_set_sys_params)
        self.cmd_list["CMDID_SEND_PARAMS"]           = (0x0029, self.cmd_get_sys_params)
        self.cmd_list["CMDID_SEND_SENSORDATA"]       = (0x002B, self.cmd_get_temp_power)
        self.cmd_list["CMDID_GET_IFC_PARAMS"]        = (0x0030, self.cmd_get_ifc_params)
        self.cmd_list["CMDID_SET_IFC_PARAMS"]        = (0x0031, self.cmd_set_ifc_params)
        self.cmd_list["CMDID_ACTIVATE_IFC_PARAMS"]   = (0x0032, self.cmd_activate_ifc_params)
        self.cmd_list["CMDID_RESTART_CPU"]           = (0x002C, self.cmd_restart_system)        
        # Raw Data Commands
        self.cmd_list["CMDID_UP_RMP"]                = (0x0040, self.cmd_up_ramp)
        self.cmd_list["CMDID_DN_RMP"]                = (0x0041, self.cmd_down_ramp)
        self.cmd_list["CMDID_GAP"]                   = (0x0042, self.cmd_gap)
        self.cmd_list["CMDID_TDATA"]                 = (0x0043, self.cmd_get_td_data)
        self.cmd_list["CMDID_FDATA"]                 = (0x0044, self.cmd_get_fd_data)
        self.cmd_list["CMDID_UP_RMP_TD"]             = (0x0045, self.cmd_get_td_data) # cmd_up_ramp_td
        self.cmd_list["CMDID_UP_RMP_FD"]             = (0x0046, self.cmd_get_fd_data) # cmd_up_ramp_fd
        self.cmd_list["CMDID_DN_RMP_TD"]             = (0x0047, self.cmd_get_td_data) # cmd_down_ramp_td
        self.cmd_list["CMDID_DN_RMP_FD"]             = (0x0048, self.cmd_get_fd_data) # cmd_down_ramp_fd
        self.cmd_list["CMDID_GP_TD"]                 = (0x0049, self.cmd_get_td_data) # cmd_gap_td
        self.cmd_list["CMDID_GP_FD"]                 = (0x004A, self.cmd_get_fd_data) # cmd_gap_fd
        # Human Tracker Commands
        self.cmd_list["CMDID_HT_PARAMS"]             = (0x0060, self.cmd_set_ht_params)
        self.cmd_list["CMDID_SEND_REF_DATA"]         = (0x0062, self.cmd_get_ht_threshold)
        self.cmd_list["CMDID_DO_HT"]                 = (0x0063, self.cmd_do_ht_meas)
        self.cmd_list["CMDID_SEND_HT_PARAMS"]        = (0x0065, self.cmd_get_ht_params)

    '''==========================================================================''' 
    def getSupportedCmds(self):
        #print "\nList of all commands which are supported by this Radar-Module:"
        for cmd_id in self.cmd_list:
            if self.cmd_list[cmd_id][1]:
                print(cmd_id)

    '''==========================================================================''' 
    # Function to execute the commands of cmd_list with optional input parameters
    # and optional output parameters
    def execute_cmd(self, cmdID, *opt):

        if not cmdID in self.cmd_list:
            raise CommandError(("Invalid Command ID: %s")%cmdID)

        cmd_params = self.cmd_list[cmdID]       # Get the right command if supported
        cmd_code = cmd_params[0]                # Get command code which starts the function in the radar module
        cmd_func = cmd_params[1]                # Get the function which starts processing

        # preprocessing
        self.doTransfer_start(cmd_code)

        # invoke command function
        return_val = cmd_func(*opt)
        
        # postprocessing
        self.doTransfer_end(cmd_code)

        # Return result if any
        return return_val

    '''=============================================================================
    @brief:         Transfer Preprocessing
    ============================================================================='''
    def doTransfer_start(self, cmd_code):
        pass

    '''=============================================================================
    @brief:         Transfer Postprocessing
    ============================================================================='''
    def doTransfer_end(self, cmd_code):
        pass

    '''=============================================================================
    @brief:         Receive Preprocessing
    ============================================================================='''
    def doTransfer_rxstart(self):
        pass

    '''==========================================================================''' 
    def cmd_dummy(self):
        # do nothing
        pass

    '''=============================================================================
                                    System Functions
    ============================================================================='''
    def cmd_ping(self):

        return True

    '''=========================================================================='''
    def cmd_getTime(self):

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = [2, 2, 2, 2])

        # convert time to Unix timestamp
        return conv.TimeStamp_NetToHost(RecpL)

    '''=========================================================================='''
    def cmd_setTime(self):

        # get current time as Unix timestamp and convert
        # it into a payload of appropriate format
        secs = currenttime()

        self.doTransfer(SndLenE = [2, 2, 2, 2], SndpL = conv.TimeStamp_HostToNet(secs))

        return secs

    '''=========================================================================='''
    def cmd_get_sys_info(self):

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = [4, 4, 4, 4, 4, 2, 2, 2, 4, 4, -4])

        self.hwParams.fwVersion     = RecpL.pop(0)
        self.hwParams.fwRevision    = RecpL.pop(0)
        self.hwParams.sntID         = RecpL.pop(0)
        self.hwParams.basebandID    = RecpL.pop(0)
        self.hwParams.frontendID    = RecpL.pop(0)
        self.hwParams.availChannels = RecpL.pop(0)
        self.hwParams.availAlgos    = RecpL.pop(0)
        self.hwParams.usedHardware  = RecpL.pop(0)
        self.hwParams.radarNumber   = RecpL.pop(0)
        self.hwParams.flashDate     = RecpL.pop(0)
        self.hwParams.phaseOffset   = RecpL.pop(0)

    '''=========================================================================='''
    def cmd_rst_sys_params(self):

        self.doTransfer()

    '''=========================================================================='''
    def cmd_set_sys_params(self):

        SndLenE = 7*[1] + [2, 1, 2, 2, 2, 1]

        SndpL = []
        SndpL.append(self.sysParams.band)
        SndpL.append(self.sysParams.t_ramp)
        SndpL.append(self.sysParams.zero_pad)
        SndpL.append(self.sysParams.FFT_data_type)
        SndpL.append(self.sysParams.frontendEn)
        SndpL.append(self.sysParams.powerSaveEn)
        SndpL.append(self.sysParams.norm)
        SndpL.append(self.sysParams.active_RX_ch)
        SndpL.append(self.sysParams.advanced)
        SndpL.append(self.sysParams.freq_points)
        SndpL.append(self.sysParams.minFreq)
        SndpL.append(self.sysParams.manualBW)
        SndpL.append(self.sysParams.atten)

        self.doTransfer(SndLenE = SndLenE, SndpL = SndpL, delay = self.delay_set_sys_params)

    '''=========================================================================='''
    def cmd_get_sys_params(self):

        RecLenE_fix = 7*[1] + [2, 1, 2, 2, 2, 1]
        RecLenE_fix += [4, 4, 4]

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix)

        self.sysParams.band          = RecpL.pop(0)
        self.sysParams.t_ramp        = RecpL.pop(0)
        self.sysParams.zero_pad      = RecpL.pop(0)
        self.sysParams.FFT_data_type = RecpL.pop(0)
        self.sysParams.frontendEn    = RecpL.pop(0)
        self.sysParams.powerSaveEn   = RecpL.pop(0)
        self.sysParams.norm          = RecpL.pop(0)
        self.sysParams.active_RX_ch  = RecpL.pop(0)
        self.sysParams.advanced      = RecpL.pop(0)
        self.sysParams.freq_points   = RecpL.pop(0)
        self.sysParams.minFreq       = RecpL.pop(0)
        self.sysParams.manualBW      = RecpL.pop(0)
        self.sysParams.atten         = RecpL.pop(0)
        
        self.sysParams.tic           = RecpL.pop(0)
        self.sysParams.doppler       = RecpL.pop(0)
        self.sysParams.freq_bin      = RecpL.pop(0)

        self.sysParams.max_dist = int(round((self.sysParams.tic*1e-6 * (self.sysParams.freq_points-1))/self.sysParams.zero_pad))
        self.sysParams.max_speed = int(round(self.sysParams.doppler*1.e-6 * (self.sysParams.freq_points-1)/self.sysParams.zero_pad))        

    '''=========================================================================='''
    def cmd_do_cbit(self):

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = [4])
        error_code = RecpL[0]
        return error_code

    '''=========================================================================='''
    def cmd_get_temp_power(self):
        
        RecLenE_fix = [-4, 4, -4]

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix)

        temp = RecpL[0]
        power = float(RecpL[1])/10
        temp2 = RecpL[2]
        
        return temp, power, temp2

    '''=============================================================================
                                    Raw Data Functions
    ============================================================================='''
    def cmd_up_ramp_td(self):
        self.cmd_up_ramp()
        self.cmd_get_td_data()
        
    '''=========================================================================='''
    def cmd_up_ramp_fd(self):
        self.cmd_up_ramp()
        self.cmd_get_fd_data()
    
    '''=========================================================================='''
    def cmd_down_ramp_td(self):
        self.cmd_down_ramp()
        self.cmd_get_td_data()

    '''=========================================================================='''
    def cmd_down_ramp_fd(self):
        self.cmd_down_ramp()
        self.cmd_get_fd_data()

    '''=========================================================================='''
    def cmd_gap_td(self):
        time.sleep(self.sysParams.t_ramp/1000)     # measurement time in [s]
        self.cmd_get_td_data()
    
    '''=========================================================================='''
    def cmd_gap_fd(self):
        time.sleep(self.sysParams.t_ramp/1000)     # measurement time in [s]
        self.cmd_get_fd_data()

    '''=========================================================================='''
    def cmd_up_ramp(self):

        self.doTransfer(delay = self.sysParams.t_ramp/1000)     # ramp time in [s]

    '''=========================================================================='''
    def cmd_down_ramp(self):

        self.doTransfer(delay = self.sysParams.t_ramp/1000)     # ramp time in [s]

    '''=========================================================================='''
    def cmd_gap(self):

        self.doTransfer(delay = self.sysParams.t_ramp/1000)     # ramp time in [s]

    '''=========================================================================='''
    def cmd_get_td_data(self):

        self.TD_Data.data = [] # empty data container

        self.doTransfer_rxstart()
        if self.single_transfer:
            RecpL = self.doTransfer(RecLenE_fix = [2], RecLenE_nFlex = [-4])
        else:
            RecpL = self.doTransfer(RecLenE_fix = [2])

        act_chan = RecpL[0]
        if act_chan < 1 or act_chan > MAX_CHANNELS: raise CommandError("Invalid number of active channels: %s"%act_chan)
        self.TD_Data.nValues = act_chan * TD_SAMPLES

        if self.single_transfer:
            # extract time information
            self.TD_Data.time0 = RecpL[-2]/100.                               
            self.TD_Data.time1 = RecpL[-1]/100.                
            del RecpL[-2:]
            # extract time domain data
            self.TD_Data.data = RecpL[1:]
        else:
            # read time domain data
            self.TD_Data.data = self.doReceive_int32(nItems = self.TD_Data.nValues)
    
            # read time information
            RecpL = self.doTransfer(RecLenE_fix = [4,4])
            self.TD_Data.time0 = RecpL[0]/100.
            self.TD_Data.time1 = RecpL[1]/100.

    '''=========================================================================='''
    def cmd_get_fd_data(self):

        RecLenE_fix = [1, 4, 4] + [-4]*MAX_CHANNELS*2 + [1, 2, 2]

        self.doTransfer_rxstart()
        if self.single_transfer:
            RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix, RecLenE_nFlex = [-4])
        else:
            RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix)

        self.FD_Data.clear()       # empty data container

        self.FD_Data.datType = RecpL[0]
        self.FD_Data.time0 = RecpL[1]/100.
        self.FD_Data.time1 = RecpL[2]/100.
        self.FD_Data.minValues = RecpL[3:7]
        self.FD_Data.maxValues = RecpL[7:11]
        self.FD_Data.overload = RecpL[11]
        act_chan = RecpL[12]
        self.FD_Data.nSamples = RecpL[13]

        if act_chan < 1 or act_chan > MAX_CHANNELS:
            raise CommandError("Invalid number of active channels: %s"%act_chan)
        if self.FD_Data.nSamples < 1 or self.FD_Data.nSamples > FD_SAMPLES:   
            raise CommandError("Invalid number of samples: %s"%self.FD_Data.nSamples)
        
        if self.single_transfer:
            # extract time information
            self.FD_Data.time2 = RecpL[-1]/100.
            del RecpL[-1]
            # extract FD data
            self.FD_Data.data = RecpL[14:]
        else:
            # read FD data
            if self.FD_Data.datType == DT_MAGN:
                num_smpl = act_chan * self.FD_Data.nSamples
            else:
                num_smpl = act_chan * self.FD_Data.nSamples * 2

            self.FD_Data.data = self.doReceive_int32(nItems = num_smpl)
            
            # read time information
            RecpL = self.doTransfer(RecLenE_fix = [4])
            self.FD_Data.time2 = RecpL[0]/100.    # [ms]

    '''=============================================================================
                                Human Tracker Functions
    ============================================================================='''
    def cmd_set_ht_params(self):

        SndpL = []
        SndpL.append(self.htParams.nRefPulses)      # nRefMeasures
        SndpL.append(self.htParams.timeInterval)    # time Interval
        SndpL.append(self.htParams.nTargets)        # nTargets
        SndpL.append(self.htParams.backgrFilter)    # Suppression Filter (go to the nearest 2**x value)
        SndpL.append(self.htParams.threshFilter)    # Noise Adaption
        SndpL.append(self.htParams.overThreshold)   # Signal Level (with one digit after point) ... 25 = 2.5
        SndpL.append(self.htParams.minDistance)     # minimum target distance [m]
        SndpL.append(self.htParams.minSeparation)   # [Bins]
        SndpL.append(self.htParams.enableTracker)   # enable tracker
        SndpL.append(self.htParams.maxRangeShift)   # maximum target displacement [m]
        SndpL.append(self.htParams.maxLostDetect)   # max lost detect

        # wait until radar performs a calibration
        delay = (self.htParams.nRefPulses*self.htParams.timeInterval/1000.0) #* 1.1
        self.doTransfer(SndLenE = 11*[2], SndpL = SndpL, delay = delay)

    '''=========================================================================='''
    def cmd_get_ht_params(self):

        self.doTransfer_rxstart()
        RecpL = self.doTransfer(RecLenE_fix = 11*[2])

        self.htParams.nRefPulses    = RecpL.pop(0)
        self.htParams.timeInterval  = RecpL.pop(0)
        self.htParams.nTargets      = RecpL.pop(0)
        self.htParams.backgrFilter  = RecpL.pop(0)
        self.htParams.threshFilter  = RecpL.pop(0)
        self.htParams.overThreshold = RecpL.pop(0)
        self.htParams.minDistance   = RecpL.pop(0)
        self.htParams.minSeparation = RecpL.pop(0)
        self.htParams.enableTracker = RecpL.pop(0)
        self.htParams.maxRangeShift = RecpL.pop(0)
        self.htParams.maxLostDetect = RecpL.pop(0)

    '''=========================================================================='''
    def cmd_get_ht_threshold(self):

        self.doTransfer_rxstart()
        if self.single_transfer:
            RecpL = self.doTransfer(RecLenE_fix = [2], RecLenE_nFlex = [-4])
        else:
            RecpL = self.doTransfer(RecLenE_fix = [2])

        num_cells = RecpL.pop(0)
        if num_cells < 1 or num_cells > FD_SAMPLES: 
            raise CommandError("Invalid number of range cells: %s"%num_cells)

        if not self.single_transfer:
            RecpL = self.doTransfer(RecLenE_nFlex = [-4], nFlex = num_cells)

        return RecpL

    '''=========================================================================='''
    def cmd_do_ht_meas(self):

        RecLenE_fix = [4, 4, 4, 4, 2]
        RecLenE_nFlex = [2, 2, 2, 4, 4, -4]

        self.doTransfer_rxstart()
        if self.single_transfer:
            RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix, RecLenE_nFlex = RecLenE_nFlex)
        else:
            RecpL = self.doTransfer(RecLenE_fix = RecLenE_fix)

        # empty entries
        self.htTarget.clear()
        self.htTarget.tPreMeas  = RecpL.pop(0) / 100.
        self.htTarget.tPostMeas = RecpL.pop(0) / 100.
        self.htTarget.tPreProc  = RecpL.pop(0) / 100.
        self.htTarget.tPostProc = RecpL.pop(0) / 100.
        self.htTarget.nTargets  = RecpL.pop(0)

        # read the rest of transmitted data
        if not self.single_transfer:
            RecpL = self.doTransfer(RecLenE_nFlex = RecLenE_nFlex, nFlex = self.htTarget.nTargets)

        for _ in range(self.htTarget.nTargets):
            self.htTarget.id.append     (RecpL.pop(0))
            self.htTarget.tracked.append(RecpL.pop(0))
            self.htTarget.count.append  (RecpL.pop(0))
            self.htTarget.level.append  (RecpL.pop(0))
            self.htTarget.dist.append   (RecpL.pop(0)/1000.)            # [m]
            self.htTarget.angle.append  (RecpL.pop(0)*180/np.pi/2**25)  # [deg]

'''============================================================================'''
class CommandError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
