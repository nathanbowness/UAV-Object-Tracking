'''
Created on 02.10.2015

@author: IMST GmbH
'''
class EthernetParams():
    def __init__(self):
        self.ip = "192.168.0.2"
        self.port = 1024
        
        self.timeout = 1.0
        self.sock = None

        # default connection parameters

        self.default_ip = self.ip
        self.default_port = self.port
