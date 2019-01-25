#!/usr/bin/env python

import socket
import atexit
import re
import sys
import numpy as np

from time import sleep

class DBBC3Exception(Exception):
	pass
	
class DBBC3():

	# constants
	NUMSAMPLERS = 4

	def __init__(self, host, port, timeout=120, verbose=False):

		self.host = host
		self.port = port
		self.socket = None
		self.timeout = timeout
		self.lastCmdState = -1
		self.verbose = verbose
		atexit.register(self.disconnect)
		self.boards = ["A","B","C","D"]
		self.lastCommand = ""
		self.lastResponse = ""


		
	def connect(self):

		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.settimeout(self.timeout) 
		try:
			self.socket.connect((self.host, self.port))
		except:
			raise DBBC3Exception("Failed to connect to %s on port %d." % (self.host, self.port))

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
			raise DBBC3Exception("An error in the communication to %s has occured" % (self.host))
		
		if rv <= 0:
			raise DBBC3Exception("An error in the communication to %s has occured" % (self.host))

		self.lastCommand = command
		self.lastResponse = self.socket.recv(1024)	
		return(self.lastResponse)

#        def receive(self):
#                ret = self.socket.recv(1024)


	#def send(self, command):
#
		##self.socket.settimeout(0.0000000000000000000001)
		#try:
			#rv = self.socket.send(command + "\0")
		#except:
			#raise DBBC3Exception("An error in the communication to %s has occured" % (self.host))
	#	
		#if rv <= 0:
			#raise DBBC3Exception("An error in the communication to %s has occured" % (self.host))
#
		#self.lastReceive = self.socket.recv(1024)	


	
	def getBoardName(self, boardNum):
		return(self.boards[boardNum-1])
		

# Convenience functions

        def dbbcif(self, board):
               
                return (self.sendCommand("dbbcif%s" % (board)))



	def setTap2Filter(self, boardNum, filterFile, scaling=1):
		'''
		Sets the second tap filter when in OCT mode
		'''

		return self.sendCommand("tap2=%d,%s,%d" % (boardNum, filterFile,scaling))

	def setTapFilter(self, boardNum, filterFile, scaling=1):
		''' 
                Sets the first tap filter when in OCT mode 
                ''' 

		return self.sendCommand("tap=%d,%s,%d" % (boardNum, filterFile,scaling))

	def enableloop(self):
		return self.sendCommand("enableloop")

	def disableloop(self):
		return self.sendCommand("disableloop")

	def enablecal(self, threshold="on", gain="off", offset="off"):
		return self.sendCommand("enablecal=%s,%s,%s" % (threshold,gain,offset))

	def getSynthFreq(self, synthNum):

		freq = -1
		ret = self.sendCommand("synth=%d,cw" % synthNum)

		lines = ret.split("\n")
		for line in lines:
			if "MHz" in line:
				tok = line.split(" ")
				freq = int(tok[1]) * 2

		return(freq)


	def getSynthLock(self, synthNum):
		'''
		Gets the lock state of the 2 synthesizer sources of the given synthesizer number.
		A state of 1 indicates lock
		A state of 0 indicates unlock
		A state of -1 indicates an error obtaining the lock state
		
		Returns: an array holding the state 
		'''
		locked = [-1,-1]
		ret = self.sendCommand("synth=%d,lock" % synthNum)
		
		lines = ret.split("\n")
		for line in lines:
			if line.startswith("S1 not locked"):
				locked[0]=0
			elif line.startswith("S1 locked"):
				locked[0]=1
			if line.startswith("S2 not locked"):
				locked[1]=0
			elif line.startswith("S2 locked"):
				locked[1]=1

		 
		return locked
	

	def core3_bstat(self, boardNum):
		'''
		Obtains the bit statistics for all samplers of the given board
		Returns a 2D array containing the 4 stats for all 4 samplers
		Returns None if the core board is not connected
		'''

		sampler = []
		for samplerNum in range(self.NUMSAMPLERS):
                        bstats = []
                        ret = self.sendCommand("core3h=%s,core3_bstat %d" % (boardNum,samplerNum))
			if "not connected" in ret:
				return(None)

			# evaluate the registers that contain the statistics
                        bstats.append(self.readCore3Register(boardNum, 5))
                        bstats.append(self.readCore3Register(boardNum, 6))
                        bstats.append(self.readCore3Register(boardNum, 7))
                        bstats.append(self.readCore3Register(boardNum, 8))
			sampler.append(bstats)

		return (sampler)

	def core3_power(self, boardNum):
		''' 
		Obtains the gains of all 4 samplers of the given board

		Returns: the array of the sampler gains
		Returns: None in case the core3 board is not connected
		'''
		
		pow = []
		ret = self.sendCommand("core3h=%d,core3_power" % (boardNum))

		if "not connected" in ret:
			return None

		pow.append(self.readCore3Register(boardNum, 5))
		pow.append(self.readCore3Register(boardNum, 6))
		pow.append(self.readCore3Register(boardNum, 7))
		pow.append(self.readCore3Register(boardNum, 8))

		return(pow)

# validation methods

	def checkphase(self):
		''' 
		Checks that all samplers are in sync
	
		Returns True if all samplers are in sync
		Returns False otherwise (get output with lastResponse()
		'''
		ret = dbbc3.sendCommand("checkphase")

		if "out of sync" in ret:
			return(False)
		else:
			return(True)

	def getBstatAsymmetry(self,boardNum):
		'''
		Obtains the bit statistics and calculates the asymmetry of the low against the 
		high states.
		'''

		allStats = self.core3_bstat(boardNum)
		
		percs = []
		for samplerNum in range(dbbc3.NUMSAMPLERS):
			bstats = allStats[samplerNum]
			
			# Checking lower against upper half
			percs.append( abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3])))

		return allStats, percs

		
	def cmd_core3_bstat(self, boardNum):

		errorCount = 0
		for samplerNum in range(4):
			bstats = []
			ret = dbbc3.sendCommand("core3h=%s,core3_bstat %d" % (boardNum,samplerNum))

			bstats.append(self.readCore3Register(boardNum, 5))
			bstats.append(self.readCore3Register(boardNum, 6))
			bstats.append(self.readCore3Register(boardNum, 7))
			bstats.append(self.readCore3Register(boardNum, 8))

			if self.verbose:
				print bstats

			#print bstats[0]+bstats[1], bstats[2]+bstats[3], 1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3])
			# Checking lower against upper half
			dev = abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3]))
			if dev > 0.10:
				errorCount += 1
				self.report(self.ERROR, "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (self.boards[boardNum-1], samplerNum, str(bstats), dev*100), "Restart the control software (skip firmware loading)", exit=True)
			if dev > 0.05:
				errorCount += 1
				self.report(self.WARN, "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s %f%%" % (self.boards[boardNum-1], samplerNum, str(bstats), dev*100), "Check power levels or try recalibrating")

		if errorCount == 0:
			self.report(self.INFO, "OK")
			


		


	def readCore3Register(self, boardNum, regNum):
		ret = dbbc3.sendCommand("core3h=%d,regread core3 %d" % (boardNum, regNum))
		lines = ret.split("\n")
		fields = lines[2].split("/")
		return int(fields[2].strip())


		

	def cmd_time(self):
		times = []

		ret = dbbc3.send("time")
		
		#2019-01-20T21:19:12
		pattern = re.compile("(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})")
		lines = ret.split("\r")
		for line in lines:
			line.strip()
			print line
			match = pattern.match(line)
			if match:
				year = match.group(1)
				month = match.group(2)
				day = match.group(3)
				hour = match.group(4)
				min = match.group(5)
				sec = match.group(6)
				print year


		
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

		dbbc3 = DBBC3("192.168.0.60", 4000, verbose=False)
#	try:
		dbbc3.connect()

		print "=== Disabling calibration loop"
		dbbc3.disableloop()
	
		validateSynthesizerLocks()
		validateSynthesizerFreq(1, 9048)
		validateSynthesizerFreq(2, 9048)

		validateIFLevel('a')
		validateIFLevel('b')
		validateIFLevel('c')
		validateIFLevel('d')

		validateSamplerPhases()

#		validateSamplerPower(1)
#		validateSamplerPower(2)
		validateSamplerPower(3)
		validateSamplerPower(4)

#		validateSamplerOffsets(1)
#		validateSamplerOffsets(2)
		validateSamplerOffsets(3)
		validateSamplerOffsets(4)

		
		# load tap filters (extra script)
		response = raw_input("Do you want to set the tap filters now? [y/n]")
		if response == "y":
#			print "=== Loading tap filters for board A"
#			dbbc3.setTapFilter(1,"2000-4000_floating.flt")
#			dbbc3.setTap2Filter(1,"0-2000_floating.flt")
#			print "=== Loading tap filters for board B"
#			dbbc3.setTapFilter(2,"2000-4000_floating.flt")
#			dbbc3.setTap2Filter(2,"0-2000_floating.flt")
			print "=== Loading tap filters for board C"
			dbbc3.setTapFilter(3,"2000-4000_floating.flt")
			dbbc3.setTap2Filter(3,"0-2000_floating.flt")
			print "=== Loading tap filters for board D"
			dbbc3.setTapFilter(4,"2000-4000_floating.flt")
			dbbc3.setTap2Filter(4,"0-2000_floating.flt")
		else:	
			sys.exit(0)

		print "=== Setting up calibration loop"
		dbbc3.enablecal()
		print "=== Enabling calibration loop"
		dbbc3.enableloop()

		print "=== Waiting for 1 minute to allow adjusting the power levels"
		sleep(60)
		
		print "=== Now re-checking the bit statistics (should be proper 2-bit)"
#		validateSamplerOffsets(1)
#		validateSamplerOffsets(2)
		validateSamplerOffsets(3)
		validateSamplerOffsets(4)

		print "=== Setting up calibration loop"
		dbbc3.enablecal()
		print "=== Enabling calibration loop"
		dbbc3.enableloop()
		
		dbbc3.disconnect()
		print "=== Done"
#	except Exception as e:
#		print e.message
#		dbbc3.disconnect()
		

	
