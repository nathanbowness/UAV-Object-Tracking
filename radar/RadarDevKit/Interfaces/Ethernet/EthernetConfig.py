'''
Created on 02.10.2015

@author: IMST GmbH
'''
class EthernetParams():
    """
    A class to handle Ethernet parameters for the radar connection.

    Attributes
    ----------
    ip : str
        IP address of the radar connection. Default is "192.168.0.2".
    port : int
        Port number for the radar connection. Default is 1024.
    timeout : float
        Timeout value in seconds. Default is 1.0.
    sock : NoneType
        Socket for Ethernet communication. Default is None.
    """
    def __init__(self):
        self.ip = "192.168.0.2"
        self.port = 1024
        
        self.timeout = 1.0
        self.sock = None

        # default connection parameters

        self.default_ip = self.ip
        self.default_port = self.port
    
    def __str__(self):
        """
        Returns a string representation of the Ethernet parameters.
        """
        return f"EthernetParams(ip={self.ip}, port={self.port}, timeout={self.timeout})"
