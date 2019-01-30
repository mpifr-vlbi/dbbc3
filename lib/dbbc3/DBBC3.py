#!/usr/bin/env python

from DBBC3Config import DBBC3Config
import DBBC3Commandset as d3cs
import socket
import atexit
import re
import sys
import numpy as np
import types

from time import sleep

class DBBC3Exception(Exception):
	pass
class DBBC3ValueException(DBBC3Exception):
	pass
	
class DBBC3(object):

	# constants
	NUMSAMPLERS = 4

	def __initOld__(self, host, port, timeout=120, verbose=False):

                self.config = DBBC3Config()
		self.socket = None
		self.timeout = timeout
		self.lastCmdState = -1
		self.verbose = verbose
		atexit.register(self.disconnect)
		self.lastCommand = ""
		self.lastResponse = ""

                self.config.setNumCoreBoards(4)
		self.config.host = host
		self.config.port = port
                print self.config.coreBoards


		
        def __init__(self, dbbc3Config):

            self.config = dbbc3Config
            self.socket = None

            self.initCommandSet(mode="OCT_D")

        def initCommandSet(self, mode="", version=""):
            
            if (mode=="OCT_D"):
                cmd = d3cs.DBBC3CommandsetOCTD(self)
            else:
                cmd = d3cs.DBBC3Commandset(self)

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
                
		

# validation methods


	def getBstatAsymmetry(self,boardNum):
		'''
		Obtains the bit statistics and calculates the asymmetry of the low against the 
		high states.
		'''

		allStats = self.core3_bstat(boardNum)
		
		percs = []
		for samplerNum in range(self.NUMSAMPLERS):
			bstats = allStats[samplerNum]
			
			# Checking lower against upper half
			percs.append( abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3])))

		return allStats, percs

		
	def readCore3Register(self, boardNum, regNum):
		ret = dbbc3.sendCommand("core3h=%d,regread core3 %d" % (boardNum, regNum))
		lines = ret.split("\n")
		fields = lines[2].split("/")
		return int(fields[2].strip())


		

# end of class
OK = "\033[1;32mOK\033[0m"
INFO = "\033[1;34mINFO\033[0m"
WARN = "\033[1;35mWARN\033[0m"
ERROR = "\033[1;31mERROR\033[0m"
RESOLUTION = "\033[1;34mRESOLUTION\033[0m"



		
def report(level, message, resolutionMsg = "", exit=False):
	
	print("[%s] %s" % (level, message))
	if resolutionMsg != "":
		print "[%s] \033[1;34m%s\033[0m" % (RESOLUTION, resolutionMsg)

	if exit:
		sys.exit(1)

def validateIFLevel(board):
	
	print "\n=== Checking IF power level on core board %s" % board.upper()

	errorCount = 0
	ret = dbbc3.dbbcif(board)


	pattern = re.compile("dbbcif%s/\s(\d),(\d+),(.+),(\d),(\d+),(\d+)"%(board))

	match = pattern.match(ret)
	if match:

		input = int(match.group(1))
		gain = int(match.group(2))
		mode = match.group(3)
		filter = int(match.group(4))
		count = int(match.group(5))
		target = int(match.group(6))

		if abs(target -count) > 1000:
			msg = "Check and adjust IF input power levels (should be @ -11dBm)"
			report(ERROR, "IF power not on target value. Should be close to %d is %d" % (target, count), msg, exit=True)
			errorCount +=1
		if input != 2:
			report(ERROR, "Wrong if input setting. Is %d, should be 2 to enable downconversion" % input, exit=True)
			errorCount +=1
		if mode != "agc":
			report(ERROR, "Automatic gain control is disabled", exit=True)
			errorCount +=1
		if gain < 20:
			report(WARN, "IF input power is too low. The gain should be in the range 20-40, but is %d" % (gain))
			errorCount +=1
		if  gain > 40:
			report(WARN, "IF input power is too high. The gain should be in the range 20-40, but is %d" % (gain))
			errorCount +=1
	if errorCount == 0:
		report(OK, "count = %d" % (count))

def validateSamplerPhases():
	print "\n=== Checking sampler phases"

	if (dbbc3.checkphase()):
		report(OK, "OK")
	else:
		msg = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
		msg += "If the problem persists retry restart up to 5 times.\n"
		msg += "If the problem persists check your 10MHz power level.\n"
		msg += "If the problem persists do a full hardware restart."

		report(ERROR, dbbc3.lastResponse, msg, exit=True)

def validateSamplerPower(boardNum):

	errors = 0
	print "\n ===Checking sampler gains for board %s" % (dbbc3.getBoardName(boardNum))

	pow= dbbc3.core3_power(boardNum)
	if pow is None:
		report(ERROR, dbbc3.lastResponse, exit=True)

	mean = np.mean(pow)
	if (mean == 0):
		resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "If the problem persists do a full hardware restart."

		report(ERROR, "Sampler powers are 0 for board %s" % dbbc3.getBoardName(boardNum), resolv, exit=True)
	#if self.verbose:
	#	print "power values=%s mean=%f" % (str(pow), mean)

	for power in pow:
		dev = abs(1 - power/mean)
		if dev > 0.2:
			msg = "Large differences (>20%%) in sampler powers for board=%s. %s %f%%" % (dbbc3.getBoardName(boardNum), str(pow), dev*100)
			resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
			resolv += "If the problem persists retry restart up to 5 times.\n"
			resolv += "If the problem persists do a full hardware restart."
			report(ERROR, msg , resolv)
			errors += 1
		elif dev > 0.05:
			msg = "Large differences (>5%%) in sampler powers for board=%s. %s %f%%" % (dbbc3.getBoardName(boardNum), str(pow), dev*100)
			resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
			resolv += "If the problem persists retry restart up to 5 times.\n"
			resolv += "Possibly do a gain calibration (cal_delay=boardNum). Consult the documentation"
			report(WARN, msg , resolv)
			errors += 1

	if errors == 0:
		report(OK,  "sampler powers = %s" % (pow))
		


def validateSamplerOffsets(boardNum):
	print "\n===Checking sampler offsets for board %s" % (dbbc3.getBoardName(boardNum))

	errorCount = 0

	bstats = dbbc3.core3_bstat(boardNum)
	if bstats is None:
		report (ERROR, dbbc3.lastResponse, exit=True)


	for samplerNum in range(dbbc3.NUMSAMPLERS):
		#print bstats[0]+bstats[1], bstats[2]+bstats[3], 1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3])

		# Checking lower against upper half
		dev = abs(1 - float(bstats[samplerNum][0]+bstats[samplerNum][1]) / float(bstats[samplerNum][2]+bstats[samplerNum][3]))
		if dev > 0.10:
			errorCount += 1
			msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (dbbc3.getBoardName(boardNum), samplerNum, str(bstats[samplerNum]), dev*100) 
			resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
			resolv += "If the problem persists retry restart up to 5 times.\n"
			resolv += "If the problem persists do a full hardware restart."

			report(ERROR, msg, resolv, exit=True)
		if dev > 0.05:
			errorCount += 1
			msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (dbbc3.getBoardName(boardNum), samplerNum, bstats[samplerNum], dev*100)  
			resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
			resolv += "If the problem persists retry restart up to 5 times.\n"
			resolv += "If the problem persists do a full hardware restart."
		
			report(WARN, msg, resolv, exit=False)

	if errorCount == 0:
		report(OK, "Asymmetry = %f%%" % dev)


def reportLock(board, value):
	
	error = 0 
	if (value == 1): 
                report(OK, "Locked") 
        elif (value==0):    
                report(ERROR, "Synthesizer for board %s is not locked" % board, "Check if 10MHz is connected", exit=False)  
		error = 1
        else:    
                report(ERROR, "State of synthesizer for board %s cannot be determined" % board, "Check your hardware", exit=False)
		error = 1
	return error
	

def validateSynthesizerLocks():
	synth1 = dbbc3.getSynthLock(1)
	synth2 = dbbc3.getSynthLock(2)

	error = 0

	print "\n===Checking synthesizer lock state of board A"
	error += reportLock("A", synth1[0])

	print "\n===Checking synthesizer lock state of board B"
	error += reportLock("A", synth1[1])

	print "\n===Checking synthesizer lock state of board C"
	error += reportLock("A", synth2[0])

	print "\n===Checking synthesizer lock state of board D"
	error += reportLock("A", synth2[1])

	if error > 0:
		sys.exit(1)

def validateSynthesizerFreq(synthNum, targetFreqMHz):

	freq = dbbc3.getSynthFreq(synthNum)

	print "\n===Checking frequency of synthesizer %d" % (synthNum)
	if freq != targetFreqMHz:
		msg = "Synthesizer %d is tuned to %d MHz but should be %d MHz"
		resolv = "Check the tuning frequencies in the dbbc3 config file"
		report (ERROR, msg, resolv, exit=true)
	else:
		report(OK, "Freq=%d MHz" % freq)
	



if __name__ == "__main__":

            
    config = DBBC3Config()

    config.numCoreBoards = 4
    config.host="192.168.0.60"
    dbbc3 = DBBC3(config)


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


