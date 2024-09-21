'''
@brief: Scan for Existing Radar Modules in Ethernet

@date: 19.02.2016

@author: hubert.kronenberg
'''

import socket,thread,time,SocketServer
from collections import namedtuple
from GUI.Interfaces import ConversionFuncs as conv

UDPPORT_RADAR = 4142        # port for datagrams from host to radar
UDPPORT_HOST = 4143         # port for datagrams from radar to host
MAGIC_NR = 47475            # magic number as a mark for valid datagram

# data structure for result
dgram = namedtuple('dgram', ['ip', 'nr', 'port'])

'''====================================================================
    @brief: Class for Collecting Datagrams from Radar  
            
    @global: (inp) wanted_nr    Number of Wanted Radar (if value is
                                "None", scan for all radars)
    @global: (out) data         List with all found radars as "dgram"
                                items (i.e. ip/nr tuples)
===================================================================='''  
class Handler(SocketServer.DatagramRequestHandler):

    data = []                   # container for received data
    wanted_nr = None            # number of specific radar to be found
    
    def handle(self):
        
        cls = self.__class__

        # read datagram and sender ip
        recv_dgram = self.rfile.readline()
        recv_ip = self.client_address[0]

        # check validity of datagram
        #
        # expected: magic number (2 bytes)
        #           radar number (2 bytes)
        if len(recv_dgram) < 6:
            return
        if (conv.string_to_u16(recv_dgram[0:2]) != MAGIC_NR):
            return

        # extract radar number
        recv_nr = conv.string_to_u16(recv_dgram[2:4])
        # extract IP port
        recv_port = conv.string_to_u16(recv_dgram[4:6])
        # store the received data, if the radar number conforms
        # to the wanted number or unspecific scan is performed
        if (cls.wanted_nr is None) or (cls.wanted_nr == recv_nr):
            item = dgram(nr = recv_nr, ip = recv_ip, port = recv_port)
            cls.data.append(item)

    def __del__(self):
        pass

'''====================================================================
    @brief: Class for Collecting Radar Numbers and associated IP's
            by UDP
            
    The scan is initiated by a broadcast request via port UDPPORT_RADAR.
    The request datagram consists of the magic number.

    The replies are expected on port UDPPORT_HOST. The reply datagram
    consists of the magic number followed by the radar number. The
    sender IP is extracted from the header of the reply.

    The result consists of a list of named tuples (ip, nr, port). If
    the scan is confined to a certain radar all replies from other
    radars are omitted and the list contains only one element.
===================================================================='''  
class ScanRadars:
    
    serv = None         # UDP Server
    thrd = 0            # Thread ID
    hdata = Handler     # Datagram Handler Class

    '''====================================================================
        @brief: Constructor
                
        @param nr: number of radar to be scanned for
                   (if None scan for all available radars) 

        @global: (out) wanted_nr    radar number
    ===================================================================='''  
    def __init__(self, nr = None):
        
        cls = self.__class__

        # set global variables
        cls.hdata.wanted_nr = nr

        # start server for datagram collection
        if cls.serv is None:
            cls.serv =  SocketServer.UDPServer(('',UDPPORT_HOST),cls.hdata)
            cls.thrd = thread.start_new_thread(cls.serv.serve_forever,())

        time.sleep(0.5)
        
        # send request to all radars
        sc = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sc.setsockopt(socket.SOL_SOCKET,socket.SO_BROADCAST,1)
        sc.connect(("<broadcast>",UDPPORT_RADAR))
        sc.send(conv.u16_to_string(MAGIC_NR))
        sc.close()
        
        time.sleep(1)

    '''====================================================================
        @brief: Return collected data
    ===================================================================='''  
    def result(self):
        cls = self.__class__
        return cls.hdata.data

    '''====================================================================
        @brief: Destructor
        
        Stop server and empty data container
    ===================================================================='''  
    def __del__(self):
        cls = self.__class__
        cls.hdata.data = []
        cls.serv.shutdown()
        cls.serv = None
