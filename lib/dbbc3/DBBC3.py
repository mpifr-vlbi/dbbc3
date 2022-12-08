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
__copyright__ = "2021, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
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

        Upon instantiation a connection is made to the DBBC3 control software server. If a connection was successfully
        established the mode and version of the loaded control software is being queried and the appropriate command
        set is being attached to the class instance.

        Note:
            in case the optional arguments mode and/or majorVersion are given these values are comapred
            against the actual currently loaded mode and software version. An Exception is being raised
            if the values do not match.

        Args:
            host (str): the host name or IP address of the DBBC3
            port (int, optional): the port of the socket provided by the DBBC3 control software server (default: 4000)
            mode (str, optional): the expected mode of the DBBC3 (see note above)
            majorVersion (int, optional): the expected major version of the DBBC3 control software (see note above)
            timeout (int, optional): the timeout in seconds to set for the socket communication to the DBBC3 (default: None)
        '''
        
        dataFormats = ["vdif","raw"]    # valid output data formats
    
        core3hModes = ["independent","half_merged", "merged", "pfb"] # valid core3h modes

        @property 
        def config (self):
            ''' :py:class:`DBBC3Config`: the dbbc3 configuration '''
            return (self._config)

        @property 
        def lastCommand (self):
            ''' str: the last command that was sent to the DBBC3 '''
            return (self._lastCommand)

        @property 
        def lastResponse (self):
            'str: the last response received from the DBBC3'''
            return (self._lastResponse)

        @property 
        def timeout (self):
            'int: the socket timeout in seconds'''
            return (self._timeout)

        def __init__(self, host, port=4000,  mode=None, majorVersion=None, timeout=None):
            ''' 
            The constructor

            '''

            self.socket = None

            self._connect(host,port, timeout)

            # attach basic command set
            DBBC3Commandset(self)

            # obtain firmware version and validate
            retVersion = self.version()
            self._validateVersion(retVersion, mode, majorVersion)

            # update the configuration
            self._config = DBBC3Config(retVersion)
            self._config.host = host
            self._config.port = port
            # temporarily set the number of installed boards to maximum (will be determined below)
            self._config.numCoreBoards = 8

            # attach final command set
            DBBC3Commandset(self, retVersion)

            # determine number of enabled GComos (should be equal to number of installed core3h boards)
            self._config.numCoreBoards = self._getNumCoreBoards()

            self._timeout = timeout
            self._lastCommand = ""
            self._lastResponse = ""

        def _connect (self, host, port, timeout=None):
            '''
            Opens a socket connection to the DBBC3 control software
            
            If the optional timeout parameter is not set the socket connection will be
            be set to blocking 

            Args:
                host (str):  the host name or IP address of the dbbc3
                port (int):  the port to use for the socket connection
                timeout (int): the connection timeout in seconds (default: None)

            Raises:
                DBBC3Exception: in case the connection could not be established
            '''
            try:
                
                self.socket = socket.create_connection((host, port), 5)

                # DBBC3 socket issue: will establish formal connection without 
                # raising a timeout exception  even if
                # other clients are connected (for unknown reasons) 
                # workaround ist to send a dummy command to provoke the timeout

                self.sendCommand("version")
            
                if timeout:
                    self.socket.settimeout(timeout) 

            except socket.timeout:
                raise DBBC3Exception("Failed to connect to %s on port %d." % (host, port))

            self.socket.settimeout(None)

        def disconnect(self):
            """
            Close the socket connection to the DBBC3

            Returns:
                None
            """
            if self.socket:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket = None


        def sendCommand(self, command):
            '''
            Method for sending generic commands to the DBBC3

            Note:
                the response of the last sendCommand is always available through the lastResponse class property

            Args:
                command (str): the command to the DBBC3 control software server

            Returns:
                str: the response received from the DBBC3 control software

            Raises:
                DBBC3Exception: in case an error occured in the communication with the DBBC3 server
            
            '''

            rv = -1
            try:
                rv = self.socket.send((command + "\0").encode())
                self._lastCommand = command
                self._lastResponse = ""

                while True:
                    part = self.socket.recv(2048)
                    if not part or len(part) < 2048:
                        break
                    self._lastResponse += part.decode('utf-8')
                self._lastResponse += part.decode('utf-8')

            except Exception as e:
                raise DBBC3Exception("An error in the communication has occured")

            if rv <= 0:
                raise DBBC3Exception("An error in the communication has occured" )
            
            return(self._lastResponse)


        def _validateVersion(self, retVersion, mode, majorVersion):

            if (mode):
                if (retVersion["mode"] != mode):
                    raise Exception("The requested mode (%s) does not match the loaded firmware (%s)" % (mode, retVersion["mode"]))

            if (majorVersion):
                if (retVersion["majorVersion"] != majorVersion):
                    raise Exception("The requested version (%s) does not match the version of the loaded firmware (%s)" % (majorVersion, retVersion["majorVersion"]))


        def _validateMAC(self, mac):
            if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
                raise ValueError("Invalid MAC address %s" % (mac))

        def _validateDataFormat(self, form):
            if form not in DBBC3.dataFormats:
                raise ValueError("Invalid data format requested %s. Must be one of %s" % (form, DBBC3.dataFormats))

        def _validateCore3hMode(self, mode):
            '''
            Checks whether the specified core3h mode is valid.

            Raises:
                ValueError: in case the specified core3h mode is invalid
            '''
            
            if mode not in DBBC3.core3hModes:
                raise ValueError("envalid Core3H mode %s. Must be one of %s" %(mode, DBBC3.core3hModes))

        def _validateSamplerNum (self, sampler):
            '''
            Checks whether the specified sampler number is valid.

            Raises:
                ValueError: in case the specified sampler number is invalid
            '''
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

            Raises:
                ValueError: in case the specified bbc number is invalid
            '''

            if bbc not in range(1, self.config.maxTotalBBCs+1):
                raise ValueError("BBC must be in the range 1-%d" % (self.config.maxTotalBBCs))

        def _validateBBCFreq(self, freq):
            ''' 
            Checks whether the specified bbc frequency is valid

            Raises:
                ValueError: in case the specified bbc frequency is invalid
            '''

            if (freq < 0.0 or freq > self.config.maxBBFreq):
                raise ValueError("BBC freq must be in the range 0-%f" % (self.config.maxBBFreq))

        def _validateTPInt(self, tpint):
            '''
            Checks whether the specified tpint is valid

            Raises:
                ValueError: in case the specified tpint value is invalid
            '''

            if (tpint < 1 or tpint > 60):
                raise ValueError("tpint value must be in the range 1-60")

        def _getNumCoreBoards(self):
            '''
            Determines the number of active GComo units by issuing dbbcif commands
            Because the number of GComos must match the number of installed 
            core3h boards this method is used to determine the number of boards.

            Note: This does not catch cases where the core3h board is installed but
            disabled by a prefix of 30 in the configuration file.

            Returns:
                int: the number of core boards installed in the system
            '''

            for board in range(8):
                if not self.dbbcif(board):
                    return(board)

            return(8)

        def boardToChar(self, board):
            '''
            Converts the core board number (starting at 0) into a board ID (e.g. A,B,C....)

            Args:
                board (str or int): board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns:
                char: the core board identifier as uppercase char e.g. A
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

            Args:
                board (str or int): board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns:
                int: the core board identifier as integer (starting at 0 for board A)
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
#        print( dbbc3._lastResponse)


