#!/usr/bin/env python3

import socket
import struct
import datetime
import sys

MCAST_GRP = '224.0.0.255'
MCAST_PORT = 25000
IS_ALL_GROUPS = True

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
if IS_ALL_GROUPS:
    # on this port, receives ALL multicast groups
    sock.bind(('', MCAST_PORT))
else:
    # on this port, listen ONLY to MCAST_GRP
    sock.bind((MCAST_GRP, MCAST_PORT))
mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

while True:
    #print(sock.recv(1024))
    valueArray = sock.recv(16384)
    offset = 0
    versionString = valueArray[offset:offset+32].decode("utf-8") 
    print(datetime.datetime.utcnow())
    print(versionString)
    offset = offset + 32
    
    # GCoMo values
    for i in range(0,8):
        shortArray = struct.unpack('HHH', valueArray[offset+i*8+2:offset+i*8+8])
        if valueArray[32+i*8] == 0:
            print(str(i+1) + " man" + str(shortArray))
        else:
            print(str(i+1) + " agc" + str(shortArray))
            
    offset = offset + (8 * 8)
           
    # Downconverter Values        
    for i in range(0,8):
        shortArray = struct.unpack('HHHH', valueArray[offset+i*8:offset+i*8+8])
   #     print(str(shortArray))
        
    offset = offset + (8 * 8)
        
    # ADB3L Values
    for i in range(0,8):
        powerArray = struct.unpack('IIII', valueArray[offset:offset+16])
   #     print(str(powerArray))
        offset = offset + 16
        
        bstatArray_0 = struct.unpack('IIII', valueArray[offset:offset+16])
   #     print(str(bstatArray_0) + str(sum(bstatArray_0)))
        offset = offset + 16
        
        bstatArray_1 = struct.unpack('IIII', valueArray[offset:offset+16])
   #     print(str(bstatArray_1) + str(sum(bstatArray_1)))
        offset = offset + 16
        
        bstatArray_2 = struct.unpack('IIII', valueArray[offset:offset+16])
   #     print(str(bstatArray_2) + str(sum(bstatArray_2)))
        offset = offset + 16
        
        bstatArray_3 = struct.unpack('IIII', valueArray[offset:offset+16])
   #     print(str(bstatArray_3) + str(sum(bstatArray_3)))
        offset = offset + 16
        
        corrArray = struct.unpack('III', valueArray[offset:offset+12])
   #     print(str(corrArray))
        offset = offset + 12
        
    # Core3H Values    
    for i in range(0,8):
        timeValue = struct.unpack('I', valueArray[offset:offset+4])
   #     print("Time["+str(i)+"] " +str(timeValue))
        offset = offset + 4
        
        ppsDelayValue = struct.unpack('I', valueArray[offset:offset+4])
   #     print("pps_delay["+str(i)+"] " +str(ppsDelayValue))
        offset = offset + 4
        
        tpS0_0Value = struct.unpack('I', valueArray[offset:offset+4])
   #     print("tpS0_0["+str(i)+"] " +str(tpS0_0Value))
        offset = offset + 4
        
        tpS0_1Value = struct.unpack('I', valueArray[offset:offset+4])
   #     print("tpS0_1["+str(i)+"] " +str(tpS0_1Value))
        offset = offset + 4
        
        tsysValue = struct.unpack('I', valueArray[offset:offset+4])
   #     print("Tsys["+str(i)+"] " + str(tsysValue))
        offset = offset + 4
        
        sefdValue = struct.unpack('I', valueArray[offset:offset+4])
   #     print("Sefd["+str(i)+"] " + str(sefdValue))
        offset = offset + 4
        
#    # BBC Values
##    for i in range(0,128):
#        bbcValue = struct.unpack('IBBBBIIIIHHHHHHHH', valueArray[offset:offset+40])
#        offset = offset + 40
#        if (i < 8) or (63 < i < 72):
#            print("[" + str(i+1) + "]" + str(bbcValue[0]//524288) + "," + str(bbcValue[1])+ "," + str(bbcValue[2])+ "," + str(bbcValue[3])+ "," + str(bbcValue[4])+ "," + str(bbcValue[5])+ "," + str(bbcValue[6])+ "," + str(bbcValue[7])+ "," + str(bbcValue[8])+ ",",end='')
#            print(str(bbcValue[9])+ ","+ str(bbcValue[10])+ "," + str(bbcValue[11])+ "," + str(bbcValue[12])+ "," + str(bbcValue[13])+ "," +str(bbcValue[14])+ "," +str(bbcValue[15])+ "," +str(bbcValue[16]))
#
