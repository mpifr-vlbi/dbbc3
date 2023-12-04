# -*- coding: utf-8 -*-

#  Copyright (C) 2019 Helge Rottmann, Max-Planck-Institut für Radioastronomie, Bonn, Germany
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
  This module is part of the DBBC3 package and implements the muticast 
  functionality.
'''
__author__ = "Helge Rottmann"
__copyright__ = "2022, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

import socket
import locale
import re
import struct
import math
import sys
import importlib
from datetime import datetime
from abc import ABC, abstractmethod


class DBBC3MulticastFactory(object):
    '''
    Factory class to create an instance of a Multicast sub-class matching the current DBBC3 mode and software version
    '''

    def create(self, group="224.0.0.255", port=25000, timeout=10):
        """
        Return an instance of the Multicast sub-class that matches the currently running mode and software version

        Args:
            group (str, optional): the multicast group to use (default: 224.0.0.255)
            port (int, optional): the multicast port to use (default: 25000)
            timeout (int, optional): the socket timeout in seconds (default: 10)

        Returns:
            the instance of the multicast class matching the current mode and software version
        """

        # obtain mode and version from parsing message
        mc = DBBC3MulticastBase(group, port, timeout)
        #print (mc.message["mode"])
        #print (mc.message["majorVersion"])
         
        csClassName = _getMatchingVersion(mc.message["mode"], mc.message["majorVersion"])
        if (csClassName == ""):
            csClassName = "DBBC3MulticastDefault"
        CsClass = getattr(importlib.import_module("dbbc3.DBBC3Multicast"), csClassName)
        #print (csClassName, CsClass)
        return(CsClass(group, port ,timeout))

def _getMatchingVersion(mode, majorVersion):
    '''
    Determines the MultiCast sub-class to be used for the given mode and major version.

    if mode is not given the default Multicast class (DBBC3MulticastBase) is selected
    if majorVersion is not given the latest implemented version for the activated mode will be used.

    Args:
        mode (str): the dbbc3 mode (e.g. OCT_D)
        majorVersion (str): the command set major version

    Returns:
        str: The class name that implements the valdation methods for the given mode and major version


    '''

    # parse all class names of this module
    current_module = sys.modules[__name__]

    pattern = re.compile("DBBC3Multicast_%s_(.*)"%(mode))

    versions = []
    for key in dir(current_module):
        if isinstance( getattr(current_module, key), type ):
            match = pattern.match(key)
            if match:
                versions.append(match.group(1))

    # no versions found for this mode
    if len(versions) == 0:
        return("DBBC3MulticastBase")

    versions.sort()

    if (majorVersion == ""):
        # if no specific version was requested return the most recent one
        pickVer = versions[-1]
    else:
        pickVer = versions[0]
        for i in versions:
            if int(i) <= int(majorVersion):
                pickVer = i
            else:
                break

    ret = "DBBC3Multicast_%s_%s" % (mode,pickVer)
    return(ret)

class DBBC3MulticastAbstract(ABC):
    '''
    Abstract base class for all derived Multicast classes
    '''

    @abstractmethod
    def poll(self):
        pass

class DBBC3MulticastBase(DBBC3MulticastAbstract):
    '''
    Base class that contains the multicast functionality common to all modes and
    software versions.

     All classes that contain multicast content specific to a particaular mode and
     software version should be derived from this class.

     Note:
        All derived sub-classes must follow the naming convention DBBC3Mutlicast_*modei*_*version*

     Args:
        group (str, optional): the multicast group to use (default: 224.0.0.255)
        port (int, optional): the multicast port to use (default: 25000)
        timeout (int, optional): the socket timeout in seconds (default: 10)
'''

    def __init__(self, group, port, timeout):

        self.socket = None
        self.group = group
        self.port = port
        self.message = {} 

        self._connect(timeout)

        # configure multicast layout based on mode and version
        self._setupLayout()

        super().__init__()


    @property
    def lastMessage(self):
        ''' dict: Returns the last received multicast message dictionary '''

        return self.message

    def _connect(self, timeout):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.settimeout(timeout)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.sock.bind((self.group, self.port))

        mreq = struct.pack("4sl", socket.inet_aton(self.group), socket.INADDR_ANY)

        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        
    def poll(self):
        '''
        Poll and parse the next multicast message

        Returns:
            None
        '''

        self.message = {}
        valueArray = self.sock.recv(16384)

        self._parseVersion(valueArray, 0)


    def _setupLayout(self):

        # determine mode and version
        valueArray = self.sock.recv(16384)

        self._parseVersion(valueArray, 0)
        
        if self.message["mode"] == "OCT_D":
            self.ifMaskOffset = 32
            self.gcomoOffset = self.ifMaskOffset + 2
            self.dcOffset = self.gcomoOffset + 8*8
            self.adb3lOffset = self.dcOffset + 8*8
            self.core3hOffset = self.adb3lOffset + 8*48
        else:
            # defaults
            self.gcomoOffset = 32
            self.dcOffset = self.gcomoOffset + 8*8
            self.adb3lOffset = self.dcOffset + 8*8
            self.core3hOffset = self.adb3lOffset + 8*92
            self.bbcOffset = self.core3hOffset + 8*24


    def _calcStatsPercentage(self, stats):

        total = float(sum(stats))
        perc = []
        for level in stats:
            if total == 0:
                value = 0.0
            else:
                value = float(level)/total*100.0
            perc.append(value)

#        print ("Stats:", stats, total, perc)
        return(tuple(perc))

    def _parseVersion(self, message, offset):
        '''
        Parses the multicast message for the firmware mode and version

        Result are appended to the message dictionary with keys: mode, majorVersion, minorVersion, minorVersionString

        Example:
              "mode": "OCT_D"
              "majorVersion": 120
              "minorVersion": 211019
              "minorVersionString": "October 19th 2021"

        Returns:
            the byte start index of the next multicast section
        '''

        versionString = message[offset:offset+32].decode("utf-8").split(",")
        versionString[2] = versionString[2].replace(u'\x00', '')
        amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2), versionString[2])

        # DDC_V,124,November 07 2019
        self.message["mode"] = versionString[0]
        self.message["majorVersion"] = int(versionString[1])
        self.message["minorVersionString"] = versionString[2]
        #self.message["minorVersion"] = int(datetime.strptime(amended.strip().encode("utf-8"), '%B %d %Y').strftime('%y%m%d'))
        self.message["minorVersion"] = int(datetime.strptime(amended.strip(), '%B %d %Y').strftime('%y%m%d'))

        return(32)

    def _parseGcomo(self, mc, offset):
        '''
        Parses the multicast message for the GCoMo states

        Results are appended to the message dictionary with keys: if_1 to if_8

        Example:
            "if_1": { "attenuation": 20, "count": 31787, "mode": "agc", "target": 32000 },
            "if_2": { "attenuation": 24, "count": 32386, "mode": "agc", "target": 32000 },
            ...

        Parameters:
            message( :obj of bytes) : the multicast binary message
            offset (int): the byte index into the message to start the parsing

        Returns:
            the byte start index of the next multicast section
        '''

        for i in range(0,8):
            gcomo = {}
            shortArray = struct.unpack('HHH', mc[offset+i*8+2:offset+i*8+8])
            #print ("SHORTARRAY: ", shortArray)
            if int(mc[offset+i*8]) == 0:
                gcomo["mode"] = "man"
            else:
                gcomo["mode"] = "agc"
            gcomo["attenuation"] = int(shortArray[0])
            gcomo["count"] = int(shortArray[1])
            gcomo["target"] = int(shortArray[2])


            self.message["if_"+str(i+1)] = gcomo

        return (offset+64)

    def _parseDC(self,message, offset):
        '''
        Parses the multicast message for the downconversion states

        Results are appended to the message dictionary with keys: status, lock, attenuation, frequency

        Example:
            "if_1": { "attenuation": 20, "count": 32031, "mode": "agc",
                 "synth": { "attenuation": 18, "frequency": 4524.0, "lock": 1, "status": 1 },
                 "target": 32000 }

        Parameters:
            message( :obj of bytes) : the multicast binary message
            offset (int): the byte index into the message to start the parsing

        Returns:
            the byte start index of the next multicast section
        '''

        # Downconverter Values
        for i in range(0,8):
            synth = {}
            shortArray = struct.unpack('HHHH', message[offset+i*8:offset+i*8+8])
        #    print(str(shortArray))

            synth["status"] = int(shortArray[0])
            synth["lock"] = int(shortArray[1])
            synth["attenuation"] = int(shortArray[2])
            synth["frequency"] = float(shortArray[3])

            self.message["if_"+str(i+1)]["synth"] = synth

        return(offset+64)
        



class DBBC3Multicast_DDC_U_125(DBBC3MulticastBase):
    '''
    Class for parsing multicast broadcasts specific to the the DDC_U 125 mode/version.
    '''

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

        Returns:
            None
        '''

        self.message = {}
        valueArray = self.sock.recv(16384)

        self._parseVersion(valueArray, 0)
        nIdx = self._parseGcomo(valueArray, self.gcomoOffset)
        nIdx = self._parseDC(valueArray, nIdx)
        nIdx = self._parseAdb3l(valueArray, nIdx)
        nIdx = self._parseCore3h(valueArray, nIdx)
        nIdx = self._parseBBC(valueArray, nIdx)

        return(self.message)

    def _parseAdb3l(self,message, offset):
#OK

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
            offset = offset + 16
    
            s0["stats"] = bstatArray_0
            s1["stats"] = bstatArray_1
            s2["stats"] = bstatArray_2
            s3["stats"] = bstatArray_3

            s0["statsFrac"] = self._calcStatsPercentage(bstatArray_0)
            s1["statsFrac"] = self._calcStatsPercentage(bstatArray_1)
            s2["statsFrac"] = self._calcStatsPercentage(bstatArray_2)
            s3["statsFrac"] = self._calcStatsPercentage(bstatArray_3)

            corrArray = struct.unpack('III', message[offset:offset+12])
            offset += 12

            self.message["if_"+str(i+1)]["sampler0"]= s0
            self.message["if_"+str(i+1)]["sampler1"]= s1
            self.message["if_"+str(i+1)]["sampler2"]= s2
            self.message["if_"+str(i+1)]["sampler3"]= s3
            
            self.message["if_"+str(i+1)]["delayCorr"]= corrArray

        return(offset)

    def _parseCore3h(self,message, offset):

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

        return(offset)
    
            
    def _parseBBC(self, message, offset):

        # BBC Values
        for i in range(0,128):
            if i < 64:
                    ifNum = int(math.floor(i /  8)) + 1
            else:
                    ifNum = int(math.floor((i-64) /  8)) + 1
            bbc= {}
            bbcValue = struct.unpack('IBBBBIIIIHHHHHHHH', message[offset:offset+40])
            offset = offset + 40

            bbc["frequency"] = float(bbcValue[0]/524288)
            bbc["bandwidth"] = bbcValue[1]
            bbc["agcStatus"] = bbcValue[2]
            bbc["gainUSB"] = bbcValue[3]
            bbc["gainLSB"] = bbcValue[4]
            bbc["powerOnUSB"] = bbcValue[5]
            bbc["powerOnLSB"] = bbcValue[6]
            bbc["powerOffUSB"] = bbcValue[7]
            bbc["powerOffLSB"] = bbcValue[8]
            bbc["stat00"] = bbcValue[9]
            bbc["stat01"] = bbcValue[10]
            bbc["stat10"] = bbcValue[11]
            bbc["stat11"] = bbcValue[12]
            bbc["tsysUSB"] = bbcValue[13]
            bbc["tsysLSB"] = bbcValue[14]
            bbc["sefdUSB"] = bbcValue[15]
            bbc["sefdLSB"] = bbcValue[16]

            self.message["if_" + str(ifNum)]["bbc_" + str(i+1)] = bbc

        return(offset)
            
        


class DBBC3Multicast_OCT_D_120(DBBC3MulticastBase):
    '''
    Class for parsing multicast broadcasts specific to the the DDC_U 125 mode/version.
    '''

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
        
        Returns:
            None
        '''

        self.message = {}
        valueArray = self.sock.recv(16384)

        self._parseVersion(valueArray, 0)
        nIdx = self._parseIFMask(valueArray, 32)
        nIdx = self._parseGcomo(valueArray, nIdx)
        nIdx = self._parseDC(valueArray, nIdx)
        nIdx = self._parseAdb3l(valueArray, nIdx)
        nIdx = self._parseCore3h(valueArray, nIdx)

        return(self.message)


    def _parseIFMask(self, mc, offset):
        '''
        Parses the multicast message to obtain information about IFs (boards)
        installed in the system and activated boards

        Results are appended to the message dictionary with keys: boardPresent, boardActive.:
        Example:
            "boardPresent": [ true, true, true, true, false, false, false, false ]
            "boardActive": [ true, true, true, true, false, false, false, false ]

            indicating boards 0-4 being present and active

        Parameters:
            message( :obj of bytes) : the multicast binary message
            offset (int): the byte index into the message to start the parsing

        Returns:
            the byte start index of the next multicast section
        '''
        
        end = offset+2
        res = struct.unpack('cc', mc[offset:end])
        present = int.from_bytes(res[0], "big")
        active = int.from_bytes(res[1], "big")
        
        presentList = [False] * 8
        activeList = [False] * 8
        for bit in range(0 , 8, 1):
            if present >> bit  & 1== 1:
                presentList[bit] = True
            if active >> bit  & 1== 1:
                activeList[bit] = True
                
        
        self.message["boardPresent"] = presentList
        self.message["boardActive"] = activeList

        return end

    def _parseAdb3l(self,message, offset):
        '''
        Parses the multicast message to obtain information about the ADB3L states

        Parameters:
            message( :obj of bytes) : the multicast binary message
            offset (int): the byte index into the message to start the parsing

        Returns:
            the byte start index of the next multicast section
        '''

        # ADB3L Values
        for i in range(0,8):
            s0 = {}
            s1 = {}
            s2 = {}
            s3 = {}

            res = struct.unpack('IIII', message[offset:offset+16])
            s0["power"] = int(res[0])
            s1["power"] = int(res[1])
            s2["power"] = int(res[2])
            s3["power"] = int(res[3])
            offset += 16

            res = struct.unpack('IIII', message[offset:offset+16])
            s0["offset"] = int(res[0])
            s1["offset"] = int(res[1])
            s2["offset"] = int(res[2])
            s3["offset"] = int(res[3])
            offset = offset + 16

            res = struct.unpack('III', message[offset:offset+12])
            # include 4 bytes zero padding
            offset += 16

            self.message["if_"+str(i+1)]["sampler0"]= s0
            self.message["if_"+str(i+1)]["sampler1"]= s1
            self.message["if_"+str(i+1)]["sampler2"]= s2
            self.message["if_"+str(i+1)]["sampler3"]= s3

            self.message["if_"+str(i+1)]["delayCorr"]= res

        return (offset)

    def _parseCore3h(self,message, offset):
        '''
        Parses the multicast message to obtain information about the CORE3H states

        Parameters:
            message( :obj of bytes) : the multicast binary message
            offset (int): the byte index into the message to start the parsing

        Returns:
            the byte start index of the next multicast section
        '''

        for i in range(0,8):
            filter1 = {}
            filter2 = {}
            timeValue = struct.unpack('I', message[offset:offset+4])
            self.message["if_"+str(i+1)]["vdifSeconds"]= struct.unpack('I', message[offset:offset+4])[0]
            offset = offset + 4

            self.message["if_"+str(i+1)]["vdifEpoch"] = struct.unpack('I', message[offset:offset+4])[0]
            offset = offset + 4

            self.message["if_"+str(i+1)]["ppsDelay"]= struct.unpack('I', message[offset:offset+4])[0]
            offset = offset + 4

            filter1["power"] = struct.unpack('I', message[offset:offset+4])[0]
            offset = offset + 4

            filter2["power"] = struct.unpack('I', message[offset:offset+4])[0]
            offset = offset + 4

            filter1["stats"] = []
            filter2["stats"] = []
            filter1["stats"] = struct.unpack('IIII', message[offset:offset+16])
            offset = offset + 16

            filter2["stats"] = struct.unpack('IIII', message[offset:offset+16])
            offset = offset + 16

            filter1["statsFrac"] = self._calcStatsPercentage(filter1["stats"])
            filter2["statsFrac"] = self._calcStatsPercentage(filter2["stats"])

            self.message["if_"+str(i+1)]["filter1"] = filter1
            self.message["if_"+str(i+1)]["filter2"] = filter2

        return(offset)

    

class DBBC3Multicast_DDC_U_126(DBBC3Multicast_DDC_U_125):
    pass
