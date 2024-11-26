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
__copyright__ = "2022, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

import re
import sys
import numpy as np
from datetime import datetime
from math import floor
import time
import importlib
import os
import logging

import inspect

class Item(object):
    """
    Storage class to hold information about one validation check
    provided by one of the DBBC3 validation methods.
    Instances of this class can be passed to :py:class:`ValidationReport`
    via the  :py:func:`ValidationReport.add` method to provde a user 
    friendly representation of the validation procedure.


    The class provides these constants for specifying the reporting level::

        INFO
        WARN
        ERROR

    The class provides these constants for specifying the validation state::

        OK
        FAIL

    Args:
        level (str): the reporting level of the validation item (see levels above)
        action (str): a description of the validation action that was performed
        message (str): a message describing the outcome of the validation action
        resolution (str, optional): a resolution message to be displayed in case validation errors have occured
        state (str): a string describing the state of the validation action
        exit (boolean): True indicates that processing should stop in case of a validation failure (default: False)

    Note:
        Setting exit=True only indicates that validation failure is considered to be critical. Handling of the exit condition
        is not done by this class or by :py:class:`ValidationReport` and must be  handled in the upsteam code calling the 
        validation actions

    """

    # level
    #INFO = "INFO"
    #WARN = "WARN"
    #ERROR = "ERROR"

    INFO = "\033[1;34mINFO\033[0m"
    WARN = "\033[1;33mWARN\033[0m"
    ERROR = "\033[1;31mERROR\033[0m"

    # states
    #OK = "OK"
    OK = "\033[1;32mOK\033[0m"
    FAIL = "FAIL"

    #aux
    #RESOLUTION = "RESOLUTION"
    RESOLUTION = "\033[1;34mRESOLUTION\033[0m"

    def __init__(self, level="", action="", message="", resolution="", state="", exit=False):
        self.level = level
        self.action = action
        self.message = message
        self.resolution = resolution
        self.state = state
        self.exit = exit

    def __str__(self):
        
        #return(str(vars(self)))
        return 'action:\t{}\nstate:\t{}\nlevel:\t{}\nmessage:\t{}\nexit:\t{}\nresolution:\t{}'.format(self.action, self.state, self.level, self.message, self.exit, self.resolution)
        

class ValidationReport(object):
    '''
    Reporter class to provide human readable reports and/or logs of validation actions. Each report can consist of multiple validation items
    represented by an :py:class:`Item` instance.

    If any of the validation items has failed and has an exit condition the exit attribute of this class is set to True (unless 
    overridden by the py:attr:`ignoreErrors` argument.

    Args:
        ignoreErrors (boolean): If True a validation failure in any of the validation items will not set an exit condition (default: False)
    '''


    def __init__(self, ignoreErrors=False):

        self.clear()
        self.ignoreErrors = ignoreErrors

    @property
    def numWarnings(self):
        """ int: the total number of warnings raised for all validation items of this report """
        return self._numWarning

    @property
    def numError(self):
        """ int: the total number of errors raised for all validation items of this report """
        return self._numError

    @property
    def exit(self):
        """ boolean: True if at least one of the validation items has failed with an exit condition """
        return self._exit

    @property
    def result(self):
        ''' Identical to :py:obj:`items`. Returns the list of report items attached to this ValidationReport'''
        return(self.items)

    @property
    def items(self):
        ''' Returns the list of report items attached to this ValidationReport

        Returns:
            list of :obj:`Item`: the list of reporting items
        '''
        return(self._items)

    def clear(self):
        '''
        Reset the contents of the ValidationReport
        '''
        
        self._items = []
        self._numWarning = 0
        self._numError = 0
        self._exit = False

    def add(self, item):
        '''
        Add a validation item to the report

        If the item contains an exit condition (item.exit = True)
        the self.exit member is set to True unless the
        ignoreErrors parameter was set on initiliazation

        Args:
            item (Item): the validation Item instance to add
        '''
        if (item.level == Item.ERROR):
            self._numError += 1
        elif (item.level == Item.WARN):
            self._numWarning += 1

        self._items.append(item)

        if (item.exit == True and self.ignoreErrors == False):
            self._exit = True
    
    def __str__(self):
        ret = ""
        for result in self._items:
            ret += "---------------------\n"
            ret += result.__str__()
            ret += "\n---------------------\n"
           
        return(ret)


    def log(self, logger):
        '''
        Write all validation items attached to the report to the log. 

        Depending on the item.level string each logger entry will have either the 
        info, warning or error log levels::

            item.level contains "INFO" => log level info
            item.level contains "WARN" => log level warning
            item.level contains "ERROR" => log level error

        The message test will be formated in the following way::

        [item.state] item.action - item.message

        if the validation item contains a non-empty resolution field an additional line 
        will be logged with the following format::

        [RESOLUTION] item.resolution

        Args:
            logger (:py:class:`logging.Logger`): the logger object to use for logging the output 
        
        '''
        if (len(self._items) == 0):
            return

        for res in self._items:
            if "INFO" in res.level:
                logger.info("[{}] {} - {}".format(res.state,  res.action, res.message))
            elif ("WARN" in res.level ):
                logger.warning("[{}] {} - {}".format(res.state,  res.action, res.message))
            elif ("ERROR" in res.level ):
                logger.error("[{}] {} - {}".format(res.state,  res.action, res.message))

            if len(res.resolution) > 0:
                logger.info("[{}] {}".format(Item.RESOLUTION,  res.resolution))
        
class ValidationFactory(object):
    '''
    Factory class for providing the matching DBBC3Validation sub-class for the currently active
    DBBC3 mode and software version.

    In order to function all derived DBBC3Validation classes must follow the naming convention::

        DBBC3Validation_mode_majorversion

    e.g. DBBC3Validation_OCT_D_120 for mode OCT_D major version 120
    '''

    def create(self, dbbc3, ignoreErrors=False):
        """
        Return a DBBC3Validation sub-class object matching the current mode and software version of the DBBC3
        as specified in dbbc3.config 

        Args:
            dbbc3 (DBBC3): the active DBBC3 instance
            ignoreErrors (boolean, optional): If True do not exit processing in case of validation failures (default: False)
        Returns:
            the instance of the validation class matching the current mode and software version
        """

            #dbbc3 (:obj:`DBBC3.DBBC3`): the active :obj:`DBBC3.DBBC3` instance
        csClassName = _getMatchingValidation(dbbc3.config.mode, dbbc3.config.cmdsetVersion['majorVersion'])
        if (csClassName == ""):
            csClassName = "DBBC3ValidationDefault"
        CsClass = getattr(importlib.import_module("dbbc3.DBBC3Validation"), csClassName)
        return(CsClass(dbbc3,ignoreErrors))

def _getMatchingValidation(mode, majorVersion):
    '''
    Determines the validation sub-class to be used for the given mode and major version.

    if mode is not given the default validation class (DBBC3ValidationDefault) is selected
    if majorVersion is not given the latest implemented version for the activated mode will be used.

    Args:
        mode (str): the dbbc3 mode (e.g. OCT_D)
        majorVersion (str): the command set major version

    Returns:
        str: The class name that implements the valdation methods for the given mode and major version

    '''

    # parse all class names of this module
    current_module = sys.modules[__name__]


    pattern = re.compile("DBBC3Validation_%s_(.*)"%(mode))

    versions = []
    for key in dir(current_module):
        if isinstance( getattr(current_module, key), type ):
            match = pattern.match(key)
            if match:
                versions.append(match.group(1))

    # no versions found for this mode
    if len(versions) == 0:
        return("")

    versions.sort()

    if (majorVersion == ""):
        # if no specific version was requested return the most recent one
        pickVer = versions[-1]
    else:
        pickVer = versions[0]
        for i in versions:
            if int(i) <= int(majorVersion):
                pickVer = i
            else:
                break

    ret = "DBBC3Validation_%s_%s" % (mode,pickVer)
    return(ret)

class DBBC3ValidationDefault(object):
    '''
    Base class that contains the validation methods common to all DBBC3 modes

    All classes that contain validation methods specific for a particaular mode and
    software version should be derived from this class.

    Args:
        dbbc3 (DBBC3): the active DBBC3 instance
        ignoreErrors (boolean): If True do not exit processing in case of validation failures
    '''

#    OK = "\033[1;32mOK\033[0m"
#    INFO = "\033[1;34mINFO\033[0m"
#    WARN = "\033[1;35mWARN\033[0m"
#    ERROR = "\033[1;31mERROR\033[0m"
#    RESOLUTION = "\033[1;34mRESOLUTION\033[0m"
    
    def __init__(self, dbbc3, ignoreErrors):
        '''
        Constructor
        '''
        self.state = None
        self.dbbc3 = dbbc3
        self.ignoreErrors = ignoreErrors
        self._saveState()

        
    def _saveState(self):
        '''
        Saves the initial state (e.g. IF settings)
        '''
        if not self.dbbc3:
            return

        self.state = {}
        for board in range(self.dbbc3.config.numCoreBoards):
            ret = self.dbbc3.dbbcif(board)
            self.state["IF_{0}".format(board)] = ret


    def restoreState(self):
        '''
        Restores the state of the DBBC3 according to the
        state that was previously saved upon
        initialization 
        '''

        for board in range(self.dbbc3.config.numCoreBoards):
            ifstate = self.state["IF_{0}".format(board)]
            self.dbbc3.dbbcif(board, ifstate["inputType"], ifstate["mode"], ifstate["target"])
        

#    def setIgnoreErrors(self,ignoreErrors):
#        '''
#        Setter for the ignoreErrors parameter
#        '''
#        self.ignoreErrors = ignoreErrors


        
    def validateIFLevel(self, board, downConversion=True, agc=True):
        '''
        Performs various validations of the IF power settings as obtained from the dbbcif command:

        - IF power should be within 1000 counts of the target value
        - The attenuation setting should be within 20-40
        - AGC should be switched on (unless disabled by the agc parameter)
        - Downconversion should be switched on (unless check is disabled with the downConversion parameter)

        Args:
             board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
             downConversion (boolean, optional): If True validate that downconversion is enabled (default: True)
             agc (boolean, optional): If True validate that agc is turned on (default: True)

        Returns: 
            ValidationReport: the validation report 
        '''
        
        rep = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)
        check = "=== Checking IF power level on core board %s" % board.upper()
        item = Item()

        errorCount = 0
        ret = self.dbbc3.dbbcif(board)

        if abs(ret['target'] - ret['count']) > 1000:
                res = "Check and adjust IF input power levels (input level should be approx. -6dBm)"
                msg = "IF power not on target value. Should be close to %d is %d" % (ret['target'], ret['count'])
                rep.add(Item(Item.ERROR, check, msg, res, Item.FAIL, True))
                errorCount +=1
        if ret['inputType'] != 2 and downConversion==True:
                msg = "Wrong IF input setting. Is %d, should be 2 to enable downconversion" % ret['inputType']
                rep.add(Item(Item.ERROR, check, msg, "Switch on downconversion with the dbbcif command through the dbbc3 client software.", Item.FAIL, True))
                errorCount +=1
        if ret['mode'] != "agc" and agc==True:
                rep.add(Item(Item.ERROR, check, "Automatic gain control is disabled", "Enable agc with the dbbcif command through the dbbc3 client software.", Item.FAIL, True))
                errorCount +=1
        if ret['attenuation'] < 20:
                msg = "IF input power is too low. The attenuation should be in the range 20-40, but is %d" % (ret['attenuation'])
                rep.add(Item(Item.WARN, check, msg, "Increase the IF power", Item.FAIL, False))
                errorCount +=1
        if  ret['attenuation'] > 40:
                msg  = "IF input power is too high. The attenuation should be in the range 20-40, but is %d" % (ret['attenuation'])
                rep.add(Item(Item.WARN, check, msg, "Decrease the IF power", Item.FAIL, False))
                errorCount +=1
        if errorCount == 0:
            msg = "count = %d" % (ret['count'])
            rep.add(Item(Item.INFO, check, msg, state=Item.OK))
        
        return(rep)

    def validateSamplerPhases(self):
        """
        Validates that all sampler phases for all boards are synchronized

        Returns: 
            ValidationReport: the validation report 
        """

        rep = ValidationReport(self.ignoreErrors)
        check = "=== Checking sampler phases"
        # workaround for (possible) timing issue in the control software
        # if checkphase is called to quickly after reload of the firmware 
        # failure is responded even though the samplers are in sync
        time.sleep(2)
        

        if (self.dbbc3.checkphase()):
                rep.add(Item(Item.INFO, check, "", state=Item.OK))
        else:
                msg = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                msg += "If the problem persists retry restart up to 5 times.\n"
                msg += "If the problem persists check your 10MHz power level.\n"
                msg += "If the problem persists do a full hardware restart."

                rep.add(Item(Item.ERROR, check, self.dbbc3.lastResponse, msg, state=Item.FAIL, exit=True))

        return(rep)

    def _regulatePower(self, board, targetCount):

        prevAtt = -1
        
        retOrig = self.dbbc3.dbbcif(board)
        ret = retOrig
        if (ret["count"] > targetCount):
            upper = 64
            lower = ret["attenuation"]
        else:
            lower = 0
            upper = ret["attenuation"]


        # regulate power within +-10% of target
        while (abs(ret["count"] - targetCount) > 0.5 * targetCount ):
#            print (ret["count"], ret["attenuation"],targetCount, abs(ret["count"] - targetCount))
            att = int(floor((upper + lower)/2))
            if (att == prevAtt):
                return(False)
                
            #print (upper, lower, att)
            prevCounts = ret["count"]
            
            # set the attenuation level
            self.dbbc3.dbbcif(board, retOrig["inputType"], att)
            time.sleep(2)
            # re-read the new count level
            ret = self.dbbc3.dbbcif(board)

            if (ret["count"] < targetCount):
                upper = att
            else:
                lower = att
            prevAtt = att

        return True

    def validateSamplerPower(self, boardNum):
        """
        Validate the powers of all samplers of the specified board

        Args:
             boardNum (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns: 
            ValidationReport: the validation report 
        """

        rep = ValidationReport(self.ignoreErrors)

        targetCount = 32000
        errors = 0
        board = self.dbbc3.boardToChar(boardNum)
        check = "=== Checking sampler gains for board %s" % (board)

        # sampler gains should be checked with IF power close to target (32000)
        retOrig = self.dbbc3.dbbcif(board)

        if (self._regulatePower(board, targetCount) == False):
            # reset the dbbcif settings to their original values
            self._resetIFSettings( board, retOrig)
            rep.add(Item(Item.WARN, check, "Failed to regulate power level to {0}. Skipping test.".format(targetCount), "", state=Item.FAIL))
            return (rep)

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, 2, "man")
        #print (self.dbbc3.lastResponse)

        pow= self.dbbc3.core3h_core3_power(boardNum)
        if not pow:
                self._resetIFSettings( board, retOrig)
                rep.add(Item(Item.ERROR, check, self.dbbc3.lastResponse, "", state=Item.FAIL, exit=True))

        mean = np.mean(pow)
        if (mean == 0):
                resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "If the problem persists do a full hardware restart."

                self._resetIFSettings( board, retOrig)
                rep.add(Item(Item.ERROR, check, "Sampler powers are 0 for board %s" % board, resolv, state=Item.FAIL, exit=True))
        #if self.verbose:
        #       print "power values=%s mean=%f" % (str(pow), mean)

        maxdev = 0
        for power in pow:
            dev = abs(1 - power/mean)
            if dev > maxdev:
                maxdev = dev
        if maxdev > 0.2:
                msg = "Large differences (>20%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), maxdev*100)
                resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "If the problem persists do a full hardware restart."
                rep.add(Item(Item.ERROR, check, msg,  resolv, state=Item.FAIL, exit=True))
                errors += 1
        elif maxdev > 0.05:
                msg = "Large differences (>5%%) in sampler powers for board=%s. %s %f%%" % (board, str(pow), maxdev*100)
                resolv = "Restart the DBBC3 control software (no reload of firmware, re-initialize)\n"
                resolv += "If the problem persists retry restart up to 5 times.\n"
                resolv += "Possibly do a gain calibration (cal_delay=boardNum). Consult the documentation"
                rep.add(Item(Item.WARN, check, msg, resolv, state=Item.FAIL, exit=True))
                errors += 1

        if errors == 0:
                rep.add(Item(Item.INFO, check, "sampler powers = %s" % (pow), "", state=Item.OK))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings( board, retOrig)
#        self.dbbc3.dbbcif(board, retOrig["inputType"], retOrig["mode"], retOrig["target"])

        return rep
                


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
        """
        Validate the bit statistics for all samplers of the specified board

        Args:
             boardNum (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns: 
            ValidationReport: the validation report 
        """

        rep = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(boardNum)

        for samplerNum in range(self.dbbc3.config.numSamplers):

                check = "=== Checking bit statistics for board %s sampler %d" % (board, samplerNum)
                errorCount = 0

                bstats = self.dbbc3.core3h_core3_bstat(boardNum, samplerNum)
        #        print (self.dbbc3.lastResponse)
                if bstats is None:
                        rep.add(Item(Item.ERROR, check, self.dbbc3.lastResponse, "", state=Item.FAIL, exit=True))

                # Checking difference lower against upper half
                try:
                        #dev = abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3]))
                        dev = abs((bstats[0] + bstats[1] - bstats[2] - bstats[3]) / float(bstats[0] + bstats[1] + bstats[2] + bstats[3]))
                except ZeroDivisionError:
                        msg = "Corrupted bit statitics found (all 0): %s" % str(bstats)
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
        
                        rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))
                        continue

                        
                if dev > 0.10:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100) 
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."

                        rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))
                elif dev > 0.05:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100)  
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "If the problem persists retry restart up to 5 times.\n"
                        resolv += "If the problem persists do a full hardware restart."
                
                        rep.add(Item(Item.WARN, check, msg, resolv, state=Item.FAIL, exit=False))

                if errorCount == 0:
                        
                        rep.add(Item(Item.INFO, check, "Asymmetry = %f%%" % (dev*100), "", state=Item.OK))
        return(rep)

    def validateSamplerOffsets(self, boardNum):
        """
        Validate the offsets of all samplers of the specified board

        Args:
             boardNum (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns: 
            ValidationReport: the validation report 
        """

        rep = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(boardNum)


        check = "=== Checking sampler offsets for board %s" % (board)
        # save the original IF settings
        retOrig = self.dbbc3.dbbcif(board)
        #print (retOrig)
        ret = retOrig
        #print ("Original IF settings: ", retOrig)

        targetCount = 5000
        upper = 64
        lower = 0
        prevAtt = -1
        
        # try to regulate power to targetCount
        # if targetCount cannot be reached continue on lowest possible counts
        self._regulatePower(board, targetCount)
        #if (self._regulatePower(board, targetCount) == False):
        #    # reset the dbbcif settings to their original values
        #    self._resetIFSettings( board, retOrig)
        #    rep.add(Item(Item.WARN, check, "Failed to regulate power level to {0}. Skipping test.".format(targetCount), "", state=Item.FAIL))
        #    return (rep)

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, retOrig["inputType"], "man")
            
        # Reset the core3h thresholds (needed in case the calibration has been running)
        # core3h=1,regwrite core3 1 0xA4A4A4A4
        self.dbbc3.core3h_regwrite(board, "core3", 1, 0xA4A4A4A4)

        for samplerNum in range(self.dbbc3.config.numSamplers):

                errorCount = 0
                check = "=== Checking sampler offsets for board %s sampler %d" % (board, samplerNum)

                bstats = self.dbbc3.core3h_core3_bstat(boardNum, samplerNum)
        #        print (self.dbbc3.lastResponse)
                if bstats is None:
                        self._resetIFSettings(board, retOrig)
                        rep.add(Item(Item.ERROR, check, self.dbbc3.lastResponse, "", state=Item.FAIL, exit=True))

                # Checking difference lower against upper half
                try:
                        #dev = abs(1 - float(bstats[0]+bstats[1]) / float(bstats[2]+bstats[3]))
                        dev = abs((bstats[0] + bstats[1] - bstats[2] - bstats[3]) / float(bstats[0] + bstats[1] + bstats[2] + bstats[3]))
                except ZeroDivisionError:
                        msg = "Sampler offsets of 0 found %s" % str(bstats)
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
        
                        self._resetIFSettings(board, retOrig)
                        rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))
                        continue

                        
                if dev > 0.10:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>10%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100) 
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "Make sure pure noise is inserted (no tones!).\n"
                        resolv += "If the problem persists re-calibration of the system might be required.\n"

                        self._resetIFSettings(board, retOrig)
                        rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))
                elif dev > 0.05:
                        errorCount += 1
                        msg = "Asymmetric bit statistics (>5%%) for board %s sampler %d. %s. %f%%" % (board, samplerNum, str(bstats), dev*100)  
                        resolv = "Restart the DBBC3 control software (no reload of firmware only reinitialize)\n"
                        resolv += "Make sure pure noise is inserted (no tones!).\n"
                        resolv += "If the problem persists re-calibration of the system might be required.\n"
                
                        self.dbbc3.dbbcif(board)
                        #print (self.dbbc3.lastResponse)
                        rep.add(Item(Item.WARN, check, msg, resolv, state=Item.FAIL, exit=False))

                if errorCount == 0:
                        rep.add(Item(Item.INFO, check, "Asymmetry = %f%%" % (dev*100), "", state=Item.OK))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings(board, retOrig)
        return(rep)


    def _reportLock(self, board, value, report):
        
        check = "=== Checking synthesizer lock state of board %s" % (board)
        error = 0 
        if (value == True): 
                report.add(Item(Item.INFO, check, "Locked", "", Item.OK))
        elif (value==False):    
                report.add(Item(Item.ERROR, check, "Synthesizer for board %s is not locked" % board, "Check if 10MHz is connected", Item.FAIL, exit=True))
                error = 1
        else:    
                report.add(Item(Item.ERROR, check, "State of synthesizer for board %s cannot be determined" % board, "Check your hardware", Item.FAIL, exit=True))
                error = 1
        return error
        

    def validateSynthesizerLock(self, board, exitOnError = True):
        '''
        Validates that the synthesizer serving the given board is locked

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            exitOnError (boolean): if True any error will cause a program exit

        Returns:
            ValidationReport: contains the validation report
        '''
        report = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)
        ret = self.dbbc3.synthLock(board)

        self._reportLock(board, ret, report)
        return (report)


    def validateSynthesizerFreq(self, board, targetFreq=0.0, exitOnError = True):
        '''
        Validates the actual tuning frequency of the GCoMo synthesizer serving the given board against
        the target value as specified by the last synthFreq command or the value in the DBBC3 configuration file.

        If the parameter targetFreq is set to a value > 0 an additional check is performed against that frequency.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            targetFreq (float): the synthesizer frequency in MHz
            exitOnError (boolean): if True any error will cause a program exit

        Returns:
            ValidationReport: contains the validation report

        '''
        report = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)
        freq = self.dbbc3.synthFreq(board)

        check = "=== Checking GCoMo synthesizer frequency of board %s" % (board)

        # verify that synth is tuned to the freq specified in the config
        if freq['actual'] != freq['target']:
                msg = "Synthesizer of board %s is tuned to %f MHz but should be %f MHz" % (board, freq['actual'], freq['target'])
                resolv = "Check your hardware"
                report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))
        # check freq against the user supplied value
        elif ((freq['actual'] != targetFreq) and (targetFreq > 0)):
                msg = "Synthesizer of board %s is tuned to %f MHz but should be %f MHz" % (board, float(freq['actual']), targetFreq)
                resolv = "Check the tuning frequencies in the dbbc3 config file"
                report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))
        else:
                report.add(Item(Item.INFO, check, "Freq=%f MHz" % freq['actual'], "", Item.OK))

        return (report)


    def validatePPS(self, maxDelay=200, exitOnError=True):
        """
        Validates the delay between the internally generated and external PPS signals.
        The validation is carried out for all all active boards of the DBBC3. The validation
        fails in case any of the PPS delays is exceeding +-maxDelay nanoseconds (configurable).

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            maxDelay (int): the maximum valid delay in nanoseconds
            exitOnError (boolean): if True any error will cause a program exit

        Returns:
            ValidationReport: contains the validation report
        """

        report = ValidationReport(self.ignoreErrors)

        notSynced = []

        check = "=== Checking 1PPS synchronisation < +- %d ns" %(maxDelay)
        delays = self.dbbc3.pps_delay()

        for i in range(len(delays)):
                if abs(delays[i]) > maxDelay:
                        notSynced.append(self.dbbc3.boardToChar(i))

        if len(notSynced) > 0:
                msg = "The following boards have pps offsets > +-%d ns: %s" % (maxDelay, str(notSynced))
                resolv = "Restart the DBBC3 control software (do not reload of firmware only reinitialize)\n"
                resolv += "If the problem persists probably you have a hardware issue."
                report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))

        if len(notSynced) ==0:
                report.add(Item(Item.INFO, check, "PPS delays: %s ns" % delays, "", Item.OK))

        return (report)

#    def validatePPSDelay(self, board, exitOnError=False):
#
#        report = ValidationReport(self.ignoreErrors)
#        #TODO: make special call pps_delay for DDC_U (returns 4 values)
#        return(report)
#
#
#        board = self.dbbc3.boardToChar(board)
#        check =  "=== Checking PPS delays of core board %s" % board.upper()
#        ret = self.dbbc3.pps_delay()
#
#        for i in range(len(delays)):
#                if delays[i] == 0:
#                        inactive.append(self.dbbc3.boardToChar(i))
#                elif delays[i] > 200:
#                        notSynced.append(self.dbbc3.boardToChar(i))
#
#        if ret[0] != ret[1]:
#            msg =   "PPS delays for 1st and 2nd block differ %s on core board %s" % (ret, board.upper())
#            resolv = "This is a bug. Contact the maintainer of the DBBC3 software"
#                
#            report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))
#        else:
#            report.add(Item(Item.INFO, check, "PPS delays (1st block / 2nd block)  %s ns", "", Item.OK))
#
#        return(report)
#

    def validateTimesync(self, board, exitOnError=True, maxDelay=5):
        """
        Validates the time synchronisation of the specified core3h board

        Validation fails in case:

            - not valid time stamp could be obtained from the DBBC3
            - the DBBC3 time deveates by more than maxDealy seconds (configurable) from the local NTP time

        Failure could indicate that the GPS antenna is not properly connected to the DBBC3 or no GPS
        satelites were visible on system initialization. Also make sure that the local computer has its
        time synchonized by NTP.

        Args:
             board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
             exitOnError (boolean): if True any error will cause a program exit
             maxDelay (int): the maximum valid time delay in seconds

        Returns:
            ValidationReport: contains the validation report

        """

        report = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)
        check =  "=== Checking time synchronisation of core board %s" % board.upper()

        resolv = "Check that a GPS antenna is connected to the DBBC3\n"
        resolv = "Check that GPS satellites are visible (core3h=BOARD,gps)\n"
        resolv += "Re-initialize the DBBC3 and re-check\n"

        ret = self.dbbc3.core3h_time( board)
        if not ret:
                msg =   "No timestamp could be obtained for core board %s" % board.upper()
                report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))
        else:
                delta = abs(datetime.utcnow() - ret)
                if delta.seconds > maxDelay:
                        msg =   "Difference between reported time and local NTP time > 10s for board %s" % board.upper()
                        resolv += "Run core3h_timesync and re-check\n"
                        resolv += "Check that the local computer is synchronised via NTP\n"
                        report.add(Item(Item.ERROR, check, msg, resolv, Item.FAIL, exit=exitOnError))
                else:
                        report.add(Item(Item.INFO, check, "Reported time: %s" % str(ret), "", Item.OK))

        return(report)


class DBBC3Validation_OCT_D_110(DBBC3ValidationDefault):
    """
    class with validation methods specific to the OCT_D 110 mode

    Args:
        dbbc3 (DBBC3): the active DBBC3 instance
        ignoreErrors (boolean): If True do not exit processing in case of validation failures
    """
        
    def __init__(self, dbbc3, ignoreErrors):
        '''
        Constructor
        '''
        DBBC3ValidationDefault.__init__(self, dbbc3, ignoreErrors)

    def validateCalibrationLoop(self, exitOnError=False):
        '''
        Validates that the calibration loop is running

        Args:
            exitOnError (boolean, optional): if True raise an exit condition on validation failure
            
        Returns:
            ValidationReport: contains the validation report
        '''
        report = ValidationReport(self.ignoreErrors)

        check =  "=== Checking that the calibration loop is enabled"
        resolv = "Start the calibration loop by issuing the enableloop command"

        self.dbbc3.sendCommand("core3hstats=1")

        if not self.dbbc3.lastResponse.startswith("Control loop not running"):
            report.add(Item(Item.INFO, check, "The calibration loop is running", "", Item.OK))
        else:
            report.add(Item(Item.ERROR, check,"The calibration loop is not running", "", Item.FAIL, exit=exitOnError))

        return(report)

class DBBC3Validation_OCT_D_120(DBBC3ValidationDefault):
    """
    class with validation methods specific to the OCT_D 120 mode

    Args:
        dbbc3 (DBBC3): the active DBBC3 instance
        ignoreErrors (boolean): If True do not exit processing in case of validation failures
    """

    def __init__(self, dbbc3, ignoreErrors):
        '''
        Constructor
        '''
        DBBC3Validation_OCT_D_110.__init__(self, dbbc3, ignoreErrors)

    
    def validateFilter(self, board, filterNum, filterFile, checkBitmask=True, exitOnError=True):
        '''
        Validate the loaded filter file for the specified board

        In case the checkBitmaks parameter is set an additional check is done to 
        validate that the vsi bitmasks match the band widths of the selected filters.
        Should the band widths of the two OCT filters differ the bit mask is validated
        to match the bandwidth of the wider of the two filters.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            filterNum (int): the filter number (must be 1 or 2)
            filterFile (str): the name of the filter file to be validated
            checkBitmask (boolean): If true also vallidate that the vsi bitmask matches the filter band width
            exitOnError (boolean): if True any error will cause a program exit
        Returns:
            ValidationReport: the report containing the validation results
            
        '''
        rep = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)
        check = "=== Checking filter%d for board %s" % (filterNum, board)

        if filterNum not in [1,2]:
            rep.add(Item(Item.ERROR, check,"Illegal filter number specified. Must be 1 or 2 but is %d" % (filterNum), "", Item.FAIL, exit=exitOnError))
            return(rep)

        filters = self.dbbc3.tap(board)
        key = "filter%d_file" % (filterNum)
        loadedFilter = os.path.basename(filters[key])

        if filterFile == loadedFilter:
            rep.add(Item(Item.INFO, check, "Filter file: %s" % (loadedFilter), "", Item.OK))
        else:
            res = "Use the tap command to load the correct filter file"
            rep.add(Item(Item.ERROR, check,"Loaded filter %s but expected %s" % (loadedFilter, filterFile), res, Item.FAIL, exit=exitOnError))
            return (rep)

        if not checkBitmask:
            return (rep)

        masks = self.dbbc3.core3h_vsi_bitmask(board)
        
        
        # determine filter bandwidth
        tmp = os.path.basename(filters["filter1_file"]).split("-")
        for i, c in enumerate(tmp[1]):
            if not c.isdigit():
                stop = tmp[1][:i].split("_")[0]
                
                break

        bw = int(stop) - int(tmp[0])
        for item in self.validateBitmask(board, bw).items:
            rep.add(item)

        return(rep)


    def validateBitmask(self, boardNum, bandwidth, exitOnError=True):
        '''
        Validates the vsi bitmasks for the specified board

        Note:
            valid bandwidth parameter values are 2000,1000,500,250
            even though the true filter bandwidths are powers of two (e.g 2048 etc.)

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            bandwidth (int): the bandwidth of the tap filters in MHz (see note above)

        Returns:
            ValidationReport: the report containing the validation results
        '''

        validMask = { 
         2000: "0xFFFFFFFF",
         1000: "0x33333333",
         500: "0x03030303",
         250: "0x00030003"}

        rep = ValidationReport(self.ignoreErrors)
        board = self.dbbc3.boardToChar(boardNum)
        check = "=== Checking vsi bitmasks for board %s" % (board)

        masks = self.dbbc3.core3h_vsi_bitmask(board)

        try:
            bw = int(bandwidth)
        except ValueError:
            rep.add(Item(Item.ERROR, "validateBitmask", "illegal value for bandwidth parameter (must be int)", "contact developer", Item.FAIL, exit=exitOnError))

        if bw not in validMask.keys():
            rep.add(Item(Item.ERROR, "validateBitmask", "illegal bandwidth parameter specified. Must be one of [{}]".format(",".join(map(str, validMask.keys()))), "", Item.FAIL, exit=exitOnError))
            return (rep)

        # check that all bitmasks are identical
        for mask in masks[1:]:
            if not mask == masks[0]:
                res = "Reinitialize the DBBC3 control software. If the problem persists contact a DBBC3 developer."
                rep.add(Item(Item.ERROR, check,"Illegal vsi bitmask found", res, Item.FAIL, exit=exitOnError))

        if not masks[0] == validMask[bw]:
            res = "Consult the DBBC3 FAQ for instructions on how to set bitmasks (https://deki.mpifr-bonn.mpg.de/Cooperations/DBBC3/DBBC3_FAQ)"
            rep.add(Item(Item.ERROR, check, "illegal mask for bandwidth of %d MHz:  %s expected: %s " %(bw, masks[0], validMask[bandwidth]), res, Item.FAIL, exit=exitOnError))

        return(rep)

    def validateSamplerPower(self, boardNum):
        '''
        Validates the sampler powers (gains)

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            ValidationReport: the report containing the validation results
        '''

        rep = ValidationReport(self.ignoreErrors)

        targetCount = 32000
        errors = 0
        board = self.dbbc3.boardToChar(boardNum)
        check = "=== Checking sampler powers (gains) for board %s" % (board)

        # sampler gains should be checked with IF power close to target (32000)
        retOrig = self.dbbc3.dbbcif(board)

        if (self._regulatePower(board, targetCount) == False):
            # reset the dbbcif settings to their original values
            self._resetIFSettings( board, retOrig)
            rep.add(Item(Item.WARN, check, "Failed to regulate power level to {0}. Skipping test.".format(targetCount), "", state=Item.FAIL))
            return (rep)

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, 2, "man")

        # TODO: Check with Sven whether this is neccesary for OCT_D_124
        # Reset the core3h thresholds (needed in case the calibration has been running)
        # core3h=1,regwrite core3 1 0xA4A4A4A4
        self.dbbc3.core3h_regwrite(board, "core3", 1, 0xA4A4A4A4)

        ret = self.dbbc3.samplerstats(board)
        # 'offset': {'val':offset [63384378, 64164764, 65276968, 65609344], 'frac': [49.52, 50.13, 51.0, 51.26], 'state': ['OK', 'OK', 'NOT OK', 'NOT OK']}


        for samplerNum in range(self.dbbc3.config.numSamplers):

            errorCount = 0

            if ret["power"]["state"][samplerNum] != "OK":
                errorCount += 1
                msg = "Offset too large for sampler %d: %f" % (samplerNum, ret["power"]["val"][samplerNum])
                resolv = "Make sure pure noise is inserted (no tones!).\n"
                resolv += "If the problem persists re-calibration of the system might be required.\n"

                self._resetIFSettings(board, retOrig)
                rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))

        if errorCount == 0:
            rep.add(Item(Item.INFO, check, "Sampler powers: %s" % (ret["power"]["val"]) , "", state=Item.OK))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings(board, retOrig)
        return(rep)


        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings( board, retOrig)
#        self.dbbc3.dbbcif(board, retOrig["inputType"], retOrig["mode"], retOrig["target"])

        return rep

    def validateSamplerOffsets(self, board, targetCount=32000):
        '''
        Validates the sampler offsets

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            targetCount (int, optional): the total power count at which the validation should be carried out. Defaults to 32000.
        
        Returns:
            ValidationReport: the report containing the validation results
        '''

        rep = ValidationReport(self.ignoreErrors)

        board = self.dbbc3.boardToChar(board)

        # save the original IF settings
        retOrig = self.dbbc3.dbbcif(board)
        ret = retOrig

        if (self._regulatePower(board, targetCount) == False):
            check = "=== Checking sampler offsets for board %s" % (board)
            # reset the dbbcif settings to their original values
            self._resetIFSettings( board, retOrig)
            rep.add(Item(Item.WARN, check, "Failed to regulate power level to {0}. Skipping test.".format(targetCount), "", state=Item.FAIL))
            return (rep)

        # Now freeze the attenuation
        ret = self.dbbc3.dbbcif(board, retOrig["inputType"], "man")

        ret = self.dbbc3.samplerstats(board)
        # 'offset': {'val': [63384378, 64164764, 65276968, 65609344], 'frac': [49.52, 50.13, 51.0, 51.26], 'state': ['OK', 'OK', 'NOT OK', 'NOT OK']}

        for samplerNum in range(self.dbbc3.config.numSamplers):

            errorCount = 0
            check = "=== Checking sampler offsets for board %s sampler %d" % (board, samplerNum)

            if ret["offset"]["state"][samplerNum] != "OK":
                errorCount += 1
                msg = "Offset too large for sampler %d: %f%%" % (samplerNum, ret["offset"]["frac"][samplerNum])
                resolv = "Make sure pure noise is inserted (no tones!).\n"
                resolv += "If the problem persists re-calibration of the system might be required.\n"

                self._resetIFSettings(board, retOrig)
                rep.add(Item(Item.ERROR, check, msg, resolv, state=Item.FAIL, exit=True))

            if errorCount == 0:
                rep.add(Item(Item.INFO, check, "Sampler offsets: %s frac: %s" % ( ret["offset"]["val"][samplerNum],  ret["offset"]["frac"][samplerNum]) , "", state=Item.OK))

        # Finally reset the dbbcif settings to their original values
        self._resetIFSettings(board, retOrig)
        return(rep)
        

if __name__ == "__main__":

        try:
                from dbbc3.DBBC3 import DBBC3
                from dbbc3.DBBC3Validation import DBBC3Validation
                import logging

                dbbc3 = DBBC3(host=sys.argv[1], port=4000, mode="DDC_U", timeout=900)

                val = DBBC3Validation(dbbc3, ignoreErrors = True)

                logger = logging.getLogger("test")
                logger.setLevel(logging.DEBUG)
                # create console handler
                ch = logging.StreamHandler()
                # create formatter and add it to the handlers
                scnformatter = logging.Formatter('%(message)s')
                ch.setFormatter(scnformatter)
                #ch.emit = decorate_emit(ch.emit)
                # add the handlers to the logger
                logger.addHandler(ch)

                val.validateFilters(0, "2000-4000_64taps.flt")
                res = val.validateIFLevel(0)
                res.log(logger)
                if res.exit:
                    print ("exiting")
                    sys.exit()


                sys.exit(1)
        
                validate.validatePPS(0)
                validate.validateSamplerOffsets(0)


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

                

                #dbbc3.disconnect()
                print ("=== Done")

        except Exception as e:
                print (e.message)
                #dbbc3.disconnect()
                

