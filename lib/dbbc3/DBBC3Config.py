
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
    
