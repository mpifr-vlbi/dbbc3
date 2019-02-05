############################################################################################
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
############################################################################################

from DBBC3Config import DBBC3Config
import DBBC3Commandset as d3cs
import socket
import atexit
import re
import sys

from time import sleep

class DBBC3Exception(Exception):
	pass
class DBBC3ValueException(DBBC3Exception):
	pass
	
class DBBC3(object):

        def __init__(self, dbbc3Config, mode="", version=""):

            self.config = dbbc3Config
            self.socket = None

            # attach command set
            d3cs.DBBC3Commandset(self, mode, version)

            
	def connect(self, timeout=120):

            try:
                self.socket = socket.create_connection((self.config.host, self.config.port), timeout)
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
			rv = self.socket.send(command + "\0")
		except:
			raise DBBC3Exception("An error in the communication to %s has occured" % (self.config.host))
		
		if rv <= 0:
			raise DBBC3Exception("An error in the communication to %s has occured" % (self.config.host))

		self.lastCommand = command
		self.lastResponse = self.socket.recv(1024)	
		return(self.lastResponse)

	
	def getBoardName(self, boardNum):
		return(self.config.coreBoards[boardNum-1])

        def _boardToChar(self, board):
            '''
            board: board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns the core board identifier as uppercase char e.g. A
            '''
            board = (str(board)).upper()

            # if board was given as number fetch the correct board letter
            if board.isdigit():
                if ((int(board) < 0) or (int(board) > self.config.numCoreBoards)):
                    raise DBBC3ValueException("Core board must be within %s" % (self.config.coreBoards))
                board = self.config.coreBoards[int(board)]
            elif board.isalpha():
                if board not in (self.config.coreBoards):
                    raise DBBC3ValueException("Core board must be within %s" % (self.config.coreBoards))

            return(board)

        def _boardToDigit(self, board):
            '''
            board: board identifier; can be numeric e.g. 0, or char e.g. 'A'
            Returns the core board identifier as integer (starting at 0 for board A)
            '''
            board = (str(board)).upper()

            # if board was given as number fetch the correct board letter
            if board.isdigit():
                if ((int(board) < 0) or (int(board) > self.config.numCoreBoards)):
                    raise DBBC3ValueException("Core board must be within %s" % (self.config.coreBoards))
                board = int(board)
            elif board.isalpha():
                if board not in (self.config.coreBoards):
                    raise DBBC3ValueException("Core board must be within %s" % (self.config.coreBoards))
                board = ord(board) - 65

            return(board)
		

if __name__ == "__main__":

            
    config = DBBC3Config()

    config.numCoreBoards = 4
    config.host="192.168.0.60"
    dbbc3 = DBBC3(config, mode="OCT_D", version="")


    dbbc3.connect()

    print dbbc3.time()
    print dbbc3.core3_power(0)
    print dbbc3.core3_power(1)
    print dbbc3.core3_power(2)
    print dbbc3.core3_power(3)

    print dbbc3.core3_bstat(0)
    print dbbc3.core3_bstat(1)
    print dbbc3.core3_bstat(2)
    print dbbc3.core3_bstat(3)

    print dbbc3.dbbcif(0)
    print dbbc3.dbbcif(1)
    print dbbc3.dbbcif(2)
    print dbbc3.dbbcif('d')

    print dbbc3.synthLock(0)
    print dbbc3.synthLock(1)
    print dbbc3.synthLock(2)
    print dbbc3.synthLock(3)

    print dbbc3.synthFreq(0)
    print dbbc3.synthFreq(1)
    print dbbc3.synthFreq(2)
    print dbbc3.synthFreq(3)

    ret =  dbbc3.checkphase()
    if not ret:
        print dbbc3.lastResponse


