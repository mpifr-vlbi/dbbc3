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
  This module is part of the DBBC3 package and implements higher
  level validation methods for verification of the proper
  initialization and configuration of the DBBC3 VLBI backend
'''

__author__ = "Helge Rottmann"
__copyright__ = "2019, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottman[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

import re
import sys
import numpy as np
from datetime import datetime
import time


class DBBC3Validation(object):

    OK = "\033[1;32mOK\033[0m"
    INFO = "\033[1;34mINFO\033[0m"
    WARN = "\033[1;35mWARN\033[0m"
    ERROR = "\033[1;31mERROR\033[0m"
    RESOLUTION = "\033[1;34mRESOLUTION\033[0m"
    
    def __init__(self, dbbc3, ignoreErrors = False):
        self.dbbc3 = dbbc3
        self.ignoreErrors = ignoreErrors
        self.latLevel = ""
        self.lastMessage = ""
        self.lstResolution = ""


    def setIgnoreErrors(ignoreErrors):
        self.ignoreErrors = ignoreErrors

    def report(self, level, check="", result="", resolution= "", exit=False):
        '''
        Default method for reporting the outcome of validation actions. 
        Should be overriding for customization
        '''

        print("[%s] - %s - %s" % (level, check, result))
        if resolution != "":
                print ("[%s] \033[1;34m%s\033[0m" % (self.RESOLUTION, resolution))

        if exit:
            if (self.ignoreErrors):
                print ("Continuing because ignoreErrors was enabled")
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
        
        board = self.dbbc3.boardToChar(board)
        check = "=== Checking IF power level on core board %s" % board.upper()


        errorCount = 0
        ret = self.dbbc3.dbbcif(board)

        if abs(ret['target'] - ret['count']) > 1000:
                msg = "Check and adjust IF input power levels (should be @ -11dBm)"
                self.report(self.ERROR, check, "IF power not on target value. Should be close to %d is %d" % (ret['target'], ret['count']), msg, exit=True)
                errorCount +=1
        if ret['inputType'] != 2 and downConversion==True:
                self.report(self.ERROR, check, "Wrong IF input setting. Is %d, should be 2 to enable downconversion" % ret['inputType'], exit=True)
                errorCount +=1
        if ret['mode'] != "agc" and agc==True:
                self.report(self.ERROR, check, "Automatic gain control is disabled", exit=True)
                errorCount +=1
        if ret['attenuation'] < 20:
                self.report(self.WARN, check, "IF input power is too low. The attenuation should be in the range 20-40, but is %d" % (ret['attenuation']))
                errorCount +=1
        if  ret['attenuation'] > 40:
                self.report(self.WARN, check, "IF input power is too high. The attenuation should be in the range 20-40, but is %d" % (ret['attenuation']))
                errorCount +=1
        if errorCount == 0:
            self.report(self.OK, check, "count = %d" % (ret['count']))



    def validateSamplerPhases(self):
        check = "=== Checking sampler phases"

        if (self.dbbc3.checkphase()):
                self.report(self.OK, check, "OK")
        else:
                msg = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                msg += "If the problem persists retry restart up to 5 times.\n"
                msg += "If the problem persists check your 10MHz power level.\n"
                msg += "If the problem persists do a full hardware restart."

                self.report(self.ERROR, check, self.dbbc3.lastResponse, msg, exit=True)

    def validateSamplerPower(self, boardNum):

        errors = 0
        board = self.dbbc3.boardToChar(boardNum)
        check = "===Checking sampler gains for board %s" % (board)

        # sampler gains should be checked with IF power close to target (32000)
        retOrig = self.dbbc3.dbbcif(board)

        #ret = dict(retOrig)
        #while (ret["count"] < 30000):
        #   ret = self.dbbc3.dbbcif(board, 1, "agc", 32000)

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, 2, "man")
        #print (self.dbbc3.lastResponse)

        pow= self.dbbc3.core3h_core3_power(boardNum)
        if pow is None:
                self._resetIFSettings( board, retOrig)
                self.report(self.ERROR, check, self.dbbc3.lastResponse, exit=True)

        mean = np.mean(pow)
        if (mean == 0):
                resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "If the problem persists do a full hardware restart."

                self._resetIFSettings( board, retOrig)
                self.report(self.ERROR, check, "Sampler powers are 0 for board %s" % board, resolv, exit=True)
        #if self.verbose:
        #       print "power values=%s mean=%f" % (str(pow), mean)

        for power in pow:
                dev = abs(1 - power/mean)
                if dev > 0.2:
                        msg = "Large differences (>20%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), dev*100)
                        resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                        self.report(self.ERROR, check, msg , resolv)
                        errors += 1
                elif dev > 0.05:
                        msg = "Large differences (>5%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), dev*100)
                        resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "Possibly do a gain calibration (cal_delay=boardNum). Consult the documentation"
                        self.report(self.WARN, check, msg , resolv)
                        errors += 1

        if errors == 0:
                self.report(self.OK, check,  "sampler powers = %s" % (pow))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings( board, retOrig)
#        self.dbbc3.dbbcif(board, retOrig["inputType"], retOrig["mode"], retOrig["target"])
                


    def _resetIFSettings(self, board, setting):

        # set attenuator manually to original value
        self.dbbc3.dbbcif(board, setting["inputType"], setting["attenuation"])

        # check that IF settings have been changed (workaround for bug)
        while True:
            ret = self.dbbc3.dbbcif(board)
            if (ret["attenuation"] == setting["attenuation"]):
                break
            else:
                ret = self.dbbc3.dbbcif(board, setting["inputType"], setting["attenuation"])
            

        # switch back to original mode
        self.dbbc3.dbbcif(board, setting["inputType"], setting["mode"], setting["target"])

        while True:
            ret = self.dbbc3.dbbcif(board)
            if (ret["mode"] == setting["mode"]):
                break
            else:
                self.dbbc3.dbbcif(board, setting["inputType"], setting["mode"], setting["target"])

        #print (self.dbbc3.lastResponse)


        
    def validateBitStatistics(self, boardNum):

        board = self.dbbc3.boardToChar(boardNum)

        self.report(self.INFO, "===Checking bit statistics for board %s" % (board), "" , "")
            
        for samplerNum in range(self.dbbc3.config.numSamplers):

                errorCount = 0
                check = "===Checking board %s sampler %d" % (board, samplerNum)

                bstats = self.dbbc3.core3h_core3_bstat(boardNum, samplerNum)
        #        print (self.dbbc3.lastResponse)
                if bstats is None:
                        self.report (self.ERROR, check, self.dbbc3.lastResponse, exit=True)

                # Checking difference lower against upper half
                try:
                        #dev = abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3]))
                        dev = abs((bstats[0] + bstats[1] - bstats[2] - bstats[3]) / float(bstats[0] + bstats[1] + bstats[2] + bstats[3]))
                except ZeroDivisionError:
                        msg = "Corrupted bit statitics found (all 0): %s" % str(bstats)
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
        
                        self.report(self.ERROR, check, msg, resolv, exit=True)
                        continue

                        
                if dev > 0.10:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100) 
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."

                        self.report(self.ERROR, check, msg, resolv, exit=True)
                elif dev > 0.05:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100)  
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                
                        self.report(self.WARN, check, msg, resolv, exit=False)

                if errorCount == 0:
                        self.report(self.OK, check, "Asymmetry = %f%%" % (dev*100))

    def validateSamplerOffsets(self, boardNum):

        board = self.dbbc3.boardToChar(boardNum)

        self.report(self.INFO, "===Checking sampler offsets for board %s" % (board), "" , "")
        # save the original IF settings
        retOrig = self.dbbc3.dbbcif(board)
        #print ("Original IF settings: ", retOrig)

        #ret = dict(retOrig)
        #attenuation = ret["attenuation"]
        
        # set attenuator to max. value
        attenuation = 63
        ret = self.dbbc3.dbbcif(board, 2, attenuation)

        # check that IF settings have been changed (workaround for bug)
        count = 0
        while True:
            ret = self.dbbc3.dbbcif(board)
            if (ret["attenuation"] == 63):
                break
            elif (count == 10):
                self.report(self.WARN, "Failed to set the power levels for verifying sampler offsets. Skipping test.", "")
                break
            else:
                ret = self.dbbc3.dbbcif(board, 2, attenuation)
                count += 1

        # sampler offsets should be checked with IF power of approx. 5000
        print (ret["count"], ret["attenuation"])
        while (ret["count"] < 5000 and ret["attenuation"] > 0):
            print (ret["count"], ret["attenuation"])
            time.sleep(1)
            ret = self.dbbc3.dbbcif(board, 2, ret["attenuation"]-1)
        # if power cannot be regulated (e.g. no IF connected) give up
#       self.report(self.WARN, "Too little IF power to perform

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, 2, "man")
        #print ("Modified IF settings: ", ret)
            
        # Reset the core3h thresholds (needed in case the calibration has been running)
        # core3h=1,regwrite core3 1 0xA4A4A4A4
        self.dbbc3.core3h_regwrite(board, "core3", 1, 0xA4A4A4A4)

        for samplerNum in range(self.dbbc3.config.numSamplers):

                errorCount = 0
                check = "===Checking board %s sampler %d" % (board, samplerNum)

                bstats = self.dbbc3.core3h_core3_bstat(boardNum, samplerNum)
        #        print (self.dbbc3.lastResponse)
                if bstats is None:
                        self._resetIFSettings(board, retOrig)
                        self.report (self.ERROR, check, self.dbbc3.lastResponse, exit=True)

                # Checking difference lower against upper half
                try:
                        #dev = abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3]))
                        dev = abs((bstats[0] + bstats[1] - bstats[2] - bstats[3]) / float(bstats[0] + bstats[1] + bstats[2] + bstats[3]))
                except ZeroDivisionError:
                        msg = "Sampler offsets of 0 found %s" % str(bstats)
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
        
                        self._resetIFSettings(board, retOrig)
                        self.report(self.ERROR, check, msg, resolv, exit=True)
                        continue

                        
                if dev > 0.10:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100) 
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."

                        self._resetIFSettings(board, retOrig)
                        self.report(self.ERROR, check, msg, resolv, exit=True)
                elif dev > 0.05:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100)  
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                
                        self.dbbc3.dbbcif(board)
                        #print (self.dbbc3.lastResponse)
                        self.report(self.WARN, check, msg, resolv, exit=False)

                if errorCount == 0:
                        self.report(self.OK, check, "Asymmetry = %f%%" % (dev*100))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings(board, retOrig)
#        self.dbbc3.dbbcif(board, retOrig["inputType"], retOrig["mode"], retOrig["target"])


    def _reportLock(self, board, value):
        
        check = "===Checking synthesizer lock state of board %s" % (board)
        error = 0 
        if (value == True): 
                self.report(self.OK, check, "Locked") 
        elif (value==False):    
                self.report(self.ERROR, check, "Synthesizer for board %s is not locked" % board, "Check if 10MHz is connected", exit=True)  
                error = 1
        else:    
                self.report(self.ERROR, check, "State of synthesizer for board %s cannot be determined" % board, "Check your hardware", exit=True)
                error = 1
        return error
        

    def validateSynthesizerLock(self, board, exitOnError = True):
        '''
        Checks if synthesizer serving the given board is locked
        '''

        board = self.dbbc3.boardToChar(board)
        ret = self.dbbc3.synthLock(board)

        self._reportLock(board, ret)


    def validateSynthesizerFreq(self, board, targetFreq=0, exitOnError = True):
        '''
        Validates the actual tuning frequency of the GCoMo synthesizer serving the given board against
        the target value specified in the DBBC3 configuration file.

        If the parameter targetFreq is set to a value > 0 an additional check is performed against that frequency.

        '''

        board = self.dbbc3.boardToChar(board)
        freq = self.dbbc3.synthFreq(board)

        check = "===Checking GCoMo synthesizer frequency of board %s" % (board)

        # verify that synth is tuned to the freq specified in the config
        if freq['actual'] != freq['target']:
                msg = "Synthesizer of board %s is tuned to %d MHz but should be %d MHz" % (board, freq['actual'], targetFreq)
                resolv = "Check your hardware"
                self.report (self.ERROR, check, msg, resolv, exit=exitOnError)
        # check freq against the user supplied value
        elif ((freq['actual'] != targetFreq) and (targetFreq > 0)):
                msg = "Synthesizer of board %s is tuned to %d MHz but according to config it should be %d MHz" % (board, freq['actual'], targetFreq)
                resolv = "Check the tuning frequencies in the dbbc3 config file"
                self.report (self.ERROR, check, msg, resolv, exit=exitOnError)
        else:
                self.report(self.OK, check, "Freq=%d MHz" % freq['actual'])


    def validatePPS(self, exitOnError=True):

        inactive = []
        notSynced = []

        check = "===Checking 1PPS synchronisation"
        delays = self.dbbc3.pps_delay()
        for i in range(len(delays)):
                if delays[i] == 0:
                        inactive.append(self.dbbc3.boardToChar(i))
                elif delays[i] > 200:
                        notSynced.append(self.dbbc3.boardToChar(i))

        if len(inactive) > 0:
                msg = "The following boards report pps_delay=0: %s" % str(inactive)
                resolv = "Check if these boards have been disabled in the DBBC3 config file"
                self.report (self.WARN, check, msg, resolv, exit=False)
        if len(notSynced) > 0:
                msg = "The following boards have pps offsets > 200 ns: %s" % str(notSynced)
                resolv = "Restart the DBBC3 control software (do not reload of firmware only reinitialize)\n"
                resolv += "If the problem persists probably you have a hardware issue."
                self.report (self.ERROR, check, msg, resolv, exit=exitOnError)

        if len(inactive) ==0 and len(notSynced) ==0:
                self.report(self.OK, check, "PPS delays: %s" % delays)

    def validatePPSDelay(self, board, exitOnError=False):

        board = self.dbbc3.boardToChar(board)
        check =  "=== Checking PPS delays of core board %s" % board.upper()
        ret = self.dbbc3.pps_delay(board)

        if ret[0] != ret[1]:
            msg =   "PPS delays for 1st and 2nd block differ %s on core board %s" % (ret, board.upper())
            resolv = "This is a bug. Contact the maintainer of the DBBC3 software"
            self.report (self.ERROR, check, msg, resolv, exit=exitOnError)
        else:
            self.report(self.OK, check, "PPS delays (1st block / 2nd block)  %s ns" % ret)




    def validateTimesync(self, board, exitOnError=True):

        board = self.dbbc3.boardToChar(board)
        check =  "=== Checking time synchronisation of core board %s" % board.upper()

        resolv = "Check that a GPS antenna is connected to the DBBC3\n"
        resolv = "Check that GPS satellites are visible (core3h=BOARD,gps)\n"
        resolv += "Re-initialize the DBBC3 and re-check\n"

        ret = self.dbbc3.core3h_time( board)
        if not ret:
                msg =   "No timestamp could be obtained for core board %s" % board.upper()
                self.report (self.ERROR, check, msg, resolv, exit=exitOnError)
        else:
                delta = datetime.utcnow() - ret
                if delta.seconds > 10:
                        msg =   "Difference between reported time and local NTP time > 10s for board %s" % board.upper()
                        resolv += "Run core3h_timesync and re-check\n"
                        resolv += "Check that the local computer is synchronised via NTP\n"
                        self.report (self.ERROR,check,  msg, resolv, exit=exitOnError)
                else:
                        self.report(self.OK, check, "Reported time: %s" % str(ret))



if __name__ == "__main__":

        try:
                from DBBC3Config import DBBC3Config
                from DBBC3 import DBBC3
                config = DBBC3Config()

                config.numCoreBoards = 4
                config.host="192.168.0.60"
                dbbc3 = DBBC3(config)
                dbbc3.connect()

                print ("=== Disabling calibration loop")
                dbbc3.disableloop()
                
                validate = DBBC3Validation(dbbc3, ignoreErrors = True)
        
                validate.validatePPS(0)
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

                
                print ("=== Setting up calibration loop")
                dbbc3.enablecal()
                print ("=== Enabling calibration loop")
                dbbc3.enableloop()

                dbbc3.disconnect()
                print ("=== Done")

        except Exception as e:
                print (e.message)
                dbbc3.disconnect()
                

        
