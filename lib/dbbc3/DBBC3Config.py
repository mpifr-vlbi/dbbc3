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
  This module is part of the DBBC3 package. It contains code for handling the DBBC3 configuration

'''

__author__ = "Helge Rottmann"
__copyright__ = "2022, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

class DBBC3Config(object):
    '''
    Class for storing and handling of the DBBC3 configuration. 

    Args:
        version (dict): the version dict as returned by :py:func:`dbbc3.DBBC3Commandset.DBBC3CommandsetDefault.version`
    '''

    def __init__(self, version):
        '''
        Constructor
        '''
        # version dict (see DBBC3Commandset version() method for structure)
        self._cmdsetVersion = version
        self._mode = self._cmdsetVersion["mode"]
        self._coreBoards = []
        self._host = ""
        self._port = 0

        # number of samplers per core3h board
        self._numSamplers = 4

        # the number of core boards configured in the current system 
        self._numCoreBoards = 0

        # the maximum total number of BBCs (depending on mode and number of boards)
        self._maxTotalBBCs = -1

        # highest tuning frequency for a BBC
        self._maxBBFreq = 4096.0

        # maximum number of output formats allowed for the core3h_start command
        self._numCore3hOutputs = 4

        # multicast support
        self._enableMulticast = False

        # specific parameters depending on the DBBC3 mode
        if (self._cmdsetVersion["mode"] == "DDC_U"):
            self._setupDDC_U()
        elif (self._cmdsetVersion["mode"] == "DDC_V"):
            self._setupDDC_V()
        elif (self._cmdsetVersion["mode"] == "DDC_L"):
            self._setupDDC_L()
        elif (self._cmdsetVersion["mode"] == "OCT_D"):
            self._setupOCT_D()
        elif (self._cmdsetVersion["mode"] == "OCT_S"):
            self._setupOCT_S()

    @property
    def host(self):
        """ str: the hostname or IP address of the DBBC3 system """
        return self._host 

    @host.setter
    def host(self, host):
        self_host = host

    @property
    def port(self):
        """ int: the port of the socket connection of the DBBC3 control software server """
        return self._port

    @port.setter
    def port(self, host):
        self_port = port

    @property
    def mode(self):
        """ str: the mode of the currently loaded control software """
        return self._mode

    @property
    def coreBoards(self):
        """ list: the list of core3H boards installed in the system """
        return self._coreBoards

    @property
    def cmdsetVersion(self):
        """ (dict): the dict containing the currently loaded control software version """
        return self._cmdsetVersion

    @property
    def numSamplers(self):
        """ int: The number of samplers for each of the Core3H boards """
        return self._numSamplers

    @property
    def maxTotalBBCs(self):
        """ int: The maximum total number of BBCs available for the DBBC3 (depending on mode and number of boards) """
        return self._maxTotalBBCs

    @property
    def maxBBFreq(self):
        """ float: The maximum tuning frequency possible for a BBC"""
        return self._maxBBFreq

    @property
    def maxBoardBBCs(self):
        """ int: The maximum number of BBCs per Core3H board (depending on mode) """
        return self._maxBoardBBCs

    @property
    def numCoreBoards(self):
        """ int: The number of CORE3H boards installed in the DBBC3 """
        return self._numCoreBoards

    @property
    def enableMulticast(self):
        """ boolean: True/False in case  multicast is enabled/disabled (depending on the mode)"""
        return self._enableMulticast

    @numCoreBoards.setter
    def numCoreBoards(self, numCoreBoards):
        self._numCoreBoards = numCoreBoards

        self._maxTotalBBCs = numCoreBoards * self.maxBoardBBCs
        for i in range(numCoreBoards):
            self._coreBoards.append(chr(65 +i))

        self._maxTotalBBCs = numCoreBoards * self._maxBoardBBCs

    def _setupDDC_U(self):
        '''
        Configuration settings specific to the DDC_U mode
        '''
        # the maximum number of BBCs per core board
        self._maxBoardBBCs = 16

        if (self._cmdsetVersion["majorVersion"] >= 125):
            self._enableMulticast = True

    def _setupDDC_L(self):
        '''
        Configuration settings specific to the DDC_L mode
        '''
        # the maximum number of BBCs per core board
        self._maxBoardBBCs = 8
        
    def _setupDDC_V(self):
        '''
        Configuration settings specific to the DDC_V mode
        '''
        # the maximum number of BBCs per core board
        self._maxBoardBBCs = 8

    def _setupOCT_D(self):
        '''
        Configuration settings specific to the OCT_D mode
        '''
        # the maximum number of BBCs per core board
        self._maxBoardBBCs = 8

    def _setupOCT_S(self):
        '''
        Configuration settings specific to the OCT_S mode
        '''
        # the maximum number of BBCs per core board
        self._maxBoardBBCs = 8

        

if __name__ == "__main__":
    config = DBBC3Config()

    config.numCoreBoards = 4
    
