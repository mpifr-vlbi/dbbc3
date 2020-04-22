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
  module for monitoring and control of the DBBC3 VLBI backend
'''

__author__ = "Helge Rottmann"
__copyright__ = "2019, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottman[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"


from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Commandset import DBBC3Commandset
from dbbc3.DBBC3Exception import DBBC3Exception
import socket
import atexit
import re
import sys
from time import sleep


        
class DBBC3(object):
        ''' 
        Main class of the DBBC3 module.
        '''
        
        dataFormats = ["vdif","raw"]    # valid output data formats
    
        core3hModes = ["independent","half_merged", "merged", "pfb"] # valid core3h modes


        def __init__(self, host, port=4000, numBoards=8, mode="", version=""):
            ''' Constructor '''

            self.socket = None
            self.mode = mode
            self.modeVersion = version

            self.config = DBBC3Config(mode, version)
            self.config.host = host
            self.config.port = port
            self.config.numCoreBoards = numBoards

            self._connect(host,port)
            # attach command set
            DBBC3Commandset(self, mode, version)

            self._validateVersion()


            self.lastCommand = ""
            self.lastResponse = ""

        def _connect (self, host, port, timeout=120):
            '''
            open a socket connection to the DBBC3 control software
            
            timeout: the connection timeout in seconds (default 120)
            '''
            try:
                self.socket = socket.create_connection((host, port), timeout)
            except:
                raise DBBC3Exception("Failed to connect to %s on port %d." % (self.config.host, self.config.port))

        def disconnect(self):
            if self.socket:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket = None


        def sendCommand(self, command):
                '''
                Method for sending generic commands to the DBBC3
                
                Returns the response
                '''

                try:
                        #rv = self.socket.send(command + "\0")
                        rv = self.socket.send((command + "\0").encode())
                except:
                        raise DBBC3Exception("An error in the communication to %s has occured" % (self.config.host))
                
                if rv <= 0:
                        raise DBBC3Exception("An error in the communication to %s has occured" % (self.config.host))

                self.lastCommand = command
                self.lastResponse = self.socket.recv(2048).decode('utf-8')
                return(self.lastResponse)


        def _validateVersion(self):
            retVersion = self.version()

            if (retVersion["mode"] != self.mode):
                raise Exception("The requested mode (%s) does not match the loaded firmware (%s)" % (self.mode, retVersion["mode"]))

            if (self.modeVersion != ""):
                if (retVersion["majorVersion"] != self.modeVersion):
                    raise Exception("The requested version (%s) does not match the version of the loaded firmware (%s)" % (self.modeVersion, retVersion["majorVersion"]))


        def _validateMAC(self, mac):
            if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
                raise ValueError("Invalid MAC address %s" % (mac))

        def _validateDataFormat(self, form):
            if form not in DBBC3.dataFormats:
                raise ValueError("Invalid data format requested %s. Must be one of %s" % (form, DBBC3.dataFormats))

        def _validateCore3hMode(self, mode):
            
            if mode not in DBBC3.core3hModes:
                raise ValueError("Invalid Core3H mode %s. Must be one of %s" %(mode, DBBC3.core3hModes))

        def _validateSamplerNum (self, sampler):
            if not isinstance(sampler, int):
                raise ValueError("Sampler number must be an integer.")

            if sampler < 0:
                raise ValueError("Sampler number must be >0.")

            if sampler > self.config.numSamplers:
                raise ValueError("Sampler number must be in the range: 0-%d" % (self.config.numSamplers))

        def _valueToHex(self, value):

            if isinstance(value, str):
                if not value.startswith("0x"):
                    raise ValueError("")
                hexVal = value

            else:
                hexVal = hex(value)

            return (hexVal)
        
        def _validateBBC(self, bbc):
            ''' 
            Checks whether the specified bbc number is valid
            '''

            if bbc not in range(1, self.config.maxTotalBBCs+1):
                raise ValueError("BBC must be in the range 1-%d" % (self.config.maxTotalBBCs))

        def _validateBBCFreq(self, freq):
            ''' 
            Checks whether the specified bbc frequency is valid
            '''

            if (freq < 0.0 or freq > self.config.maxBBFreq):
                raise ValueError("BBC freq must be in the range 0-%f" % (self.config.maxBBFreq))

        def _validateTPInt(self, tpint):
            '''
            Checks whether the specified tpint is valid
            '''

            if (tpint < 1 or tpint > 60):
                raise ValueError("tpint value must be in the range 1-60")

        def _validateOnOff(self, mode):
            if (mode not in ["on", "off"]):
                raise ValueError("Mode must be either on or off")

        def boardToChar(self, board):
            '''
            Converts the core board number (starting at 0) into a board ID (e.g. A,B,C....)
            board: board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns the core board identifier as uppercase char e.g. A
            '''
            board = (str(board)).upper()

            # if board was given as number fetch the correct board letter
            if board.isdigit():
                if ((int(board) < 0) or (int(board) > self.config.numCoreBoards)):
                    raise ValueError("Core board must be within %s" % (self.config.coreBoards))
                board = self.config.coreBoards[int(board)]
            elif board.isalpha():
                if board not in (self.config.coreBoards):
                    raise ValueError("Core board must be within %s" % (self.config.coreBoards))

            return(board)

        def boardToDigit(self, board):
            '''
            Converts the core board ID (e.g. A) into the board number (starting at 0)
            board: board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns the core board identifier as integer (starting at 0 for board A)
            '''
            board = (str(board)).upper()

            # if board was given as number fetch the correct board letter
            if board.isdigit():
                if ((int(board) < 0) or (int(board) >= self.config.numCoreBoards)):
                    raise ValueError("Core board must be within %s" % (self.config.coreBoards))
                board = int(board)
            elif board.isalpha():
                if board not in (self.config.coreBoards):
                    raise ValueError("Core board must be within %s" % (self.config.coreBoards))
                board = ord(board) - 65

            return(board)
                

if __name__ == "__main__":

            
    dbbc3 = DBBC3(host="134.104.30.223", mode="DDC_V")
    
    print (dbbc3.dsc_bstat(0,1))

    #print( dbbc3.time())
    #print( dbbc3.core3_power(0))
    #print( dbbc3.core3_power(1))
    #print( dbbc3.core3_power(2))
    #print( dbbc3.core3_power(3))
#
#    print( dbbc3.core3_bstat(0))
#    print( dbbc3.core3_bstat(1))
#    print( dbbc3.core3_bstat(2))
#    print( dbbc3.core3_bstat(3))
#
#    print( dbbc3.dbbcif(0))
#    print( dbbc3.dbbcif(1))
#    print( dbbc3.dbbcif(2))
#    print( dbbc3.dbbcif('d'))
#
#    print( dbbc3.synthLock(0))
#    print( dbbc3.synthLock(1))
#    print( dbbc3.synthLock(2))
#    print( dbbc3.synthLock(3))
#
#    print( dbbc3.synthFreq(0))
#    print( dbbc3.synthFreq(1))
#    print( dbbc3.synthFreq(2))
#    print( dbbc3.synthFreq(3))
#
#    ret =  dbbc3.checkphase()
#    if not ret:
#        print( dbbc3.lastResponse)


