'''
Created on 02.10.2015

@author: rainer.jetten
'''

import time
from radar_tracking.RadarDevKit.Interfaces import ConversionFuncs as conv
from radar_tracking.RadarDevKit.Interfaces.Commands import Commands
from radar_tracking.RadarDevKit.Interfaces.Commands import CommandError


class IPCommands(Commands):
    '''
    classdocs
    '''
    '--------------------------------------------------------------------------'        
    def __init__(self, connection, main_win):
        #invoke base class constructor
        self.super = super(self.__class__,self)
        self.super.__init__(False)

        self.main_win = main_win
        self.myCon = connection
        self.etherParams = self.main_win.etherParams
                
        # data and data-transport classes
        self.sysParams = self.main_win.sysParams
        self.hwParams = self.main_win.hwParams
        self.htParams = self.main_win.htParams
        self.TD_Data = self.main_win.TD_Data
        self.FD_Data = self.main_win.FD_Data
        self.htTarget = self.main_win.HT_Targets

    '''====================================================================
        @brief: split a string message into a set of sub-messages according 
                to the given structure
                
        @param message: text message
        
        @param struct: byte structure of the message, e.g. [2,2,4,8]
        
        @return: list of sub-messages
    ===================================================================='''  
    def split_message(self, message, struct):
        sub_msg = []
        for n in map(abs,map(int,struct)):
            sub_msg.append(message[:n])
            message = message[n:]
    
        return sub_msg

    '''=============================================================================
    @brief:         Transfer Preprocessing
    @note:          Check connection and send handshake
    ============================================================================='''
    def doTransfer_start(self, cmd_code):

        if self.myCon.is_connected() == False:
            raise EthernetError("Connection Error")
            
        self.myCon.transmit(conv.u16_to_string(cmd_code))

        # receive handshake except after CPU reset
        if cmd_code != self.cmd_list["CMDID_RESTART_CPU"][0]:
            RecMsgLen = 2
            msg = self.myCon.receive(RecMsgLen)
            
            if len(msg) == RecMsgLen and conv.string_to_u16(msg) == cmd_code:
                pass
            else:
                self.myCon.clear_rx_buffer(100)
                raise EthernetError("Handshake Error in command: %s"%hex(cmd_code))

    '''=============================================================================
        @brief: interface specific data transfer function

        @param: SndLenE: List with length of items to be sent
        @param: SndpL: List items to be sent
        @param: RecLenE_fix: List with length of items to be received once
        @param: RecLenE_nFlex: List with length of items to be received repeatedly
        @param: nFlex: Number of repeatedly received items
        @param: delay: Delay time between transmission and reception in ms

        @note:  The type of the length element determines the way of conversion
                before transmission or after reception.
                - numerical string: no conversion 
                - negative number: conversion from or into a signed integer
                - positive number: conversion from or into an unsigned integer
                The value of integer elements may be 1,2,4,8 or their negatives.
    ============================================================================='''
    def doTransfer(self, SndLenE = [], SndpL = [], RecLenE_fix = [], RecLenE_nFlex = [], nFlex = 0, delay = 0):

        # send message
        SndMsgLen = sum(map(abs,map(int,SndLenE)))
        if SndMsgLen > 0:
            # build payload
            msg = b""
            for (item, item_len) in zip(SndpL, SndLenE):
                
                if type(item_len) is str:
                    msg+=str(item)
                elif item_len == 1:
                    msg+=conv.u8_to_string(item)
                elif item_len == 2:
                    msg+=conv.u16_to_string(item)
                elif item_len == 4:
                    msg+=conv.u32_to_string(item)
                elif item_len == 8:
                    msg+=conv.u64_to_string(item)
                elif item_len == -1:
                    msg+=conv.int8_to_string(item)
                elif item_len == -2:
                    msg+=conv.int16_to_string(item)
                elif item_len == -4:
                    msg+=conv.int32_to_string(item)
                elif item_len == -8:
                    msg+=conv.int64_to_string(item)

            # send payload
            if self.myCon.transmit(msg) == False:
                raise EthernetError("Transmission Error")

        # wait before reception
        if delay > 0:
            time.sleep(delay) 

        # items received once
        RecMsgLen = sum(map(abs,map(int,RecLenE_fix)))
        RecpL = []
        if RecMsgLen > 0:

            # receive payload
            msg = self.myCon.receive(RecMsgLen)
            if len(msg) != RecMsgLen:
                raise EthernetError("Wrong message length")

            # split payload according to the structure
            sub_msg = self.split_message(msg, RecLenE_fix)

            # convert elements of sub_msg and store in payload
            for item_len in RecLenE_fix:
                if type(item_len) is str:
                    RecpL.append(sub_msg.pop(0))
                elif item_len == 1:
                    RecpL.append(conv.string_to_u8(sub_msg.pop(0)))
                elif item_len == 2:
                    RecpL.append(conv.string_to_u16(sub_msg.pop(0)))
                elif item_len == 4:
                    RecpL.append(conv.string_to_u32(sub_msg.pop(0)))
                elif item_len == 8:
                    RecpL.append(conv.string_to_u64(sub_msg.pop(0)))
                elif item_len == -1:
                    RecpL.append(conv.string_to_int8(sub_msg.pop(0)))
                elif item_len == -2:
                    RecpL.append(conv.string_to_int16(sub_msg.pop(0)))
                elif item_len == -4:
                    RecpL.append(conv.string_to_int32(sub_msg.pop(0)))
                elif item_len == -8:
                    RecpL.append(conv.string_to_int64(sub_msg.pop(0)))
        
        # repeatedly received items
        RecMsgLen = nFlex * sum(map(abs,map(int,RecLenE_nFlex)))
        if RecMsgLen > 0:

            # receive payload
            msg = self.myCon.receive(RecMsgLen)
            if len(msg) != RecMsgLen:
                raise EthernetError("Wrong message length")

            # split payload according to the structure
            sub_msg = self.split_message(msg, RecLenE_nFlex*nFlex)

            # convert elements of sub_msg and store in payload
            for _ in range(nFlex):
                for item_len in RecLenE_nFlex:
                    if type(item_len) is str:
                        RecpL.append(sub_msg)
                    elif item_len == 1:
                        RecpL.append(conv.string_to_u8(sub_msg.pop(0)))
                    elif item_len == 2:
                        RecpL.append(conv.string_to_u16(sub_msg.pop(0)))
                    elif item_len == 4:
                        RecpL.append(conv.string_to_u32(sub_msg.pop(0)))
                    elif item_len == 8:
                        RecpL.append(conv.string_to_u64(sub_msg.pop(0)))
                    elif item_len == -1:
                        RecpL.append(conv.string_to_int8(sub_msg.pop(0)))
                    elif item_len == -2:
                        RecpL.append(conv.string_to_int16(sub_msg.pop(0)))
                    elif item_len == -4:
                        RecpL.append(conv.string_to_int32(sub_msg.pop(0)))
                    elif item_len == -8:
                        RecpL.append(conv.string_to_int64(sub_msg.pop(0)))

        return RecpL

    '''=============================================================================
        @brief: Receive array of signed 32-bit integer values

        @param: nItems: Number of values

        @note:  The type of the length element determines the way of conversion
                before transmission or after reception.
                - numerical string: no conversion 
                - negative number: conversion from or into a signed integer
                - positive number: conversion from or into an unsigned integer
                The value of integer elements may be 1,2,4,8 or their negatives.
    ============================================================================='''
    def doReceive_int32(self, nItems = 0):
        # Receive data
        msg_len = nItems * 4
        msg = self.myCon.receive(msg_len)
        if len(msg) != msg_len:
            raise EthernetError("Wrong message length (2)")
        # convert data to int32
        sub_msg = self.split_message(msg, [4]*nItems)
        
        return [conv.string_to_int32(item) for item in sub_msg]
                
    '''=========================================================================='''
    def cmd_get_ifc_params(self):

        RecpL = self.doTransfer(RecLenE_fix = ["4",2,"6"])

        if RecpL is None:
            return None

        ip = conv.IP_NetToHost(RecpL[0])
        port = RecpL[1]
        mac = conv.MAC_NetToHost(RecpL[2])

        return (ip, port, mac)

    '''=========================================================================='''        
    def cmd_set_ifc_params(self):

        ip = self.etherParams.ip
        port = self.etherParams.port

        msg = []
        msg.append(conv.IP_HostToNet(ip))
        msg.append(port)

        self.doTransfer(SndLenE = ["4",2], SndpL = msg)

        return (ip, port)

    '''=========================================================================='''        
    def cmd_activate_ifc_params(self):

        self.doTransfer()

    '''=========================================================================='''
    def cmd_restart_system(self):
        self.doTransfer()
        time.sleep(2)
        # TODO: reconnect interface after CPU reset
        #EVT_CUSTOM.ProcessEvent('IfcReconnect')

    '''=========================================================================='''
    def cmd_get_burst_data(self):
        pass

    '''=========================================================================='''
    def cmd_do_track_meas(self):
        pass
    
    '''=========================================================================='''
    def cmd_set_track_params(self):
        pass
    
    '''=========================================================================='''
    def cmd_send_track_params(self):
        pass

'''============================================================================'''
class EthernetError(CommandError):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
