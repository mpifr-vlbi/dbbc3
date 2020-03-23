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

import DBBC3Util as d3util
import types 
import re
import time
import importlib
import inspect
import sys
from datetime import datetime

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
    print ("Selecting commandset version: %s" % ret)

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
        print ("Using commandset version: ", csClassName)
    
        if (csClassName == ""):
            csClassName = "DBBC3CommandsetDefault"

        CsClass = getattr(importlib.import_module("dbbc3.DBBC3Commandset"), csClassName)
        CsClass(clas)


class DBBC3CommandsetDefault(DBBC3Commandset):
    '''
    '''

    def __init__(self, clas):

        #clas.dbbcif = types.MethodType (self.dbbcif.__func__, clas)
        #clas.enableloop = types.MethodType (self.enableloop.__func__, clas)
        clas.dbbcif = types.MethodType (self.dbbcif.__func__, clas)
        clas.enableloop = types.MethodType (self.enableloop.__func__, clas)
        clas.disableloop = types.MethodType (self.disableloop.__func__, clas)
        clas.enablecal = types.MethodType (self.enablecal.__func__, clas)
        clas.synthFreq = types.MethodType (self.synthFreq.__func__, clas)
        clas.synthLock = types.MethodType (self.synthLock.__func__, clas)
        clas.checkphase = types.MethodType (self.checkphase.__func__, clas)
        clas.time = types.MethodType (self.time.__func__, clas)
        clas.version = types.MethodType (self.version.__func__, clas)
        clas.reconfigure = types.MethodType (self.reconfigure.__func__, clas)

        clas.core3h_version = types.MethodType (self.core3h_version.__func__, clas)
        clas.core3h_sysstat = types.MethodType (self.core3h_sysstat.__func__, clas)
        clas.core3h_sysstat_fs = types.MethodType (self.core3h_sysstat_fs.__func__, clas)
        clas.core3h_mode_fs = types.MethodType (self.core3h_mode_fs.__func__, clas)
        clas.core3h_status_fs = types.MethodType (self.core3h_status_fs.__func__, clas)
        clas.core3h_devices = types.MethodType (self.core3h_devices.__func__, clas)
        clas.core3h_regread = types.MethodType (self.core3h_regread.__func__, clas)
        clas.core3h_regread_dec = types.MethodType (self.core3h_regread_dec.__func__, clas)
        clas.core3h_regwrite = types.MethodType (self.core3h_regwrite.__func__, clas)
        clas.core3h_regupdate = types.MethodType (self.core3h_regupdate.__func__, clas)
        clas.core3h_core3_bstat = types.MethodType (self.core3h_core3_bstat.__func__, clas)
        clas.core3h_core3_power = types.MethodType (self.core3h_core3_power.__func__, clas)
        clas.core3h_core3_corr = types.MethodType (self.core3h_core3_corr.__func__, clas)
        clas.core3h_core3_mode = types.MethodType (self.core3h_core3_mode.__func__, clas)
        clas.core3h_core3_init = types.MethodType (self.core3h_core3_init.__func__, clas)
        clas.core3h_reboot = types.MethodType (self.core3h_reboot.__func__, clas)
        clas.core3h_reset = types.MethodType (self.core3h_reset.__func__, clas)
        clas.core3h_output = types.MethodType (self.core3h_output.__func__, clas)
        clas.core3h_start = types.MethodType (self.core3h_start.__func__, clas)
        clas.core3h_stop = types.MethodType (self.core3h_stop.__func__, clas)
        clas.core3h_arp = types.MethodType (self.core3h_arp.__func__, clas)
        clas.core3h_tengbarp = types.MethodType (self.core3h_tengbarp.__func__, clas)
        clas.core3h_tengbinfo = types.MethodType (self.core3h_tengbinfo.__func__, clas)
        clas.core3h_tengbcfg = types.MethodType (self.core3h_tengbcfg.__func__, clas)
        clas.core3h_destination = types.MethodType (self.core3h_destination.__func__, clas)
        clas.core3h_vdif_userdata = types.MethodType (self.core3h_vdif_userdata.__func__, clas)
        clas._getVdifUserdata = types.MethodType (self._getVdifUserdata.__func__, clas)
        clas.core3h_vdif_station = types.MethodType (self.core3h_vdif_station.__func__, clas)
        clas.core3h_vdif_frame = types.MethodType (self.core3h_vdif_frame.__func__, clas)
        clas.core3h_vdif_enc = types.MethodType (self.core3h_vdif_enc.__func__, clas)
        clas.core3h_timesync = types.MethodType (self.core3h_timesync.__func__, clas)
        clas.core3h_time = types.MethodType (self.core3h_time.__func__, clas)
        clas.core3h_tvg_mode = types.MethodType (self.core3h_tvg_mode.__func__, clas)
        clas.core3h_splitmode = types.MethodType (self.core3h_splitmode.__func__, clas)
        clas.core3h_inputselect = types.MethodType (self.core3h_inputselect.__func__, clas)
#       clas.core3h_vsi_swap = types.MethodType (self.core3h_vsi_swap.__func__, clas)
        clas.core3h_vsi_bitmask = types.MethodType (self.core3h_vsi_bitmask.__func__, clas)
        clas.core3h_vsi_samplerate = types.MethodType (self.core3h_vsi_samplerate.__func__, clas)

        clas.adb3l_reset = types.MethodType (self.adb3l_reset.__func__, clas)
        clas.adb3l_reseth = types.MethodType (self.adb3l_reseth.__func__, clas)
        clas.adb3l_resets = types.MethodType (self.adb3l_resets.__func__, clas)
        clas.adb3l_biston = types.MethodType (self.adb3l_biston.__func__, clas)
        clas.adb3l_bistoff = types.MethodType (self.adb3l_bistoff.__func__, clas)
        clas.adb3l_SDA_on = types.MethodType (self.adb3l_SDA_on.__func__, clas)
        clas.adb3l_delay = types.MethodType (self.adb3l_delay.__func__, clas)
        clas.adb3l_offset = types.MethodType (self.adb3l_offset.__func__, clas)
        clas.adb3l_gain = types.MethodType (self.adb3l_gain.__func__, clas)

# GENERAL DBBC3 commands
    def version(self):
        '''
        Reads the DBBC3 control software version

        Returns:
        dictionary holding the values reported by the version command with the following keys:
        "mode": the current DBBC3 mode, e.g. DDC_V
        "majorVersion": the major version of the current control software e.g. 124
        '''

        resp = {}
        ret = self.sendCommand("version")

        # version/ DDC_V,124,October 01 2019;
        # version/ OCT_D,110,July 03 2019
        # version/ DDC_V,124,February 18th 2020;
        pattern = re.compile("version\/\s+(.+),(\d+),(.+?\s+.+?\s+\d{4});{0,1}")

        match = pattern.match(ret)
        if match:
            #print ("match", match.group(1))
            # remove any st/nd/rd/th from the date string
            amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2), match.group(3))
            resp["mode"] = match.group(1)
            resp["majorVersion"] =  match.group(2)
            resp["minorVersion"] = datetime.strptime(amended, '%B %d %Y').strftime('%y%m%d')

        return (resp)

    
    def time(self):
        '''
        Reads time information from all boards. For each board a dict with the
        following keys is obtained:
        seconds:
        halfYearsSince2000:
        daysSince2000:
        timestamp:
        timestampAsString:
        
        Return:
        List of dicts; one entry for each board (0=A)
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

        
    def dbbcif(self, board, inputType=None, mode="agc",  target=None):
        '''
        Gets / sets the configuration of the GCoMo IF modules

        If the IF is connected on the top pin of the GCoMo (bypassing the
        downconversion) the inputType parameter should be set to 1.
        If the IF has been downconverted by the GCoMo the inputType should
        be set to 2. Selecting inputType=1 will disable the the synthesizer
        tone.

        if the inputType is not specified or set to None the current 
        settings are reported.

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A
        inputType: 1 = IF input without downconversion
                   2 = IF input after downconversion
        mode (optional): "agc" = automatic gain control (default if not specified)
                         "man" = manual attenuation (retains last agc value)
                          numeric value = attenuation step (0-63) in steps of 0.5 dB
        target (optional): the target power level for the "agc" mode

        Return:
        dictionary holding the values reported by dbbcif with the following keys:
        "inputType": see above
        "attenuation": the current attenuation level
        "mode": the current agc mode 
        "count": the current IF level
        "target": the target IF level
        '''

        resp = {}
        board = self.boardToChar(board).lower()
        cmd = "dbbcif%s" % (board)

        if (inputType):
            if inputType not in [1,2]:
                raise ValueError("dbbcif: inputType must be 1 or 2")
            cmd += "=%d" % inputType

            agcStr = str(mode)
            if (agcStr not in ["agc", "man"]):
                if  not agcStr.isdigit():
                    raise ValueError("dbbcif: mode must be agc,man or 0-63")
                elif (int(agcStr) not in range(64)):
                    raise ValueError("dbbcif: attenuation must be in the range 0-63")
            cmd += ",%s" % agcStr

            if (target):
                cmd += ",1,%d" % target

        ret = self.sendCommand(cmd)

        pattern = re.compile("dbbcif%s/\s(\d),(\d+),(.+),(\d),(\d+),(\d+)"%(board))

        match = pattern.match(ret)
        if match:

                resp['input'] = int(match.group(1))
                resp['attenuation'] = int(match.group(2))
                resp['mode'] = match.group(3)
                resp['filter'] = int(match.group(4))
                resp['count'] = int(match.group(5))
                resp['target'] = int(match.group(6))

        return ( resp )

    def reconfigure(self):
        '''
        Reconfigures the core3h boards (reloads firmware), then reinitializes the ADB3L
        and core3h and finally does a PPS sync.
        '''

        self.sendCommand("reconfigure")

    def checkphase(self):
        '''
        Checks whether all samplers are in sync

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
        Switches on/off  the threshold, gain and offset calibration for the automatic calibration loop
        The loop must be activated with the enableloop command.
        If called without the optional parameters the defaults will be used (see Parameters)

        Parameters:
        threshold (optional, default=on): switch threshold calibration [on/off]
        gain (optional, default=off): switch gain calibration [on/off]
        offset (optional, default=off): switch offset calibration [on/off]

        Return:
        If successful returns dictionary with keys "threshold", "gain", "offset"
        '''

        #Calibration enabled:
        #threshold=ON
        #gain=OFF
        #offset=OFF

        resp = {}
        ret = self.sendCommand("enablecal=%s,%s,%s" % (threshold.lower(),gain.lower(),offset.lower()))
        for line in ret.split("\n"):
            line = line.strip()
            #if ('=' in line):
            try:
                (key,val) = line.split("=")
                resp[key] = val
            except:
                pass
                
        return (resp)

    # CORE3H commands

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

    def _getVdifUserdata(self, board):

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,vdif_userdata" % (boardNum)
        ret = self.sendCommand(cmd)

        userdata = []
        for line in ret.split("\n"):
            line = line.strip()
            if line.startswith("0x"):
                userdata.append(line)

        return(userdata)
        
    def core3h_vsi_samplerate(self, board, sampleRate=None, decimation=1):
        '''
        Gets /sets the VSI input sample rate for the specified Core3h board

        All arguments are optional. If the command is called without the
        sampleRate parameter the current VSI input sample rate is returned.

        The decimation parameter decimates the input such that the resulting
        sample rate is 1/decimation of the specified rate
        
        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        sampleRate (optional): the input sampling rate in samples per second
        decimation (optional): a divisor in the range 1..255; default=1

        Return:
        Dictionary with keys "sampleRate" and "decimation"
    
        Exception:
        Exception: in case the sample rate could not be set
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,vsi_samplerate" % (boardNum)
        if sampleRate:
            cmd += " %d %d" % (sampleRate, decimation)

        ret = self.sendCommand(cmd)

        if "Failed" in ret:
            raise Exception("core3h_vsi_samplerate: Error setting vsi_samplerate (check lastResponse)" )

        response = {} 
        pattern = re.compile(".*:\s+(\d+)\s+Hz\s?\/?\s?(\d)?")
        #VSI sample rate : 64000000 Hz
        #VSI sample rate : 1280000 Hz / 2
        for line in ret.split("\n"):
            if "VSI sample rate" in line:
                match =  pattern.match(line)
                if match:
                    if not match.group(2):
                        response["decimation"] = 1
                    else:
                        response["decimation"] = int(match.group(2))
                    response["sampleRate"] = int(match.group(1))

        return(response)

    def core3h_vsi_bitmask(self, board, vsi=None, mask=None, reset=False):
        
        boardNum = self.boardToDigit(board)+1

        vsiStr = str(vsi)
        if (not vsiStr.isdigit()):
            ValueError("core3h_vsi_bitmask: vsi must be numeric")

        if vsiStr and not mask:
            ValueError("core3h_vsi_bitmask: missing mask for vsi: %d" % (vsi))

        if not vsiStr and mask:
            ValueError("core3h_vsi_bitmask: no vsi was specified")

        valStr = self._valueToHex(bitmask)
        if (int(valStr, 16) > 0xffffffff):
            raise ValueError("core3h_vdif_bitmask: the supplied bitmask is longer than 32 bit")
    
        cmd = "core3h=%d,vsi_bitmask" % (boardNum)
        ret = self.sendCommand(cmd)

        #VSI input bitmask : 0xFFFFFFFF 0xFFFFFFFF
        
        return(ret)
        
    def core3h_vsi_swap(self, board, firstVSI=None, secondVSI=None):
        '''
        deprecated

        Not fully implemented. Don't use.
        '''

        boardNum = self.boardToDigit(board)+1

        mapping = {}
        vsiStr = ""
        count = 0
        if firstVSI:
            vsiStr += " " + firstVSI
            count += 1
        if secondVSI:
            vsiStr += " " + secondVSI
            count += 1

        if count == 1 and firstVSI != "reset":
            raise ValueError("core3h_vsi_swap: both VSIs must be specified")
            
        cmd = "core3h=%d,vsi_swap %s" % (boardNum, vsiStr)
        ret = self.sendCommand(cmd)

        pattern = re.compile("\s*vsi(\d+):\s+VSI\s+input\s+(\d+)")

        # vsi1: VSI input 2
        #for line in ret.split("\n"):
        #    match = pattern.match(line)
        #    if match:
                

        return(ret)

    def core3h_inputselect(self, board, source):
        '''
        Selects one of the available input data sources.

        The command implictely resets the VSI bitmask, input width and VSI swap settings to their
        respective defaults. 

        TODO: update the documentation

        Note: it is recommended to execute core3h_reset (with ot without keepsync option) after
             changing the input source

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        source: one of "tvg","vsi1","vsi2","vsi1-2","vsi1-2-3-4","vsi1-2-3-4-5-6-7-8"

        Return:
        String containing the current split mode setting; "unknown" if the mode could not be determined

        Exception:
        ValueError: in case an unknown mode has been specified
        
        '''

        response = "unknown"

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,inputselect %s" % (boardNum, source)
        ret = self.sendCommand(cmd)

        # Input selected: tvg
        pattern = re.compile("\s*Input selected:\s*(.*)")
        if "Failed" in ret:
            raise ValueError("core3h_inputselect: Illegal source supplied: %s" % (source))

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                response = match.group(1)

        return(response)

    def core3h_splitmode(self, board, mode):
        '''
        Enables / Disables the split mode

        When split mode is enabled the selected and bitmasked input data is
        split into two halves exactly in the middle. The two halves will be
        processed as if they were independent input streams, The lower half
        (by bit position) is output at output0 the higher half is output as 
        output1.
            
        Split mode requires an input width of at least 2 bit.

        Note: raw and vdif format can be applied independently to each split
            stream with the heklp of the core3h_start 1+2+3+4 command syntax

        Note: in order to specify a correct VDIF frame setup you have to take
            into account that the effective input width is halved when the 
            split mode is enabled.

        Note: A restriction of the split mode is that only output0 is capable
            of producing multi-threaded VDIF data. At output1 the data will 
            always be forced to be single-threaded, regardless of the chosen
            frame setup.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        mode: "on" or "off"

        Return:
        String containing the current split mode setting ("on"/"off"); "unknown" if the mode could not be determined

        Exception:
        ValueError: in case an unknown mode has been specified

        '''

        boardNum = self.boardToDigit(board)+1

        if mode not in ["on","off"]:
            raise ValueError("core3h_splitmode: illegal mode supplied: %s" % (mode))

        cmd = "core3h=%d,splitmode %s" % (boardNum, mode)
        ret = self.sendCommand(cmd)

        if "Split mode: off" in ret:
            return ("off")
        elif "Split mode: on" in ret:
            return ("on")
        else:
            return("unknown")

        
    def core3h_tvg_mode(self, board, mode=None):
        '''
        Gets / sets the test vector generator mode for the given board.

        mode can be one of:
        all-0:  all bits = 0
        all-1:  all bits = 1
        vsi-h:  VSI-H test vector pattern
        cnt:    pattern with four 8-bit counters
        If called without the mode parameter the current setting is returned.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        mode: the tvg mode identifier (see above)
    
        Return:
        String containing the current tvg mode; "unknown" if the mode could not be determined

        Exception:
        ValueError: in case an unknown mode has been specified 
        '''
        boardNum = self.boardToDigit(board)+1

        retMode = "unknown"

        modeStr = ""
        if mode:
            modeStr = mode.strip()

        cmd = "core3h=%d,tvg_mode %s" % (boardNum, modeStr)
        ret = self.sendCommand(cmd)
        
        if "Failed" in ret:
            raise ValueError("core3h_tvg_mode: illegal TVG mode supplied: %s" % (mode))
        elif "VSI-H" in ret:
            retMode = "vsi-h"
        elif "8-bit counters" in ret:
            retMode = "cnt"
        elif "all bits 0" in ret:
            retMode = "all-0"
        elif "all bits 1" in ret:
            retMode = "all-1"

        return(retMode)

    def core3h_time(self, board):
        '''
        Displays the current time of the active 1pps source

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")

        Return:
        Datetime containing the current UTC timestamp of the active 1PPS source
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,time" % (boardNum)
        ret = self.sendCommand(cmd)

        timestamp = None
        # 2019-02-21T15:09:21
        for line in ret.split("\n"):
                try:
                        line = line.strip()
                        timestamp = datetime.strptime(line,"%Y-%m-%dT%H:%M:%S")
                        break
                except ValueError:
                        continue

        return(timestamp)

    def core3h_timesync(self, board, timestamp=None):
        '''
        Performs time synchronization for the given core board.

        TODO: Finish method with code for manual setting of time
        TODO Discuss with Sven 3 sec offset between reported seconds and GPS time
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,timesync" % (boardNum)

        if (timestamp):
            datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S')
            cmd += "," + datetime


        ret = self.sendCommand(cmd)

        lines = ret.split("\n")
        entry = {}
        #halfYearsSince2000 = 38
        #seconds = 3920060
        #daysSince2000 = 6940
        #Time synchronization succeeded!

        item = {}
        item["success"] = False


        if "succeeded" in ret:
            print (ret)
            timestamp = d3util.parseTimeResponse(ret)
            item["success"] = True
            item["timestampUTC"] = timestamp
            #print timestamp, datetime.now()

                
        return (item)

    def core3h_vdif_frame(self, board, channelWidth=None, numChannels=None, payloadSize=None):
        '''
        Gets / sets the VDIF frame properties for the specified Core3H board

        If the command is called without the channelWidth parameter the current
        properties will be returned.

        If successful the command returns the resulting number of frames per second
        and the number of data threads, according to the currently selected input
        (see core3h_inputselect for details).
        If the VDIF frame properties do not match the currently selected input the
        "compatible" flag in the return dictionary is set to "False". The command
        fails if the desired frame setup is not supported. The frame setup is not
        changed in this case.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        channelWidth (optional): the size of each channel in bits (allowed values: 1,2,4,8,16,32,64)
        numChannels (optional): number of channels per VDIF frame (allowed values: 1,2,4,8,16,32,64,128)
        payloadSize (optional): the total payload size in bytes (=frame size without header) of the VDIF frame

        Return:
        Dictionary with the following keys:
            "compatible"    (False in case an incomaptible setup was requested)
            "channelWidth"
            "numChannels"
            "payloadSize"
            "frameSize"
            "numThreads"      (optional)
            "framesPerSecond" (optional)
            "framesPerThread" (optional)
            
        
        Exception:
        ValueError: in case channelWidth has been specified but no numChannels were set
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,vdif_frame" % (boardNum)
        
        if channelWidth:
            cmd += " %d" % (int(channelWidth))
            if numChannels:
                cmd += " %d" % (int(numChannels))
                if payloadSize:
                    cmd += " %d" % (int(payloadSize))
            else:
                raise ValueError("core3h_vdif_frame: missing numChannels parameter")

        ret = self.sendCommand(cmd)
        if "Failed" in ret:
            return(None)

        # VDIF Frame properties:
        # channel width (in bits)        : 2
        # number of channels per frame   : 16
        # payload size (in bytes)        : 8192
        # => frame size (in bytes)       : 8224
        # => number of frames per second : 27 (16bit@54000Hz)
        # => number of data threads      : 1
        # => number of frames per thread : 27 (16bit@54000Hz)
        response = {}
        response["compatible"] = True
        for line in ret.split("\n"):

            if "WARNING: current frame setup is not compatible with selected input!" in line:
                response["compatible"] = False

            tok = line.split(":")
            if len(tok) == 2:
                if "channel width" in tok[0]:
                    response["channelWidth"] = int(tok[1])
                elif "number of channels" in tok[0]:
                    response["numChannels"] = int(tok[1])
                elif "payload size" in tok[0]:
                    response["payloadSize"] = int(tok[1])
                elif "frame size" in tok[0]:
                    response["frameSize"] = int(tok[1])
                elif "number of frames per second" in tok[0]:
                    response["framesPerSecond"] = int(tok[1].strip().split(" ")[0])
                elif "number of data threads" in tok[0]:
                    response["numThreads"] = int(tok[1])
                elif "number of frames per thread" in tok[0]:
                    response["framesPerThreads"] = int(tok[1].strip().split(" ")[0])
                    
        return(response)

    def core3h_vdif_station(self, board, stationId=None):
        '''
        Gets / sets the VDIF station ID for the specified Core3h board

        Note: setting this value directly affects the header data of 
        the VDIF data format

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        stationId (optional): The two-letter station code to set

        Return:
        String containing the two-letter station code; "unknown" if the
            code could not be determined

        Exception:
        ValueError: in case an illegal station code has been specified
        
        '''

        boardNum = self.boardToDigit(board)+1


        code = "unknown"

        cmd = "core3h=%d,vdif_station" % (boardNum)
        if stationId is not None:
            if len(stationId) > 2:
                raise ValueError("core3h_vdif_station: stationId must be two-letter code")
            cmd += " " + stationId
            
        ret = self.sendCommand(cmd)

        #VDIF station ID : 'NA'
        for line in ret.split("\n"):
            if "VDIF station ID" in line:
                code = line.split(":")[1].replace("'","").strip()

        return(code)

    def core3h_vdif_enc(self, board):
        '''
        Get the setting of the VDIF encoding switch.

        If enabled the VSI input data is encoded as mandated by the VDIF standard.
        If disabled the input data remains unmodified.
    

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")

        Return:
        on: if VDIF encoding is enabled
        off : if VDIF encoding is disabled
        unknown: in case the encoding setting could not be determined
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,vdif_enc" % (boardNum)
        ret = self.sendCommand(cmd)

        if "on" in ret:
            return("on")
        elif "off" in ret:
            return("off")
        else:
            return("unknown")
        
    def core3h_vdif_userdata(self, board, d0=None, d1=None, d2=None, d3=None):
        '''
        Gets/sets the user data fields in the extended VDIF frame header

        The user data fields are 32bit values. Note that bits 24-31 of the
        first user data field contain the Extended Data Version (EDV) number.
        See: https://vlbi.org/vdif/ for details

        d0 - d3 are optional. If not specified the current value of the field is kept.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A") 
        d0 (optional): the value of the first user data field
        d1 (optional): the value of the second user data field
        d2 (optional): the value of the third user data field
        d3 (optional): the value of the fourth user data field

        Return:
        List containing the current content of all 4 user data fields

        Exception:
        ValueError: in case the supplied value cannot be represented as hexadecimal
        ValueError: in case the length of the supplied value exceeds 32 bit
        '''
        boardNum = self.boardToDigit(board)+1

        # first obtain current user data field contents
        current = self._getVdifUserdata(board)
        
        values = ""
        for i in range(4):
            x = eval("d"+str(i))
            if x:
                valStr = self._valueToHex(x)
                if (int(valStr, 16) > 0xffffffff):
                    raise ValueError("core3h_vdif_userdata: value exceeds 32 bit length")
                values += " " + valStr
            else:
                values += " " + current[i]

        cmd = "core3h=%d,vdif_userdata %s" % (boardNum, values)
        ret = self.sendCommand(cmd)

        userdata = self._getVdifUserdata(board)

        return(userdata)

        
    def core3h_destination(self, board, outputId ,ip="", port=46227, threadId=-1):
        '''
        Sets / gets the output destination address and port for the given board and outputId.

        If called without specifying only the outputId the current destination settings are returned.

        When the ip parameters is set to None the respective output is disabled and no frames will be sent.

        When specifying a threadId only frames from that thread are addressed to the given destination.
        Other threads will not be affected. This is useful when using multi-threaded VDIF. Likewise
        a single thread can be disabled by setting ip=None and specifying a threadID.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        outputId: the index of the Core3h output (starting at 0)
        ip: the destination IP address 
        port (optional): the destination IP port number (default = 46227)
        threadId: the id of the tread for which to set the destination
        
        Return: 
        Dictionary containing keys: "ip","port","output".
        In case thread destinations have been set additional keys exist: e.g. "thread_0" holding a dict with ip and port information

        '''

        boardNum = self.boardToDigit(board)+1
        
        if threadId >= 0:
            threadStr = str(threadId)
        else:
            threadStr = ""

        #setter part
        if ip is None:
            cmd = "core3h=%d,destination %s none %s" % (boardNum, outputId, threadStr)
            ret = self.sendCommand(cmd)
        elif ip != "":
            cmd = "core3h=%d,destination %s %s:%s %s" % (boardNum, outputId, ip, port, threadStr)
            ret = self.sendCommand(cmd)

        #getter part (always executed even after setting destination
        cmd = "core3h=%d,destination %s" % (boardNum, outputId)
        ret = self.sendCommand(cmd)

        #Output 1 destination: 192.168.1.3:46227
        pat1 = re.compile("\s*Output\s+(\d+)\s+destination:\s+(\d+\.\d+\.\d+\.\d+):(\d+)")

        #Output 1 destination: none
        pat2 = re.compile("\s*Output\s+(\d+)\s+destination:\s+none")
        #pat2 = re.compile("\s*Output\s+(\d+):\s+destination of data thread (\d+) rewritten to (\d+\.\d+\.\d+\.\d+):(\d+)")

        #Data thread [0] -> 192.168.1.100:46338
        pat3 = re.compile("\s*Data thread\s+\[(\d+)\]\s+->\s+(\d+\.\d+\.\d+\.\d+):(\d+)")
        
        entry = {}
        for line in ret.split("\n"):
            match1 = pat1.match(line) 
            match2 = pat2.match(line) 
            match3 = pat3.match(line) 
            if match1:
                entry["output"] = match1.group(1)
                entry["ip"] = match1.group(2)
                entry["port"] = match1.group(3)
            elif match2:
                 entry["output"] = match2.group(1)
                 entry["ip"] = None
                 entry["port"] = None
            elif match3:
                thread = {}
                thread["ip"] = match3.group(2)
                thread["port"] = match3.group(3)
                entry["thread_%s"%(match3.group(1))] = thread

        return(entry)


    def core3h_tengbinfo(self, board, device):
        '''
        Retrieve the current parameters of the specified 10Gb ethernet device
        
        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        device: the ethernet device name, e.g. eth0

        Return:
        a dictionary containing all configuration parameters as key/value pairs. The arp_cache
             key contains a list of arp entries ("mac","ip")

        Exception:
        ValueError: in case an unknown ethernet device has been given
        '''

        response = {} 
        arpTable = []
        boardNum = self.boardToDigit(board)+1
        ret = self.sendCommand("core3h=%d,tengbinfo %s " % (boardNum, device))

        if "not found" in ret:
            raise ValueError("Unkown ethernet device specified (%s) in call to core3h_tengbinfo." % (device))

        pattern = re.compile("\s+(..:..:..:..:..:..)\s+(\d+\.\d+\.\d+\.\d+)")
        for line in ret.split("\n"):
            # first parse normal configuration key/value pairs
            tok = line.split(":")
            if len(tok) == 2 or "MAC address" in tok[0]:
                if "Configuration information" in tok[0]:
                    continue

                # reformat key; make lower case; replace spaces by underscore; remove .
                key = (' '.join(tok[0].split())).replace(" ", "_",1).replace(".","").lower()
                value = ":".join(tok[1:]).strip()
                response[key] = value
                continue

            # now parse arp table
            # MAC               IP
            # BA:DC:AF:E4:BE:E2 192.168.1.0
            match = pattern.match(line)
            if match:
                entry = {}
                entry["mac"] = match.group(1)
                entry["ip"] = match.group(2)
                arpTable.append(entry)

        response['arp_cache'] = arpTable 
        return(response)

    def core3h_tengbcfg(self, board, device, key, value):
        '''
        Sets a parameter of the 10Gb ethernet device.

        valid parameters are:
        ip: IP address
        mac: MAC address
        nm: netmask
        port:  UDP port
        gateway: IP adress of gateway

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        device: the ethernet device name, e.g. eth0
        key: the name of the parameter to set
        value: the new parameter value

        Return:
        True
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,tengbcfg %s %s=%s" % (boardNum, device, str(key), str(value))
        ret = self.sendCommand(cmd)

        return(True)

    def core3h_tengbarp(self, board, device, arpId, mac):
        '''
        Sets one ARP entry for a 10Gb ethernet device

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        device: the ethernet device name, e.g. eth0
        arpId: index of the ARP table entry to be modified
        mac: MAC address to be set

        Return:
        True

        Exception:
        ValueError in case an invalid MAC address was given
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateMAC(mac)
        
        cmd = "core3h=%d,tengbarp %s %d %s" % (boardNum, device,arpId, mac)
        ret = self.sendCommand(cmd)
        
        return(True)

    def core3h_arp(self, board, mode=None):
        '''
        Enables or disables ARP queries on all ethernet cores.

        If called without the mode parameter the current setting is reported

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        mode (optional): Can be "on" or "off". 

        Return:
        String containing the current ARP mode ("on" / "off")

        Exception:
        ValueError: in case an illegal mode has been requested
        '''

        boardNum = self.boardToDigit(board)+1
        
        arpMode = "unknown"
        cmd = "core3h=%d,arp " % (boardNum)
        if mode:
            if mode not in ["on","off"]:
                raise ValueError("Illegal arp mode (%s). Must be on or off." % (mode))
            cmd += mode
        ret = self.sendCommand(cmd)

        # ARP requests: off (during data transfer)
        pattern = re.compile("\s+ARP requests:\s+(.*)")
        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                if "on" in match.group(1):
                    arpMode = "on"
                elif  "off" in match.group(1):
                    arpMode = "off"
                


        return (arpMode)
        
    def core3h_start(self, board, format="vdif", force=False):
        '''
        Starts/restart sending of formatted output data
        
        The output data format can be either:
        vdif:   VDIF format
        raw:    unformatted
        
        In case a single output format is given, this will be used for all outputs.
        Formats can be set for each of the outputs individually by separating
        the format specifiers by "+" e.g. vdif+raw+vdif+raw
        if not explictely specified "vdif" will be used for all outputs.

        Raw format requires no time synchronization whereas vdif format requires
        the respective timer to be synchronized (see core3h_timesync)

        For fast testing: set the force parameter to True to automatically synchronize the
        timer to "zero" time(='2000-01-01T00:00:00'). Provided that a valid 1PPS signal
        is available this will always be successful.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        format (optional): a single format specifier or several concatenated by +. Default is "vdif"
        force (optional): if set to True synchronize time to '2000-01-01T00:00:00'. Default is False

        Return:
        List containing the format specifiers for all outputs

        Exceptions:
        ValueError: in case the number of format specifiers exceed the number of available outputs
        ValueError: in case an unkown format specifier was given
        '''
        boardNum = self.boardToDigit(board)+1

        outFormats = [""] * 4

        formats = format.split("+")
        if len(formats) > self.config.numCore3hOutputs:
            raise ValueError("Too many output formats specified to core3h_start. Maximum number of outputs is %d" % (self.config.numCore3hOutputs))
        for form in formats:
            self._validateDataFormat(form)

        cmd = "core3h=%d,start %s " % (boardNum, format)
        if force:
            cmd += "force"
        ret = self.sendCommand(cmd)
        # Output 0 format selected: vdif
        
        pattern = re.compile("\s+Output\s+(\d)\s+format selected:\s+(.*)")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                outFormats[int(match.group(1))] = match.group(2)

        return(outFormats)

    def core3h_stop(self, board):
        '''
        Stops sending of output data

        The opposite of core3h_start

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''

        boardNum = self.boardToDigit(board)+1
        ret = self.sendCommand("core3h=%d,stop" % (boardNum))
        for line in ret.split("\n"):
            if "Stopped" in line:
                return(True)
        return(False)
        

    def core3h_output(self, board, outputIdx=0, frameId=0, duration=1):
        '''
        Displays output debug information.

        The command displays the first 16 words of the first frame that was sent
        within the current second interval. The frame is recorded at the output
        with the given outputIndex. 1PPS/frame-header/end-of-frame/frame-drop bits
        attached to the stream are displayed together with the data.
        If duration is given, a new frame is displayed every second. The debug sequence
        can be cancelled by pressing <space> or <enter>.
        '''

        boardNum = self.boardToDigit(board)+1
        cmd = "core3h=%d,output %d %d %d" %(boardNum, outputIdx, frameId, duration)
        ret = self.sendCommand(cmd)

        return(ret)

    def core3h_reset(self, board, keepsync=False):
        '''
        Resets FiLa10G datapathand erases the syncronized time (optional)

        If called without arguments the complete datapath is reset and time 
        synchonization is lost.
        If called with keepsync=True, FiLa10G tries to maintain the current 
        time synchronization. For this to work the input stage of the data path
        and the timers are not reset.
        Warning:  Time synchronization will not be correct
        anymore in the rare but possible case that a data sample with a 1PPS
        flag is lost during the reset process.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        keepsync (optional): keeps the time synchronization if set to True. Default=False

        Return:
        True: if successful
        False: otherwise
        '''
        
        boardNum = self.boardToDigit(board)+1
    
        cmd = "core3h=%d,reset " %(boardNum)
        if keepsync:
            cmd += "keepsync"
        ret = self.sendCommand(cmd)

        for line in ret.split("\n"):
            if ("Reset done" in line):
                return(True)

        return(False)

    def core3h_reboot(self, board):
        '''
        Reboots the system. The FiLa10G hardware and software for the given board is reset to 
        its initial state, i.e. as it was directly after the programming of the FPGA and
        lets the FiLa10G system boot again.
        Warning: all previously configured settings and states are lost when rebooting!

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")

        Return:
        True: if successful
        False: otherwise
        '''

        boardNum = self.boardToDigit(board)+1
        ret = self.sendCommand("core3h=%d,reboot" %(boardNum))

        for line in ret.split("\n"):
            if ("not connected" in line):
                return(False)
        return(True)

        
    def core3h_core3_init(self, board):
        '''
        Initializes the given core3h board and sets parameters as specified in 
        the control file.

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")

        Return:
        True if successful
        False otherwise
        '''
        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,core3_init " % (boardNum)

        ret = self.sendCommand(cmd)
        for line in ret.split("\n"):
            if "Reset done" in line:
                return(True)

        return(False)

    def core3h_core3_mode(self, board, mode=None):
        '''
        Gets or sets the Core3h mode.
        If the optional mode parameter is ommited the currently set mode is returned.
        If given, mode must be a valid Core3h mode (as listed in DBBC3Config.core3hModes)

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        mode (optional): if ommited gets the currently active mode

        Return:
        A string containing the currently set mode
        '''

        retMode = ""
        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,core3_mode " % (boardNum)
        if mode:
            self._validateCore3hMode(mode)
            cmd += mode
        
        ret = self.sendCommand(cmd)
        for line in ret.split("\n"):
            if "data from all samplers is merged" in line:
                retMode="merged"
            elif "data from two samplers is merged" in line:
                retMode="half_merged"
            elif "data from each sampler is sent to a different output" in line:
                retMode="independent"
            elif "data from pfb" in line:
                retMode="pfb"

        return(retMode)
        
    def core3h_version(self, board):
        ''' 
        Displays the firmware version

        TODO: Discuss with Sven the future format of the version output and implement parsing code

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,version" % (boardNum))

    def core3h_sysstat(self, board):
        ''' 
        Displays information about the current status of the system and
        gives an overviewof the state of the most important user 
        settings.

        TODO: add parsing code and return dictionary with values

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")

        Returns: The output of the sysstat command
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

    def core3h_core3_bstat(self, board, sampler):
        '''
        Obtains the 2-bit sampler statistics for the given core board 
        and sampler.

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A
        sampler: the sampler number (starting at 0)


        Returns:
        List containing the 4 levels
        None: if the core board is not connected
        '''

        boardNum = self.boardToDigit(board) +1
        boardId = self.boardToChar(board)

        self._validateSamplerNum(sampler)

        bstats = []
        ret = self.sendCommand("core3h=%s,core3_bstat %d" % (boardNum,sampler))

        if "not connected" in ret:
                return(None)

          #P("11") = 9.64% (6171370)
          #P("10") = 41.70% (26691866)
          #P("01") = 40.36% (25836378)
          #P("00") = 8.28% (5300386)

        pattern = re.compile("\s*P\(\"(\d\d)\"\)\s*=\s*(\d+\.\d+)%\s+\((\d+)\)")
        for line in ret.split('\n'):
            #print (line)
            match = pattern.match(line)
            if (match):
                #print (match.group(3))
                bstats.append(int(match.group(3)))

        # evaluate the registers that contain the statistics
        #bstats.append(self.core3h_regread(boardNum-1, 5))
        #bstats.append(self.core3h_regread(boardNum-1, 6))
        #bstats.append(self.core3h_regread(boardNum-1, 7))
        #bstats.append(self.core3h_regread(boardNum-1, 8))
        #print (bstats)

        return (bstats)

    def core3h_core3_power(self, board):
        '''
        Obtains the gains of all 4 samplers of the given board

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A

        Return:
        List containing the gains for all samplers (a[0] = sampler1 etc.)
        None:  in case the core3 board is not connected
        '''

        boardNum = self.boardToDigit(board) +1

        pow = []
        ret = self.sendCommand("core3h=%d,core3_power" % (boardNum))

        if "not connected" in ret:
                return None

        #CORE3 input bit statistics:
        #Power at sampler 0 = 65053929
        #Power at sampler 1 = 99624764
        #Power at sampler 2 = 77772775
        #Power at sampler 3 = 110169325
        pattern = re.compile("\s*Power\s+at\s+sampler\s+(\d)\s+=\s+(\d+)")
        for line in ret.split('\n'):
            #print (line)
            match = pattern.match(line)
            if (match):
                #print (match.group(3))
                pow.append(int(match.group(2)))

        #pow.append(self.core3h_regread(boardNum-1, 5))
        #pow.append(self.core3h_regread(boardNum-1, 6))
        #pow.append(self.core3h_regread(boardNum-1, 7))
        #pow.append(self.core3h_regread(boardNum-1, 8))

        return(pow)

    def core3h_core3_corr(self, board):
        '''
        Performs cross-correlation between the samplers of the given board. Correlation
        products are between these samplers:
        1) 0-1
        2) 1-2
        3) 2-3 
        
        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A
        
        Return:
        List containing the three cross-correlations in the order described above
        '''

        corr = [0] * 3 
        boardNum = self.boardToDigit(board) +1

        ret = self.sendCommand("core3h=%s,core3_corr" % (boardNum))

        for line in ret.split("\n"):
            if "0-1" in line:
                corr[0] = int(line.split(":")[1].strip())
            elif "1-2" in line:
                corr[1] = int(line.split(":")[1].strip())
            elif "2-3" in line:
                corr[2] = int(line.split(":")[1].strip())

        return(corr)



    # ADB3L commands
    def adb3l_reset(self):
        '''
        Resets all ADB3L boards and sets the registers to default values
        '''
        return self.sendCommand("adb3l=reset")

    def adb3l_reseth(self):
        '''
        Resets all ADB3L boards, but does NOT change/reset any register settings
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
        self._validateSamplerNum(sampler)

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
        self._validateSamplerNum(sampler)
    
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
        self._validateSamplerNum(sampler)

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
        self._validateSamplerNum(sampler)

        if value < 0 or value>255:
            raise ValueError("sampler gain value must be in the range 0-255")

        cmd = "adb3l=gain=%d,%d,%d" % (boardNum, sampler,value)

        return self.sendCommand(cmd)

class DBBC3Commandset_DDC_V_123(DBBC3CommandsetDefault):
    '''
    Implementation of the DBBC3 Commandset for the 
    DDC_V mode version 123
    '''

    def __init__(self, clas):

        DBBC3CommandsetDefault.__init__(self,clas)

        clas.dbbc = types.MethodType (self.dbbc.__func__, clas)
        clas.dbbcgain = types.MethodType (self.dbbcgain.__func__, clas)
        clas.dbbcstat = types.MethodType (self.dbbcstat.__func__, clas)
        clas.cont_cal = types.MethodType (self.cont_cal.__func__, clas)
        clas.dbbctp = types.MethodType (self.dbbctp.__func__, clas)
        clas.dsc_tp = types.MethodType (self.dsc_tp.__func__, clas)
        clas.dsc_corr = types.MethodType (self.dsc_corr.__func__, clas)
        clas.dsc_bstat = types.MethodType (self.dsc_bstat.__func__, clas)
        clas.mag_thr = types.MethodType (self.mag_thr.__func__, clas)
        clas.pps_sync = types.MethodType (self.pps_sync.__func__, clas)
        clas.pps_delay = types.MethodType (self.pps_delay.__func__, clas)

    def dbbc(self, bbc, freq=None, bw=None, ifLabel=None, tpint=None):
        ''' 
        Gets / sets the parameters of the specified BBC.

        Parameters:
        bbc the BBC number (starts at 1) 
        freq (optional): the BBC frequency. If not specified the current setting is returned
        ifLabel (optional): the IF label to be used for the BBC (relevant e.g. for FS log). Must be single letter a-h.
        tpint (optional): total power integration time in seconds (default = 1 second)

        Return:
        dictionary containting the settings of the specified BBC

        Exception:
        ValueError: in case an invalid BBC number has been specified
        ValueError: in case an invalid BBC frequency has been specified
        ValueError: in case an invalid tpint value has been specified
        '''

        self._validateBBC(bbc)

        if (ifLabel):
            ifLabel = ifLabel.lower()
            if (ifLabel not in str("abcdefgh")):
                raise ValueError("dbbc: ifLabel must be one of abcdefgh")

        cmd = "dbbc{:02d}".format(bbc)
        if (freq):
            self._validateBBCFreq(freq)
            cmd += "=%f,%s" %(freq, ifLabel)
            
        if (tpint):
            self._validateTPInt(tpint)
            cmd += "=%f,%s,32,%d" % (freq, ifLabel,tpint)

        ret = self.sendCommand(cmd)

        return(ret)

    def dbbcgain(self, bbc, mode=None, target= None, gainU=None, gainL=None):
        '''
        Gets / sets the gain levels and gain control mode for a single BBC.

        If the command is called with only the bbc parameter set the current
        settings will be returned.

        If the command is being called with the mode=agc the automatic gain control is switched on. If the target parameter
        is also set then the levels are automatically adjusted to reach the given target otherwise the target specified in the
        DBBC configuration file is being used.

        If the command is being called with mode=man the automatic gain control is switched off and the current gain levels are being frozen. In case
        also the gainU and gainL parameters are set then these values will be used as the gain levels for the USB and LSB respectively.

        Parameters:
        bbc: the BBC number (starts at 1) 
        mode (optional): the gain control mode. Can be "agc" (automatic gain control) or "man" to freeze the current gain settings.
        target (optional): the target count level when running in "agc" mode
        gainU (optional): the gain level for the USB
        

        Return:
        Dictionary with the following keys:
            "bbc"         The currently selected BBC number (starts at 1)
            "mode"        The currently selected mode 
            "target"      The current target count level (only returned when mode=agc)
            "gainUSB"     The gain level of the USB
            "gainLSB"     The gain level of the LSB

        Exception:
        ValueError: in case an invalid BBC number has been specified

        '''
        resp = {}
        validModes = ["agc","man"]

        if (bbc != "all"):
            self._validateBBC(bbc)
            cmd = "dbbcgain=%d" % (bbc)
        else:
            cmd = "dbbcgain=all"
            raise ValueError("dbbcgain: bbc=all is currently not supported")

        if (target):
            try:
                target=int(target)
            except:
                raise ValueError("dbbcgain: target must be a positive integer")
        if (gainU):
            try:
                gainU = int(gainU)
            except:
                raise ValueError("dbbcgain: gainU must be a positive integer")
        if (gainL):
            try:
                gainL = int(gainL)
            except:
                raise ValueError("dbbcgain: gainL must be a positive integer")

        if (mode):
            mode = mode.strip()
            if (mode not in validModes):
                raise ValueError("dbbcgain: mode must be one of " + str(validModes))

            if (mode == "agc"):
                cmd += ",agc" 
                if (target):
                    cmd += ",%d" % target
            elif (mode == "man"):
                if (gainU):
                    cmd += ",%d" % int(gainU)
                    if (gainL):
                     cmd += ",%d" % int(gainL)
                else:
                    cmd += ",man"

        ret = self.sendCommand(cmd)

        if ("agc" in ret):
            # dbbcgain/ 1,83,74,agc,15000;
            patStr = "dbbcgain\/\s+(.+),(\d+),(\d+),(.+),(\d+);" 
        else:
            # dbbcgain/ 1,83,74,man;
            patStr = "dbbcgain\/\s+(.+),(\d+),(\d+),(.+);" 
            
        pattern = re.compile(patStr)
    
        for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                    resp['bbc'] = int(match.group(1))
                    resp['gainUSB'] = int(match.group(2))
                    resp['gainLSB'] = int(match.group(3))
                    resp['mode'] = match.group(4)
                    if (match.group(4) == "agc"):
                        resp['target'] = int(match.group(5))

        return(resp)

    def dbbcstat(self, bbc):

        self._validateBBC(bbc)

        cmd = "dbbcstat=%d" % (bbc)
        ret = self.sendCommand(cmd)

        return(ret)

    def cont_cal(self, mode, polarity, freq, option):

        self._validateOnOff(mode)

        cmd = "cont_cal=%s" % (mode)
        ret = self.sendCommand(cmd)

        return(ret)

    def dbbctp(self, board):

        board = self.boardToChar(board).lower()
        cmd = "dbbctp%s" % (board)
        ret = self.sendCommand(cmd)

        return(ret)

    def dsc_tp(self, board):
        '''
        Reads the DSC total power values for
        all four samplers of the selected board

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A

        Returns: an array holding the TP values for all four samplers
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "dsc_tp=%d" % (boardNum)
        ret = self.sendCommand(cmd)

        values = []
        #TP[2][0] = 69948
        patStr = "TP\[%d\]\[[0123]\]\s+=\s+(\d+)" % (board+1)
        pattern = re.compile(patStr)

        for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                    values.append(int(match.group(1)))


        return(values)
        
    def dsc_corr(self, board):
        '''
        Performs cross-correlation between the samplers of the given board. Correlation
        products are between these samplers:
        1) 0-1
        2) 1-2
        3) 2-3
        The values can be used to check if the samplers are in the correct phase (=synchronized).
        Note: The absolute numbers returned depend on the input power and IF bandwidth. However the
        values of one board should not deviate by more than 10%.

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A

        Returns:
        List containing the three cross-correlations in the order described above
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "dsc_corr=%d" % (boardNum)
        ret = self.sendCommand(cmd)

        corr = [0] * 3
        # Correlation board 1:
        # [0-1]: 157322344
        # [1-2]: 155710069
        # [2-3]: 158944035;
        for line in ret.split("\n"):
            if "0-1" in line:
                corr[0] = int(line.split(":")[1].strip())
            elif "1-2" in line:
                corr[1] = int(line.split(":")[1].strip())
            elif "2-3" in line:
                corr[2] = int(line.split(":")[1].strip().replace(";",""))

        return(corr)

    def dsc_bstat(self, board, sampler):
        '''
        Determines DSC statistics of the given board and sampler

        Parameters:
        board: can be given as a number (0 = board A) or as char e.g. A
        sampler: the sampler number (0-3)

        Returns:
        list of dictionaries with the following keys:
        count:  count for the given state
        perc:   percentage for the given state

        the list indices are
        0: ++ state
        1: + state
        2: - state
        3: -- state

        return example:
        [{'count': 1413, 'perc': 9}, {'count': 6358, 'perc': 40}, {'count': 6392, 'perc': 40}, {'count': 1459, 'perc': 9}]
        
        '''

        boardNum = self.boardToDigit(board)+1

        self._validateSamplerNum(sampler)

        cmd = "dsc_bstat=%d, %d" % (boardNum, sampler)
        ret = self.sendCommand(cmd)

        pattern = re.compile("\[(\d\d)\]\s*=\s*(\d+),\s*(\d+)\%")
        # dsc_bstat/
        # Bstat[1][1]:
        # [11] =   1454,   9%
        # [10] =   6386,  40%
        # [01] =   6364,  40%
        # [00] =   1420,   9%;

        stat = [0] * 4
        for line in ret.split("\n"):
            line = line.strip().replace(";","")
            match = pattern.match(line)
            if (match):
                print (line)
                if (match.group(1) == "11"):
                    stat[0] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "10"):
                    stat[1] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "01"):
                    stat[2] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "00"):
                    stat[3] = {"count":int(match.group(2)), "perc":int(match.group(3))}

        return(stat)

    def mag_thr(self, bbc, value):

        self._validateBBC(bbc)

        cmd = "mag_thr=%d,%d" % (bbc, value)
        ret = self.sendCommand(cmd)

        return(ret)

    def pps_sync(self):

        cmd = "pps_sync"
        ret = self.sendCommand(cmd)

        return(ret)
    
    def pps_delay(self):

        cmd = "pps_delay"
        ret = self.sendCommand(cmd)

        #pps_delay/ [1]: 39 ns, [2] 39 ns, [3] 0 ns, [4] 0 ns, [5] 0 ns, [6] 0 ns, [7] 0 ns, [8] 0 ns;
        patStr = "pps_delay/"
        for i in range(8):
                patStr += "\s+\[(\d+)\]:{0,1}\s+(\d+)\s+ns,"
        patStr = patStr[:-1] + ";"
        pattern = re.compile(patStr)

        delays = []
        for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                        for i in range(self.config.numCoreBoards):
                                delays.append(int(match.group(2+i*2)))
                
        return(delays)

class DBBC3Commandset_DDC_V_124(DBBC3Commandset_DDC_V_123):

    def __init__(self, clas):

        DBBC3Commandset_DDC_V_123.__init__(self,clas)

    def pps_delay(self, board=None):
        '''
        Retrieves the delay of the internally generated vs. the external PPS signal for all core3H boards.

        Parameters:
        board: [optional] if specified returns the PPS values for the PPS groups (4 BBCs) of the given core3H board

        Returns:
        list holding the delays of the internal vs external PPS in nanoseconds for each core3H board
        '''

        cmd = "pps_delay"

        if (board is not None):
            boardNum = self.boardToDigit(board)+1

            cmd += "=%d" % boardNum;
            # pps_delay[1]/ [1]: 43 ns, [5] 43 ns;
            patStr = "pps_delay\[%d\]/" % boardNum
            numVals = int(self.config.maxBoardBBCs / 4)
            retVals = numVals
        else:
            #pps_delay/ [1]: 39 ns, [2] 39 ns, [3] 0 ns, [4] 0 ns, [5] 0 ns, [6] 0 ns, [7] 0 ns, [8] 0 ns;
            patStr = "pps_delay/"
            numVals = 8
            retVals = self.config.numCoreBoards

        ret = self.sendCommand(cmd)
        #print ret

        for i in range(numVals):
                patStr += "\s+\[(\d+)\]:{0,1}\s+(\d+)\s+ns,"
        patStr = patStr[:-1] + ";"
        pattern = re.compile(patStr)

        delays = []
        for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                        for i in range(retVals):
                                delays.append(int(match.group(2+i*2)))
        return(delays)


    
class DBBC3Commandset_OCT_D_110(DBBC3CommandsetDefault):

    def __init__(self, clas):

        DBBC3CommandsetDefault.__init__(self,clas)

        clas.tap = types.MethodType (self.tap.__func__, clas)
        clas.tap2 = types.MethodType (self.tap2.__func__, clas)


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

            
class DBBC3Commandset_DDC_U_125(DBBC3Commandset_DDC_V_124):
    '''
    Implementation of the DBBC3 Commandset for the
    DDC_U mode version 125
    '''

    def __init__(self, clas):
        '''
        For now use the DDC_V_124 commandset
        '''

        DBBC3Commandset_DDC_V_124.__init__(self,clas)


#class DBBC3Commandset_OCT_D_120(DBBC3Commandset):
#    pass
#class DBBC3Commandset_OCT_D_150(DBBC3Commandset):
#   pass
#class DBBC3Commandset_OCT_D_220(DBBC3Commandset):
#    pass

