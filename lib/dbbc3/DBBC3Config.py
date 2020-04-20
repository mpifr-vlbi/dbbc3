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

    def __init__(self, mode, version):
        '''
        Constructor
        '''
        self.mode = mode
        self.modeVersion = version

        self.coreBoards = []
        self.host = ""
        self.port = 0

        # number of samplers per core3h board
        self.numSamplers = 4

        # the maximum total number of BBCs
        self.maxTotalBBCs = 128

        # the number of core boards configured in the current system (will be set by user)
        self._numCoreBoards = 0

        # highest tuning frequency for a BBC
        self.maxBBFreq = 4096.0

        # maximum number of output formats allowed for the core3h_start command
        self.numCore3hOutputs = 4

        # specific parameters depending on the DBBC3 mode
        if (mode == "DDC_U"):
            self._setupDDC_U()
        elif (mode == "DDC_V"):
            self._setupDDC_V()
        elif (mode == "DDC_L"):
            self._setupDDC_L()

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

    def _setupDDC_U(self):
        '''
        Confugration settings specific to the DDC_U mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 16

    def _setupDDC_L(self):
        '''
        Confugration settings specific to the DDC_L mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8
        
    def _setupDDC_V(self):
        '''
        Confugration settings specific to the DDC_V mode
        '''
        # the maximum number of BBCs per core board
        self.maxBoardBBCs = 8
        
        


if __name__ == "__main__":
    config = DBBC3Config()

    config.numCoreBoards = 4
    
