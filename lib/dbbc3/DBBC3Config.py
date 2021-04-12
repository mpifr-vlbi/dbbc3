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
__copyright__ = "2019, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

class DBBC3Config(object):
    '''
    Class for storing and handling of the DBBC3 configuration
    '''

    def __init__(self, version):
        '''
        Constructor
        '''
        # version dict (see DBBC3Commandset version() method for structure)
        self.cmdsetVersion = version

        self.mode = self.cmdsetVersion["mode"]

        self.coreBoards = []
        self.host = ""
        self.port = 0

        # number of samplers per core3h board
        self.numSamplers = 4

        # the number of core boards configured in the current system (will be set by user)
        self._numCoreBoards = 0

        # the maximum total number of BBCs (depending on mode and number of boards)
        self.maxTotalBBCs = -1

        # highest tuning frequency for a BBC
        self.maxBBFreq = 4096.0

        # maximum number of output formats allowed for the core3h_start command
        self.numCore3hOutputs = 4

        # multicast support
        self.enableMulticast = False

        # specific parameters depending on the DBBC3 mode
        if (self.cmdsetVersion["mode"] == "DDC_U"):
            self._setupDDC_U()
        elif (self.cmdsetVersion["mode"] == "DDC_V"):
            self._setupDDC_V()
        elif (self.cmdsetVersion["mode"] == "DDC_L"):
            self._setupDDC_L()
        elif (self.cmdsetVersion["mode"] == "OCT_D"):
            self._setupOCT_D()
        elif (self.cmdsetVersion["mode"] == "OCT_S"):
            self._setupOCT_S()


#    @property
#    def maxBoardBBCs(self):
#        return self._maxBoardBBCs
    @property
    def numCoreBoards(self):
        """
        The number of CORE3H boards installed in the DBBC3 
        """
        return self._numCoreBoards

#    @maxBoardBBCs.setter
#    def maxBoardBBCs(self, maxBoardBBCs):
#        self._maxBoardBBCs = maxBoardBBCs

    @numCoreBoards.setter
    def numCoreBoards(self, numCoreBoards):
        self._numCoreBoards = numCoreBoards

        self.coreBoards = []
        for i in range(numCoreBoards):
            self.coreBoards.append(chr(65 +i))

        self.maxTotalBBCs = numCoreBoards * self.maxBoardBBCs

    def _setupDDC_U(self):
        '''
        Configuration settings specific to the DDC_U mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 16

        if (self.cmdsetVersion["majorVersion"] >= 125):
            self.enableMulticast = True

    def _setupDDC_L(self):
        '''
        Configuration settings specific to the DDC_L mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8
        
    def _setupDDC_V(self):
        '''
        Configuration settings specific to the DDC_V mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8

    def _setupOCT_D(self):
        '''
        Configuration settings specific to the OCT_D mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8

    def _setupOCT_S(self):
        '''
        Configuration settings specific to the OCT_S mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8

        

if __name__ == "__main__":
    config = DBBC3Config()

    config.numCoreBoards = 4
    
