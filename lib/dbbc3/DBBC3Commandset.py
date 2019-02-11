# -*- coding: utf-8 -*-
'''
  This module is part of the DBBC3 package and implements the command sets
  of the DBBC3 for the various modes and versions
  

  Copyright (C) 2019 Helge Rottmann, Max-Planck-Institut für Radioastronomie, Bonn, Germany
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

__author__ = "Helge Rottmann"
__copyright__ = "2019, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottman[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

import types 
import re
import time
import importlib
import inspect
import sys

def getMatchingCommandset(mode, version):
    '''
    Determines the Commandset sub-class to be used for the 
    given mode and version.

    All Subclasses should be derived from DBBC3CommandsetDefault and should
    follow the naming convention: DBBC3Commandset_MODE_VERSION
    e.g. DBBC3Commandset_OCT_D_110
    '''

    # parse all class names of this module
    current_module = sys.modules[__name__]

    
    pattern = re.compile("DBBC3Commandset_%s_(.*)"%(mode))

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

    if (version == ""):
        # if no specific version was requested return the most recent one
        pickVer = versions[-1]
    else:
        pickVer = versions[0]
        for i in versions:
            if int(i) <= int(version):
                pickVer = i
            else:
                break

    ret = "DBBC3Commandset_%s_%s" % (mode,pickVer)
    print "Selecting commandset version: %s" % ret   

    return(ret)


class DBBC3Commandset(object):
    '''
    Base class for all DBBC3 commandset implementations
    '''

    def __init__(self,clas, mode="", version=""):
        '''
        Constructor
        Determines the approriate class implementing the command set for the given version and mode.
        if mode is not given the default command set is loaded
        if version is not given the latest version will be used

        Parameters:
        mode: the dbbc3 mode (e.g. OCT_D)
        version: the command set version
        '''
        
        csClassName = getMatchingCommandset(mode, version )
    
        if (csClassName == ""):
            csClassName = "DBBC3CommandsetDefault"

        CsClass = getattr(importlib.import_module("dbbc3.DBBC3Commandset"), csClassName)
        CsClass(clas)


class DBBC3CommandsetDefault(DBBC3Commandset):

    def __init__(self, clas):

        clas.dbbcif = types.MethodType (self.dbbcif.im_func, clas)
        clas.enableloop = types.MethodType (self.enableloop.im_func, clas)
        clas.disableloop = types.MethodType (self.disableloop.im_func, clas)
        clas.enablecal = types.MethodType (self.enablecal.im_func, clas)
        clas.synthFreq = types.MethodType (self.synthFreq.im_func, clas)
        clas.synthLock = types.MethodType (self.synthLock.im_func, clas)
        clas.checkphase = types.MethodType (self.checkphase.im_func, clas)
        clas.time = types.MethodType (self.time.im_func, clas)
        clas.core3_bstat = types.MethodType (self.core3_bstat.im_func, clas)
        clas.core3_power = types.MethodType (self.core3_power.im_func, clas)

        clas.core3h_version = types.MethodType (self.core3h_version.im_func, clas)
        clas.core3h_sysstat = types.MethodType (self.core3h_sysstat.im_func, clas)
        clas.core3h_sysstat_fs = types.MethodType (self.core3h_sysstat_fs.im_func, clas)
        clas.core3h_mode_fs = types.MethodType (self.core3h_mode_fs.im_func, clas)
        clas.core3h_status_fs = types.MethodType (self.core3h_status_fs.im_func, clas)
        clas.core3h_devices = types.MethodType (self.core3h_devices.im_func, clas)
        clas.core3h_regread = types.MethodType (self.core3h_regread.im_func, clas)
        clas.core3h_regread_dec = types.MethodType (self.core3h_regread_dec.im_func, clas)
        clas.core3h_regwrite = types.MethodType (self.core3h_regwrite.im_func, clas)
        clas.core3h_regupdate = types.MethodType (self.core3h_regupdate.im_func, clas)

        clas.adb3l_reset = types.MethodType (self.adb3l_reset.im_func, clas)
        clas.adb3l_reseth = types.MethodType (self.adb3l_reseth.im_func, clas)
        clas.adb3l_resets = types.MethodType (self.adb3l_resets.im_func, clas)
        clas.adb3l_biston = types.MethodType (self.adb3l_biston.im_func, clas)
        clas.adb3l_bistoff = types.MethodType (self.adb3l_bistoff.im_func, clas)
        clas.adb3l_SDA_on = types.MethodType (self.adb3l_SDA_on.im_func, clas)
        clas.adb3l_delay = types.MethodType (self.adb3l_delay.im_func, clas)
        clas.adb3l_offset = types.MethodType (self.adb3l_offset.im_func, clas)
        clas.adb3l_gain = types.MethodType (self.adb3l_gain.im_func, clas)


    def core3h_regread(self, board, regNum, device="core3"):
        '''
        Reads the value of the device register

        Note: not all devices have readbale registers. See DBBC3 documentation for "devices" command

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        regNum: the index of the device register to read
        device: the name of the device (as returned by the core3h_devices command); default = core3

        Return:
        The value of the device register
        '''

        boardNum = self.boardToDigit(board) +1

        ret = self.sendCommand("core3h=%d,regread %s %d" % (boardNum, device, regNum))
        lines = ret.split("\n")
        fields = lines[2].split("/")

        return int(fields[2].strip())

    def core3h_regread_dec(self, board, regNum, device="core3"):
        '''
        Reads the value of the device register (in machine readable form)

        Note: not all devices have readbale registers. See DBBC3 documentation for "devices" command

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        regNum: the index of the device register to read
        device: the name of the device (as returned by the core3h_devices command); default = core3

        Return:
        The value of the device register
        '''

        boardNum = self.boardToDigit(board) +1

        ret = self.sendCommand("core3h=%d,regread_dec %s %d" % (boardNum, device, regNum))
        lines = ret.split("\n")

        return int(lines[2].strip())

    def core3h_regwrite(self, board, device, regNum, value):
        '''
        Writes a value into the device register

        Note: not all devices have writable registers. See DBBC3 documentation for "devices" command

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        device: the name of the device (as returned by the core3h_devices command)
        regNum: the index of the device register to read
        value: the register value to write; must be hexadecimal number or string, e.g. 0x01020304

        Return:
        True: if value was changed; False otherwise

        Exceptions:
        throws ValueError in case the supplied value is not in hex format
        '''
        boardNum = self.boardToDigit(board) +1

        try:
            hexVal = self._valueToHex(value)
        except:
            raise ValueError("core3h_regwrite: register value not in hexadecimal format")

        ret = self.sendCommand("core3h=%d,regwrite %s %d %s" % (boardNum, device, regNum, hexVal))
        if "unmodified" in ret:
            return(False)
        
        return(True)

    def core3h_regupdate(self, board, device, regNum, value, bitmask):
        '''
        Updates only certain bits of the value of a device register

        Note: not all devices have writable registers. See DBBC3 documentation for "devices" command

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        device: the name of the device (as returned by the core3h_devices command)
        regNum: the index of the device register to read
        value: the register value to write; must be hexadecimal number or string, e.g. 0x01020304
        bitmask: the bitmask specifying which bits are overwritten (1) and which remain unchanged (0)

        Return:
        True: if value was changed; False otherwise

        Exceptions:
        throws ValueError in case the supplied value is not in hex format
        '''
        boardNum = self.boardToDigit(board) +1

        try:
            hexVal = self._valueToHex(value)
        except:
            raise ValueError("core3h_regupdate: register value not in hexadecimal format")

        try:
            hexBitmask = self._valueToHex(bitmask)
        except:
            raise ValueError("core3h_regupdate: bitmask not in hexadecimal format")

        ret = self.sendCommand("core3h=%d,regupdate %s %d %s %s" % (boardNum, device, regNum, hexVal, hexBitmask))

        if "unmodified" in ret:
            return(False)

        return(True)

    def time(self):
        '''
        Reads time information from all boards. For each board a dict with the
        following keys is obtained:
        seconds:
        halfYearsSince2000:
        daysSince2000:
        timestamp:
        timestampAsString:
        
        Returns: array of dicts; one entry for each board (0=A)
        '''

        resp = []
        ret = self.sendCommand("time")

        lines = ret.split("\n")
        entry = {}
        for line in lines:
            line = line.strip()
            tok = line.split("=")
            if len(tok) == 2:
                value = tok[1].strip()
                if (value.isdigit()):
                    value = int(value)
                entry[tok[0].strip()] = value
            elif "FiLa10G" in line:
                resp.append(entry)
                entry =  {}
            else:
                # 2019-01-30T13:32:08
                try:
                    dateTime = time.strptime(line,"%Y-%m-%dT%H:%M:%S")
                    entry["timestamp"] = dateTime
                    entry["timestampAsString"] = line
                except:
                    continue
                
        return(resp)

        
    def core3_power(self, board):
        '''
        Obtains the gains of all 4 samplers of the given board

        Returns: the array of the sampler gains
        Returns: None in case the core3 board is not connected
        '''

        boardNum = self.boardToDigit(board) +1

        pow = []
        ret = self.sendCommand("core3h=%d,core3_power" % (boardNum))

        if "not connected" in ret:
                return None

        pow.append(self.core3h_regread(boardNum, 5))
        pow.append(self.core3h_regread(boardNum, 6))
        pow.append(self.core3h_regread(boardNum, 7))
        pow.append(self.core3h_regread(boardNum, 8))

        return(pow)

    def core3_bstat(self, board):
        '''
        Obtains the 2-bit statistics for all samplers of the given board
        Returns a 2D array containing the 4 levels for all samplers of the given board
        Returns None if the core board is not connected
        '''

        boardNum = self.boardToDigit(board) +1
        return(pow)

    def core3_bstat(self, board):
        '''
        Obtains the 2-bit statistics for all samplers of the given board
        Returns a 2D array containing the 4 levels for all samplers of the given board
        Returns None if the core board is not connected
        '''

        boardNum = self.boardToDigit(board) +1
        boardId = self.boardToChar(board)

        sampler = []
        for samplerNum in range(self.config.numSamplers):
                bstats = []
                ret = self.sendCommand("core3h=%s,core3_bstat %d" % (boardNum,samplerNum))

                if "not connected" in ret:
                        return(None)

                # evaluate the registers that contain the statistics
                bstats.append(self.core3h_regread(boardNum, 5))
                bstats.append(self.core3h_regread(boardNum, 6))
                bstats.append(self.core3h_regread(boardNum, 7))
                bstats.append(self.core3h_regread(boardNum, 8))
                sampler.append(bstats)

        return (sampler)

    def dbbcif(self, board):
        '''
        Reads the IF power on the given board

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A

        Returns: dictionary holding the values reported by dbbcif
        '''

        resp = {}
        board = self.boardToChar(board).lower()
        ret = self.sendCommand("dbbcif%s" % (board))

        pattern = re.compile("dbbcif%s/\s(\d),(\d+),(.+),(\d),(\d+),(\d+)"%(board))

        match = pattern.match(ret)
        if match:

                resp['input'] = int(match.group(1))
                resp['gain'] = int(match.group(2))
                resp['mode'] = match.group(3)
                resp['filter'] = int(match.group(4))
                resp['count'] = int(match.group(5))
                resp['target'] = int(match.group(6))

        return ( resp )

    def checkphase(self):
        '''
        Checks wether all samplers are in sync

        Returns True if all samplers are in sync
        Returns False otherwise (get output with lastResponse() to find out which is not
        '''
        ret = self.sendCommand("checkphase")

        if "out of sync" in ret:
                return(False)
        else:
                return(True)

    def synthLock(self, board):
        '''
        Gets the lock state of the GCoMo synthesizer serving the given core board
        A state of 1 indicates lock
        A state of 0 indicates unlock
        A state of -1 indicates an error obtaining the lock state

        Returns: an array holding the state
        '''

        resp = {}
        board = self.boardToDigit(board)
        
        freq = -1

        # Each synthesizer has two outputs (source=1 or 2)
        # board A is served by synth 1 source 1
        # board B is served by synth 1 source 2
        # board C is served by synth 2 source 1
        # etc.
        synthNum = int(board / 2) +1
        sourceNum = board % 2 + 1

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
        resp['locked'] = locked[sourceNum-1]


        return resp

    def synthFreq(self, board):
        ''' 
        Determines the frequency of the GCoMo synthesizer serving the given core board
        board: core board identifier (numeric or char)

        Returns the synthesizer frequency in MHz
        # board B is served by synth 1 source 2
        # board C is served by synth 2 source 1
        # etc.
        '''

        resp = {}
        boardNum = self.boardToDigit(board)
        synthNum = int(boardNum / 2) +1
        sourceNum = boardNum % 2 + 1

        self.sendCommand("synth=%d,source %d" % (synthNum, sourceNum))
        ret = self.sendCommand("synth=%d,cw" % synthNum)

        lines = ret.split("\n")
        # output: ['cw\r', 'F 4524 MHz; // Act 4524 MHz\r', '\r-2->']
        for line in lines:
                if "MHz" in line:
                        # F 4524 MHz; // Act 4524 MHz
                        tok = line.split(" ")
                        resp['target'] = int(tok[1]) * 2
                        resp['actual'] = int(tok[5]) * 2

        return(resp)

    def enableloop(self):
        '''
        starts the automatic calibration loop
        '''
        return self.sendCommand("enableloop")

    def disableloop(self):
        '''
        stops the automatic calibration loop
        '''
        return self.sendCommand("disableloop")

    def enablecal(self, threshold="on", gain="off", offset="off"):
        '''
        Sets the threshold, gain and offset for the automatic calibration loop
        The loop must be activated with the enableloop command
        '''
        return self.sendCommand("enablecal=%s,%s,%s" % (threshold,gain,offset))

    # CORE3H commands
    def core3h_version(self, board):
        ''' 
        Displays the firmware version

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,version" % (boardNum))

    def core3h_sysstat(self, board):
        ''' 
        Displays information about the current status of the system and
        gives an overviewof the state of the most important user 
        settings

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,sysstat" % (boardNum))

    def core3h_sysstat_fs(self, board):
        ''' 
        Identical to core3h_sysstat but returns machine (fields-system)
        readable output

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,sysstat_fs" % (boardNum))

    def core3h_mode_fs(self, board):
        ''' 
        Returns mode information in a machine-readble form (field-system)

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,mode_fs" % (boardNum))

    def core3h_status_fs(self, board):
        ''' 
        Returns time sync information in a machine-readble form (field-system)

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,status_fs" % (boardNum))

    def core3h_devices(self, board):
        ''' 
        Lists all devices of the the current system and their
        corresponding memory address ranges

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        
        Return:
        dictionary (key=devicename, value=memory address range)
        '''
        boardNum = self.boardToDigit(board)+1

        ret = self.sendCommand("core3h=%d,devices" % (boardNum))
        #print ret
        lines = ret.split("\n")
        entry = {}
        for line in lines:
            line = line.strip()
            tok = line.split("->")
            if len(tok) == 2:
                value = tok[0].strip()
                if (value.isdigit()):
                    value = int(value)
                entry[tok[1].strip()] = value


        return (entry)

    # ADB3L commands
    def adb3l_reset(self):
        '''
        Resets all ADB3L boards and sets the registers to default values
        '''
        return self.sendCommand("adb3l=reset")

    def adb3l_reseth(self):
        '''
        Resets all ADB3L boards, but does NOT changei/reset any register settings
        '''
        return self.sendCommand("adb3l=reseth")

    def adb3l_resets(self, board, sampler=-1):
        '''
        Resets the ADB3L registers to default values for the specified board and 
        for the specified sampler (optiona1)
    
        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampler (optional): sampler number (0-3)
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "adb3l=resets=%d" % boardNum
        if sampler != -1:
            cmd += ",%d" % sampler
            
        return self.sendCommand(cmd)

    def adb3l_biston(self, board):
        '''
        Turns on BIST-mode for all samplers on the specified board.
        Note: after setting BIST-mode a "reseth" command must be executed

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''

        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("adb3l=biston=%d" % boardNum)

    def adb3l_bistoff(self, board):
        '''
        Turns off BIST-mode for all samplers on the specified board.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''

        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("adb3l=bistoff=%d" % boardNum)

    def adb3l_SDA_on(self, board, sampler):
        '''
        Turns on SDA Mode (Sampler Delay Adjust) for the specified board and sampler.
        Has to be used before adjusting the delay of a sampler with the delay command.
        Introduces a delay offset of 60ps.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampler: sampler number (0-3)
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "adb3l=SDA_on=%d,%d" % (boardNum, sampler)

        return self.sendCommand(cmd)


    def adb3l_delay(self, board, sampler, value=512):
        '''
        Sets the sampler delay for the specified board and sampler.
        The allowed range is 0-1023 which corresponds to -60ps to +60ps with a stepping size of 120fs.
        The default is 512 = 0ps.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampler: sampler number (0-3)
        value (default=512): the delay value in steps of 120fs

        Exceptions:
        Throws ValueError in case an illegal value was passed
        '''

        boardNum = self.boardToDigit(board)+1
    
        if value < 0 or value>1023:
            raise ValueError("sampler delay value must be in the range 0-1023")

        cmd = "adb3l=delay=%d,%d,%d" % (boardNum, sampler,value)

        return self.sendCommand(cmd)

    def adb3l_offset(self, board, sampler, value=512):
        '''
        Sets the sampler offset value for the specified board and sampler.
        The allowed range is 0-255 which corresponds to -20mV to +20mV with a stepping size of 156microV.
        The default is 128 = 0mV.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampler: sampler number (0-3)
        value (default=128): the sampler offset in steps of 156microV.

        Exceptions:
        Throws ValueError in case an illegal value was passed
        '''

        boardNum = self.boardToDigit(board)+1

        if value < 0 or value>255:
            raise ValueError("sampler offset value must be in the range 0-255")

        cmd = "adb3l=offset=%d,%d,%d" % (boardNum, sampler,value)

        return self.sendCommand(cmd)

    def adb3l_gain(self, board, sampler, value=512):
        '''
        Sets the sampler gain value for the specified board and sampler.
        The allowed range is 0-255 which corresponds to -0.5dB to +0.5dB with a stepping size of 0.004dB.
        The default is 128 = 0dB.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampler: sampler number (0-3)
        value (default=128): the sampler offset in steps of 0.004dB.

        Exceptions:
        Throws ValueError in case an illegal value was passed
        '''

        boardNum = self.boardToDigit(board)+1

        if value < 0 or value>255:
            raise ValueError("sampler gain value must be in the range 0-255")

        cmd = "adb3l=gain=%d,%d,%d" % (boardNum, sampler,value)

        return self.sendCommand(cmd)

class DBBC3Commandset_OCT_D_110(DBBC3CommandsetDefault):

    def __init__(self, clas):

        DBBC3CommandsetDefault.__init__(self,clas)

        clas.tap = types.MethodType (self.tap.im_func, clas)
        clas.tap2 = types.MethodType (self.tap2.im_func, clas)


    def tap2(self, boardNum, filterFile, scaling=1):
        '''
        Sets the second tap filter when in OCT mode

        Parameters:
        boardNum:
        filterFile:
        scaling: should always be one (default =1)
        '''

        return self.sendCommand("tap2=%d,%s,%d" % (boardNum, filterFile,scaling))

    def tap(self, boardNum, filterFile, scaling=1):
        '''
        Sets the first tap filter when in OCT mode

        Parameters:
        boardNum:
        filterFile:
        scaling: should always be one (default =1)
        '''

        return self.sendCommand("tap=%d,%s,%d" % (boardNum, filterFile,scaling))

class DBBC3Commandset_OCT_D_120(DBBC3Commandset):
    pass
class DBBC3Commandset_DDC_S_010(DBBC3Commandset):
    pass
class DBBC3Commandset_OCT_D_150(DBBC3Commandset):
    pass
class DBBC3Commandset_OCT_D_220(DBBC3Commandset):
    pass

