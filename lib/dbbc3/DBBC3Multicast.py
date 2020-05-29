import socket
import locale
import re
import struct
import math
from datetime import datetime

class DBBC3Multicast(object):

    def __init__(self, group="224.0.0.255", port=25000, timeout=2):

        self.socket = None
        self.group = group
        self.port = port
        self.message = {} 

        self._connect(timeout)

        # configure multicast layout based on mode and version
        self._setupLayout()


    @property
    def lastMessage(self):
        '''
        Returns the last received multicast message

        Returns:
            (dict): the last message dictionary received via multicast.
        '''

        return self.message

    def _connect(self, timeout):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.settimeout(timeout)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.group, self.port))

        mreq = struct.pack("4sl", socket.inet_aton(self.group), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        
    def _setupLayout(self):

        # determine mode and version
        valueArray = self.sock.recv(16384)
        self._parseVersion(valueArray)

        # defaults
        self.gcomoOffset = 32
        self.dcOffset = self.gcomoOffset + 64
        self.adb3lOffset = self.dcOffset + 64
        self.core3hOffset = self.adb3lOffset + 92
        self.bbcOffset = self.core3hOffset + 24


    def _parseVersion(self, message):

        versionString = message[0:32].decode("utf-8").split(",")
        versionString[2] = versionString[2].replace(u'\x00', '')
        amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2), versionString[2])

        # DDC_V,124,November 07 2019
        self.message["mode"] = versionString[0]
        self.message["majorVersion"] = int(versionString[1])
        self.message["minorVersionString"] = versionString[2]
        self.message["minorVersion"] = int(datetime.strptime(amended.strip().encode("utf-8"), '%B %d %Y').strftime('%y%m%d'))
        
    def _parseGcomo(self, message):
        for i in range(0,8):
            gcomo = {}
            shortArray = struct.unpack('HHH', message[self.gcomoOffset+i*8+2:self.gcomoOffset+i*8+8])
            if message[32+i*8] == 0:
                gcomo["mode"] = "man"
        #        print(str(i+1) + " man" + str(shortArray))
            else:
                gcomo["mode"] = "agc"
        #        print(str(i+1) + " agc" + str(shortArray))
            gcomo["attenuation"] = int(shortArray[0])
            gcomo["count"] = int(shortArray[1])
            gcomo["target"] = int(shortArray[2])

            self.message["if_"+str(i+1)] = gcomo
            

    def _parseDC(self,message):

        # Downconverter Values
        for i in range(0,8):
            synth = {}
            shortArray = struct.unpack('HHHH', message[self.dcOffset+i*8:self.dcOffset+i*8+8])
        #    print(str(shortArray))

            synth["status"] = int(shortArray[0])
            synth["lock"] = int(shortArray[1])
            synth["attenuation"] = int(shortArray[2])
            synth["frequency"] = float(shortArray[3])

            self.message["if_"+str(i+1)]["synth"] = synth
    
    def _parseAdb3l(self,message):
        offset = self.adb3lOffset

        # ADB3L Values
        for i in range(0,8):
            s0 = {}
            s1 = {}
            s2 = {}
            s3 = {}

            powerArray = struct.unpack('IIII', message[offset:offset+16])
            #print(str(powerArray))
            s0["power"] = int(powerArray[0])
            s1["power"] = int(powerArray[1])
            s2["power"] = int(powerArray[2])
            s3["power"] = int(powerArray[3])

            offset = offset + 16
            bstatArray_0 = struct.unpack('IIII', message[offset:offset+16])
            #print(str(bstatArray_0) + str(sum(bstatArray_0)))
            offset = offset + 16
    
            bstatArray_1 = struct.unpack('IIII', message[offset:offset+16])
            #print(str(bstatArray_1) + str(sum(bstatArray_1)))
            offset = offset + 16
    
            bstatArray_2 = struct.unpack('IIII', message[offset:offset+16])
            #print(str(bstatArray_2) + str(sum(bstatArray_2)))
            offset = offset + 16
    
            bstatArray_3 = struct.unpack('IIII', message[offset:offset+16])
            #print(str(bstatArray_3) + str(sum(bstatArray_3)))
    
            s0["stats"] = bstatArray_0
            s1["stats"] = bstatArray_1
            s2["stats"] = bstatArray_2
            s3["stats"] = bstatArray_3

            offset = offset + 16
            corrArray = struct.unpack('III', message[offset:offset+12])
            #print(str(corrArray))

            self.message["if_"+str(i+1)]["sampler0"]= s0
            self.message["if_"+str(i+1)]["sampler1"]= s1
            self.message["if_"+str(i+1)]["sampler2"]= s2
            self.message["if_"+str(i+1)]["sampler3"]= s3
            
            self.message["if_"+str(i+1)]["delayCorr"]= corrArray

    def _parseCore3h(self,message):
        offset = self.core3hOffset

        # Core3H Values
        for i in range(0,8):
            timeValue = struct.unpack('I', message[offset:offset+4])
            #print("Time["+str(i)+"] " +str(timeValue))
            self.message["if_"+str(i+1)]["time"]= timeValue[0]

            offset = offset + 4
    
            ppsDelayValue = struct.unpack('I', message[offset:offset+4])
            #print("pps_delay["+str(i)+"] " +str(ppsDelayValue))
            self.message["if_"+str(i+1)]["ppsDelay"]= ppsDelayValue[0]
            offset = offset + 4
    
            tpS0_0Value = struct.unpack('I', message[offset:offset+4])
            #print("tpS0_0["+str(i)+"] " +str(tpS0_0Value))
            self.message["if_"+str(i+1)]["tpOn"]= tpS0_0Value[0]
            offset = offset + 4
    
            tpS0_1Value = struct.unpack('I', message[offset:offset+4])
            #print("tpS0_1["+str(i)+"] " +str(tpS0_1Value))
            self.message["if_"+str(i+1)]["tpOff"]= tpS0_1Value[0]
            offset = offset + 4
    
            tsysValue = struct.unpack('I', message[offset:offset+4])
            #print("Tsys["+str(i)+"] " + str(tsysValue))
            self.message["if_"+str(i+1)]["tsys"]= tsysValue[0]
            offset = offset + 4
    
            sefdValue = struct.unpack('I', message[offset:offset+4])
            #print("Sefd["+str(i)+"] " + str(sefdValue))
            self.message["if_"+str(i+1)]["sefd"]= sefdValue[0]
            offset = offset + 4
    
            
    def _parseBBC(self, message):

        # BBC Values
        offset = self.bbcOffset
        for i in range(0,128):
            ifNum = int(math.floor(i /  16)) + 1
            bbc= {}
            bbcValue = struct.unpack('IBBBBIIIIHHHHHHHH', message[offset:offset+40])
            offset = offset + 40

            bbc["frequency"] = float(bbcValue[0]/524288)
            bbc["bandwidth"] = bbcValue[0]
            bbc["agcStatus"] = bbcValue[1]
            bbc["gainUSB"] = bbcValue[2]
            bbc["gainLSB"] = bbcValue[3]
            bbc["powerOnUSB"] = bbcValue[4]
            bbc["powerOnLSB"] = bbcValue[5]
            bbc["powerOffUSB"] = bbcValue[6]
            bbc["powerOffLSB"] = bbcValue[7]
            bbc["stat00"] = bbcValue[8]
            bbc["stat01"] = bbcValue[9]
            bbc["stat10"] = bbcValue[10]
            bbc["stat11"] = bbcValue[11]
            bbc["tsysUSB"] = bbcValue[12]
            bbc["tsysLSB"] = bbcValue[13]
            bbc["sefdUSB"] = bbcValue[14]
            bbc["sefdLSB"] = bbcValue[15]

            self.message["if_" + str(ifNum)]["bbc_" + str(i+1)] = bbc
            
        
    def poll(self):
        '''
        Parses the multicast message

        The multicast message from the DBBC3 is parsed and the contents are returned in a
        multidimensional dictionary with the following structure::

            "majorVersion" (int): the major version of the running DBBC3 control software
            "minorVersion" (int): the minor version of the running DBBC3 control software
            "minorVersionString" (str): a human readable string of the minor version of the running DBBC3 control software
            "mode" (str): the mode of the the running DBBC3 control software
            "if_{1..8}" (dict): dictionaries holding the parameters of IF 1-8

              "if_1": {
    "attenuation": 9,
    "count": 21015,
    "delayCorr": [
      192757734,
      192986236,
      194070375
    ],
    "mode": "agc",
    "ppsDelay": [
      0
    ],
    "sampler0": {
      "power": 57240788,
      "stats": [
        28,
        7836,
        7724,
        35
      ]
    },
    "sampler1": {
      "power": 56505770,
      "stats": [
        28,
        7768,
        7795,
        32
      ]
    },
    "sampler2": {
      "power": 57090201,
      "stats": [
        28,
        7809,
        7750,
        36
      ]
    },
    "sampler3": {
      "power": 56796681,
      "stats": [
        27,
        7823,
        7737,
        36
      ]
    },
    "sefd": [
      0
    ],
    "synth": {
      "attenuation": 10,
      "frequency": 4096.0,
      "lock": 1,
      "status": 1
    },
    "target": 32000,
    "time": [
      0
    ],
    "tpOff": [
      0
    ],
    "tpOn": [
      0
    ],
    "tsys": [
      0
    ]
  },
        '''

        self.message = {}

        valueArray = self.sock.recv(16384)

        self._parseVersion(valueArray)
        self._parseGcomo(valueArray)
        self._parseDC(valueArray)
        self._parseAdb3l(valueArray)
        self._parseCore3h(valueArray)
        self._parseBBC(valueArray)

        return(self.message)

