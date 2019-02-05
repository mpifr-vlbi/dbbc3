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

import re
import sys
import numpy as np


class DBBC3Validation(object):

    OK = "\033[1;32mOK\033[0m"
    INFO = "\033[1;34mINFO\033[0m"
    WARN = "\033[1;35mWARN\033[0m"
    ERROR = "\033[1;31mERROR\033[0m"
    RESOLUTION = "\033[1;34mRESOLUTION\033[0m"
    
    def __init__(self, dbbc3, ignoreErrors = False):
        self.dbbc3 = dbbc3
        self.ignoreErrors = ignoreErrors

    def setIgnoreErrors(ignoreErrors):
        self.ignoreErrors = ignoreErrors

    def report(self, level, message, resolutionMsg = "", exit=False):
        '''
        Default method for reporting the outcome of validation actions. 
        Should be overriding for customization
        '''
        
        print("[%s] %s" % (level, message))
        if resolutionMsg != "":
                print "[%s] \033[1;34m%s\033[0m" % (self.RESOLUTION, resolutionMsg)

        if exit:
            if (self.ignoreErrors):
                print "Continuing because ignoreErrors was enabled"
            else:
                sys.exit(1)

    def validateIFLevel(self, board, downConversion=True, agc=True):
        '''
        Performs various validations of the IF power settings as obtained from trhe dbbcif command
        1) IF power should be within 1000 counts of the target value
        2) The attenuation setting should be within 20-40
        3) AGC should be switched on (unless check is  disabled with the agc parameter)
        4) input should be set to 2 (unless check is disabled with the downConversion parameter)
        '''
        
        board = self.dbbc3._boardToChar(board)
        print "\n=== Checking IF power level on core board %s" % board.upper()


        errorCount = 0
        ret = self.dbbc3.dbbcif(board)

        if abs(ret['target'] - ret['count']) > 1000:
                msg = "Check and adjust IF input power levels (should be @ -11dBm)"
                self.report(self.ERROR, "IF power not on target value. Should be close to %d is %d" % (ret['target'], ret['count']), msg, exit=True)
                errorCount +=1
        if ret['input'] != 2 and downConversion==True:
                self.report(self.ERROR, "Wrong IF input setting. Is %d, should be 2 to enable downconversion" % ret['input'], exit=True)
                errorCount +=1
        if ret['mode'] != "agc" and agc==True:
                self.report(self.ERROR, "Automatic gain control is disabled", exit=True)
                errorCount +=1
        if ret['gain'] < 20:
                self.report(self.WARN, "IF input power is too low. The attenuation should be in the range 20-40, but is %d" % (ret['gain']))
                errorCount +=1
        if  ret['gain'] > 40:
                self.report(self.WARN, "IF input power is too high. The attenuation should be in the range 20-40, but is %d" % (ret['gain']))
                errorCount +=1
        if errorCount == 0:
            self.report(self.OK, "count = %d" % (ret['count']))

    def validateSamplerPhases(self):
        print "\n=== Checking sampler phases"

        if (self.dbbc3.checkphase()):
                self.report(self.OK, "OK")
        else:
                msg = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                msg += "If the problem persists retry restart up to 5 times.\n"
                msg += "If the problem persists check your 10MHz power level.\n"
                msg += "If the problem persists do a full hardware restart."

                self.report(self.ERROR, self.dbbc3.lastResponse, msg, exit=True)

    def validateSamplerPower(self, boardNum):

        errors = 0
        board = self.dbbc3._boardToChar(boardNum)
        print "\n ===Checking sampler gains for board %s" % (board)

        pow= self.dbbc3.core3_power(boardNum)
        if pow is None:
                self.report(self.ERROR, self.dbbc3.lastResponse, exit=True)

        mean = np.mean(pow)
        if (mean == 0):
                resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "If the problem persists do a full hardware restart."

                self.report(self.ERROR, "Sampler powers are 0 for board %s" % board, resolv, exit=True)
        #if self.verbose:
        #	print "power values=%s mean=%f" % (str(pow), mean)

        for power in pow:
                dev = abs(1 - power/mean)
                if dev > 0.2:
                        msg = "Large differences (>20%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), dev*100)
                        resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                        self.report(self.ERROR, msg , resolv)
                        errors += 1
                elif dev > 0.05:
                        msg = "Large differences (>5%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), dev*100)
                        resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "Possibly do a gain calibration (cal_delay=boardNum). Consult the documentation"
                        self.report(self.WARN, msg , resolv)
                        errors += 1

        if errors == 0:
                self.report(self.OK,  "sampler powers = %s" % (pow))
                


    def validateSamplerOffsets(self, boardNum):

        board = self.dbbc3._boardToChar(boardNum)
        print "\n===Checking sampler offsets for board %s" % (board)

        errorCount = 0

        bstats = self.dbbc3.core3_bstat(boardNum)
        if bstats is None:
                self.report (self.ERROR, self.dbbc3.lastResponse, exit=True)


        for samplerNum in range(self.dbbc3.config.numSamplers):
                #print bstats[0]+bstats[1], bstats[2]+bstats[3], 1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3])

                # Checking lower against upper half
                dev = abs(1 - float(bstats[samplerNum][0]+bstats[samplerNum][1]) / float(bstats[samplerNum][2]+bstats[samplerNum][3]))
                if dev > 0.10:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats[samplerNum]), dev*100) 
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."

                        self.report(self.ERROR, msg, resolv, exit=True)
                if dev > 0.05:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, bstats[samplerNum], dev*100)  
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                
                        self.report(self.WARN, msg, resolv, exit=False)

        if errorCount == 0:
                self.report(self.OK, "Asymmetry = %f%%" % dev)


    def _reportLock(self, board, value):
        
        error = 0 
        if (value == 1): 
                self.report(self.OK, "Locked") 
        elif (value==0):    
                self.report(self.ERROR, "Synthesizer for board %s is not locked" % board, "Check if 10MHz is connected", exit=True)  
                error = 1
        else:    
                self.report(self.ERROR, "State of synthesizer for board %s cannot be determined" % board, "Check your hardware", exit=True)
                error = 1
        return error
        

    def validateSynthesizerLock(self, board, exitOnError = True):
        '''
        Checks if synthesizer serving the given board is locked
        '''

        board = self.dbbc3._boardToChar(board)
        ret = self.dbbc3.synthLock(board)

        error = 0

        print "\n===Checking synthesizer lock state of board %s" % (board)
        self._reportLock(board, ret['locked'])

        #if error > 0 and exitOnError:
        #    if self.ignoreErrors:
        #        print "Continuing because ignoreErrors was enabled"
        #    else:
        #        sys.exit(1)

    def validateSynthesizerFreq(self, board, targetFreq=0, exitOnError = True):
        '''
        Validates the actual tuning frequency of the GCoMo synthesizer serving the given board against
        the target value specified in the DBBC3 configuration file.

        If the parameter targetFreq is set to a value > 0 an additional check is performed against that frequency.

        '''

        board = self.dbbc3._boardToChar(board)
        freq = self.dbbc3.synthFreq(board)

        print "\n===Checking GCoMo synthesizer frequency of board %s" % (board)
        # verify that synth is tuned to the freq specified in the config
        if freq['actual'] != freq['target']:
                msg = "Synthesizer of board %s is tuned to %d MHz but should be %d MHz" % (board, freq['actual'], targetFreq)
                resolv = "Check your hardware"
                self.report (self.ERROR, msg, resolv, exit=exitOnError)
        # check freq against the user supplied value
        elif ((freq['actual'] != targetFreq) and (targetFreq > 0)):
                msg = "Synthesizer of board %s is tuned to %d MHz but according to config it should be %d MHz" % (board, freq['actual'], targetFreq)
                resolv = "Check the tuning frequencies in the dbbc3 config file"
                self.report (self.ERROR, msg, resolv, exit=exitOnError)
        else:
                self.report(self.OK, "Freq=%d MHz" % freq['actual'])
    


if __name__ == "__main__":

	try:
                from DBBC3Config import DBBC3Config
                from DBBC3 import DBBC3
                config = DBBC3Config()

                config.numCoreBoards = 4
                config.host="192.168.0.60"
                dbbc3 = DBBC3(config)
		dbbc3.connect()

		print "=== Disabling calibration loop"
		dbbc3.disableloop()
                
                validate = DBBC3Validation(dbbc3, ignoreErrors = True)
	
 		validate.validateSamplerOffsets(0)


		validate.validateSynthesizerLock(0)
		validate.validateSynthesizerLock(1)
		validate.validateSynthesizerLock(2)
		validate.validateSynthesizerLock(3)
#
		validate.validateSynthesizerFreq(0)
		validate.validateSynthesizerFreq(1)
		validate.validateSynthesizerFreq(2)
		validate.validateSynthesizerFreq(3)

		validate.validateIFLevel('a')
		validate.validateIFLevel('b')
		validate.validateIFLevel('c')
		validate.validateIFLevel('d')

		validate.validateSamplerPhases()

 		validate.validateSamplerPower(0)
 		validate.validateSamplerPower(1)
		validate.validateSamplerPower('C')
		validate.validateSamplerPower('D')

 		validate.validateSamplerOffsets(0)
 		validate.validateSamplerOffsets(1)
		validate.validateSamplerOffsets('C')
		validate.validateSamplerOffsets('D')

		
		print "=== Setting up calibration loop"
		dbbc3.enablecal()
		print "=== Enabling calibration loop"
		dbbc3.enableloop()

		dbbc3.disconnect()
		print "=== Done"

 	except Exception as e:
 		print e.message
 		dbbc3.disconnect()
		

	
