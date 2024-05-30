# -*- coding: cp1252 -*-
'''
Created on 26.06.2015

@author: manfred.haegelen
'''


import socket

'''
Constants
'''
BUFFER_SIZE = 1024      # [bytes]
MSG_ENABLE = True

'=============================================================================='
class IPConnection(object):
    '''
    classdocs
    '''

    '--------------------------------------------------------------------------'        
    def __init__(self, main_win):
        '''
        Constructor
        '''                
        self.main_win = main_win
        self.etherParams = main_win.etherParams        
        self.sock = self.etherParams.sock
        self.show_bytes = False
        
    '--------------------------------------------------------------------------'        
    def connect(self):
        
        self.disconnect()   # close old connection before starting a new one
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.etherParams.timeout)
            self.sock.connect((self.etherParams.ip, self.etherParams.port))
            #self.show_message("Connection to "+self.etherParams.ip+":"+str(self.etherParams.port)+" established.")
            return True
        except Exception as e:
            self.sock = None
            print(f"Connection to {self.etherParams.ip}:{self.etherParams.port} failed: {e}")
            #self.show_message("Connection to "+self.etherParams.ip+":"+str(self.etherParams.port)+" failed.")
            return False
    
    '--------------------------------------------------------------------------'        
    def default_connect(self):
        
        self.disconnect()   # close old connection before starting a new one
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.etherParams.timeout)
            self.sock.connect((self.etherParams.default_ip, self.etherParams.default_port))            
            return True
        except:
            self.sock = None
            return False
        
    '--------------------------------------------------------------------------'        
    def disconnect(self):
        if self.sock != None:
            self.sock.close()
            self.sock = None
            #self.show_message("Socket connection closed.")
    
    '--------------------------------------------------------------------------'        
    # pass text message to main window        
    def show_message(self, message):
        
        if MSG_ENABLE == True:
            self.main_win.show_message(message)
    
    '--------------------------------------------------------------------------'        
    # True: connection  established, False: connection closed        
    def is_connected(self):
        return (self.sock != None)

    '--------------------------------------------------------------------------'        
    # transmit data using Socket connection
    def transmit(self, msg):
        
        msg_size = len(msg)
        totalsent = 0

        try:
            # update timeout (optional)
            self.sock.settimeout(self.etherParams.timeout)
                    
            # repeat until all data is transmitted
            while totalsent < msg_size:
                sent = self.sock.send(msg[totalsent:])
                if sent == 0:
                    return False  # socket connection error
                totalsent = totalsent + sent
                
            # show received data
            if totalsent > 0 and self.show_bytes == True:
                out = "<< "+str(totalsent)+" bytes: "
                for b in msg[:totalsent]:
                    out += "%02X " % ord(b)
                self.show_message(out)
                
            return True

        except socket.error:
            self.connect()
            return False
            
        except:
            return False
            
    '--------------------------------------------------------------------------'        
    # receive data using Socket connection         
    def receive(self, msg_size):
        
        msg = b""
        totalrecv = 0
        
        try:
            # repeat until all data is received
            while totalrecv < msg_size:
                req_bytes = min(msg_size-totalrecv, BUFFER_SIZE)    # requested bytes
                msg_block = self.sock.recv(req_bytes)
                
                if msg_block == b"":
                    break   # socket connection error
                
                msg += msg_block
                totalrecv = len(msg)
        except:
            pass # timeout

        # show received data
        if totalrecv > 0 and self.show_bytes == True:
            out = ">> "+str(totalrecv)+" bytes: "
            for b in msg:
                out += "%02X " % ord(b)
            self.show_message(out)

        return msg      # all received bytes
    
    '--------------------------------------------------------------------------'        
    # read data from socket until a timeout occurs
    def clear_rx_buffer(self, block=4):
        
        while 1:
            msg = self.receive(block)   # try to read 'block' bytes
            msg_len = len(msg)
            
            if msg_len > 0 and self.show_bytes == True:
                out = ">> "+str(msg_len)+" bytes: "
                for b in msg:
                    out += "%02X " % ord(b)
                self.show_message(out)
            
            if msg_len < block:
                #self.show_message("Receiver buffer is empty now.")
                break
        
