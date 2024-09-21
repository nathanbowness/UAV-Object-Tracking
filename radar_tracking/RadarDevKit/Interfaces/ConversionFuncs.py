import struct
import math


BYTE_ORDER = '<'        # '@': native, '<': little-endian, '>': big-endian 

'''==============================================================================
    @brief:     Functions to convert different data types to strings for the 
                transmission to the radar or to convert received strings from
                the radar.
    
    @author:    IMST GmbH
    @date:      30.09.2015
=============================================================================='''  

def int8_to_string(val):
    return struct.pack(BYTE_ORDER + 'b', val)

def u8_to_string(val):
    return struct.pack(BYTE_ORDER + 'B', val)

def int16_to_string(val):
    return struct.pack(BYTE_ORDER + 'h', val)

def u16_to_string(val):
    return struct.pack(BYTE_ORDER + 'H', val)
    
def int32_to_string(val):
    return struct.pack(BYTE_ORDER + 'i', val)

def u32_to_string(val):
    return struct.pack(BYTE_ORDER + 'I', val)

def int64_to_string(val):
    return struct.pack(BYTE_ORDER + 'q', val)

def u64_to_string(val):
    return struct.pack(BYTE_ORDER + 'Q', val)

def string_to_int8(buf):
    return struct.unpack(BYTE_ORDER + 'b', buf)[0]

def string_to_u8(buf):
    return struct.unpack(BYTE_ORDER + 'B', buf)[0]

def string_to_int16(buf):
    return struct.unpack(BYTE_ORDER + 'h', buf)[0]

def string_to_u16(buf):
    return struct.unpack(BYTE_ORDER + 'H', buf)[0]

def string_to_int32(buf):
    return struct.unpack(BYTE_ORDER + 'i', buf)[0]

def string_to_u32(buf):
    return struct.unpack(BYTE_ORDER + 'I', buf)[0]

def string_to_int64(buf):
    return struct.unpack(BYTE_ORDER + 'q', buf)[0]

def string_to_u64(buf):
    return struct.unpack(BYTE_ORDER + 'Q', buf)[0]

def split_u16(val):
    val &= 0xFFFF
    return (val >> 8, val & 0xFF)

#convert string into list of 8-bit values 
def string_to_u8_list(buf):
    return [ord(x) for x in buf]

#convert list of 8-bit values into string
def u8_list_to_string(lst):
    return ''.join(map(chr,lst))

# Convert received MAC address to GUI format 
def MAC_NetToHost(PLoad):
    lst = string_to_u8_list(PLoad)
    return "%02X:%02X:%02X:%02X:%02X:%02X"%tuple(lst)

# Convert received IP address to GUI format 
def IP_NetToHost(PLoad):
    lst = string_to_u8_list(PLoad)
    #return "{0:3d}.{1:3d}.{2:3d}.{3:3d}".format(*lst)
    return "%3d.%3d.%3d.%3d"%tuple(lst)

# Convert IP address from GUI into format for transmission
def IP_HostToNet(buf):
    lst = map(int,buf.split('.'))
    return u8_list_to_string(lst)

'''====================================================================
    @brief:   convert payload to UNIX timestamp (seconds since 1.1.1970)
    
    @param PLoad:     payload in milliseconds (64-bit integer)

    @return:          UNIX timestamp in seconds (float)

    @author:          Hubert Kronenberg
    @date:            13.11.2015
===================================================================='''    

def TimeStamp_NetToHost(PLoad):
    try:
        # When payload is given as string convert to list of 16-bit integers
        if type(PLoad) is str:
            PLoad = map(ord,PLoad)
            for i in range(4):
                PLoad[i] = PLoad[2*i] + (PLoad[2*i+1] << 8)
        # Calculate seconds
        secs = 0.0
        for i in range(4,0,-1):
            secs *= 1<<16
            secs += PLoad[i-1]/1000.0
    except:
        secs = 0
    return secs

'''====================================================================
    @brief:   convert UNIX timestamp to payload
    
    @param secs:      UNIX timestamp in seconds (float)
    
    @return:          payload in milliseconds (64-bit integer)

    @author:          Hubert Kronenberg
    @date:            13.11.2015
===================================================================='''    

def TimeStamp_HostToNet(secs):
    try:
        PLoad = [0]*4

        # Split parameters to avoid overflow at multiplication
        (fp,ip)=math.modf(secs)
        (hi,lo)=divmod(int(ip+0.5), 1<<16)

        # Multiplication by 1000
        hi = hi * 1000
        lo = lo * 1000 + int(1000*fp+0.5)

        # Distribute result to payload
        (PLoad[1],PLoad[0]) = divmod(lo, 1<<16)
        (PLoad[2],PLoad[1]) = divmod(PLoad[1] + hi, 1<<16)
        (PLoad[3],PLoad[2]) = divmod(PLoad[2], 1<<16)
    except:
        PLoad = None
    return PLoad

'''====================================================================
    @brief:       increment and decrement iterators
    
    @param i0:    start value
    
    @return:      next value
    
    The iterator is initialized by its start value:
        
        ipp = post_incr(2)
        imm = post_decr(5)
        ppi = pre_incr(2)
        mmi = pre_decr(5)
        
    The "next" statement yields the current value and increments it
    (post increment):
    
        a = next(ipp)    # a = 2
        b = next(ipp)    # b = 3
        c = next(ipp)    # c = 4
    
        x = next(imm)    # x = 5
        y = next(imm)    # y = 4
        z = next(imm)    # z = 3

        a2 = next(ppi)    # a2 = 3
        b2 = next(ppi)    # b2 = 4
        c2 = next(ppi)    # c2 = 5
    
        x2 = next(mmi)    # x2 = 4
        y2 = next(mmi)    # y2 = 3
        z2 = next(mmi)    # z2 = 2

    The iterators can be used similar to i++ and i-- in C
    
        ipp = post_incr(0)
        a = array[next(ipp)]    # works like "a = array[i++]"
    
===================================================================='''    

def post_incr(i0=0):
    i = i0
    while True:
        yield i
        i += 1

def post_decr(i0=0):
    i = i0
    while True:
        yield i
        i -= 1

def pre_incr(i0=0):
    i = i0
    while True:
        i += 1
        yield i

def pre_decr(i0=0):
    i = i0
    while True:
        i -= 1
        yield i
