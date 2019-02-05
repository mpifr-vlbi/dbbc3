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

class DBBC3Config(object):

    def __init__(self):
        self.coreBoards = []
	self.host = ""
        self.port = 4000	

        self._numCoreBoards = 0
        self.numSamplers = 4

    @property
    def numCoreBoards(self):
        return self._numCoreBoards

    @numCoreBoards.setter
    def numCoreBoards(self, numCoreBoards):
        self._numCoreBoards = numCoreBoards

        self.coreBoards = []
        for i in range(numCoreBoards):
            self.coreBoards.append(chr(65 +i))


if __name__ == "__main__":
    config = DBBC3Config()

    config.numCoreBoards = 4
    
