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
This module is part of the DBBC3 package and implements the command sets
of the DBBC3 for the various modes and versions
'''

__author__ = "Helge Rottmann"
__copyright__ = "2021, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

import dbbc3.DBBC3Util as d3u
import types 
import re
import time
import importlib
import inspect
import sys
from datetime import datetime
from dbbc3.DBBC3Exception import DBBC3Exception

def getMatchingCommandset(mode, majorVersion):
    '''
    Determines the command set sub-class to be used for the given mode and major version.

    if mode is not given the default command set class (DBBC3CommandsetDefault) is selected
    if majorVersion is not given the latest implemented version for the activated mode will be used.

    Args:
        mode (str): the dbbc3 mode (e.g. OCT_D)
        majorVersion (str): the command set major version

    Returns:
        str: The class name that implements the command set for the given mode and major version
    

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

    ret = "DBBC3Commandset_%s_%s" % (mode,pickVer)
    print ("Selecting commandset version: %s" % ret)

    return(ret)

class DBBC3Commandset(object):
    '''
    Base class for all DBBC3 commandset implementations

    Upon construction the appropriate sub-class implementing the command set for the given version and mode is determined 
    and dynamically attached.

    if version is not given the latest implemented version for the activated mode will be used.

    Args:
        clas (object): the class to which to attach the DBBC3Commandset
        version (str): the command set version

    '''

    def __init__(self,clas, version=None):
        

        majorVersion = ""
        mode = ""
        if version:
            majorVersion = version['majorVersion']
            mode = version['mode']
        

        csClassName = getMatchingCommandset(mode, majorVersion)
        #print ("Using commandset version: ", csClassName)
    
        if (csClassName == ""):
            csClassName = "DBBC3CommandsetDefault"

        CsClass = getattr(importlib.import_module("dbbc3.DBBC3Commandset"), csClassName)
        CsClass(clas)

    
class DBBC3CommandsetDefault(DBBC3Commandset):
    '''
    The basic class implementing all commands common to all DBBC modes and versions.

    All sub-classes implementing commands that are special to a specific mode or version 
    should be derived from DBBC3CommandsetDefault and should follow the class naming
    convention: DBBC3Commandset_MODE_VERSION
    e.g. DBBC3Commandset_OCT_D_110
    '''

    def __init__(self, clas):

        clas.version = types.MethodType (self.version.__func__, clas)
        #clas.dbbcif = types.MethodType (self.dbbcif.__func__, clas)
        #clas.enableloop = types.MethodType (self.enableloop.__func__, clas)
        clas.dbbcif = types.MethodType (self.dbbcif.__func__, clas)
        clas.enableloop = types.MethodType (self.enableloop.__func__, clas)
        clas.disableloop = types.MethodType (self.disableloop.__func__, clas)
        clas.enablecal = types.MethodType (self.enablecal.__func__, clas)
        clas.synthFreq = types.MethodType (self.synthFreq.__func__, clas)
        clas.synthLock = types.MethodType (self.synthLock.__func__, clas)
        clas.synthOen = types.MethodType (self.synthOen.__func__, clas)
        clas.synthAtt = types.MethodType (self.synthAtt.__func__, clas)
        clas.checkphase = types.MethodType (self.checkphase.__func__, clas)
        clas.time = types.MethodType (self.time.__func__, clas)
        clas.reconfigure = types.MethodType (self.reconfigure.__func__, clas)
        #clas.cal_offset = types.MethodType (self.cal_offset.__func__, clas)
        #clas.cal_gain = types.MethodType (self.cal_offset.__func__, clas)
        #clas.cal_delay = types.MethodType (self.cal_offset.__func__, clas)
        clas.adb3linit = types.MethodType (self.adb3linit.__func__, clas)
        clas.core3hinit = types.MethodType (self.core3hinit.__func__, clas)
        clas.synthinit = types.MethodType (self.synthinit.__func__, clas)

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
#        clas.adb3l_biston = types.MethodType (self.adb3l_biston.__func__, clas)
#        clas.adb3l_bistoff = types.MethodType (self.adb3l_bistoff.__func__, clas)
#        clas.adb3l_SDA_on = types.MethodType (self.adb3l_SDA_on.__func__, clas)
        clas.adb3l_delay = types.MethodType (self.adb3l_delay.__func__, clas)
        clas.adb3l_offset = types.MethodType (self.adb3l_offset.__func__, clas)
        clas.adb3l_gain = types.MethodType (self.adb3l_gain.__func__, clas)


# GENERAL DBBC3 commands
    def version(self):
        ''' Returns the DBBC3 control software version.

        Returns:
            a dictionary containing the version information of the DBBC3 control software::

                "mode" (str): the current DBBC3 mode, e.g. DDC_V
                "majorVersion" (int): the major version, e.g. 124
                "minorVersion" (int): the minor version (format YYYYMMDD) e.g. 20200113
        '''

        resp = {}
        ret = self.sendCommand("version")

        # version/ DDC_V,124,October 01 2019;
        # version/ OCT_D,110,July 03 2019
        # version/ DDC_V,124,February 18th 2020;
        pattern = re.compile("version\/\s+(.+),(\d+),(.+?\s+.+?\s+\d{4});{0,1}")

        match = pattern.match(ret)
        if match:
            # remove any st/nd/rd/th from the date string
            amended = re.sub('\d+(st|nd|rd|th)', lambda m: m.group()[:-2].zfill(2), match.group(3))
            resp["mode"] = match.group(1)
            resp["majorVersion"] =  int(match.group(2))
            resp["minorVersion"] = int(datetime.strptime(amended, '%B %d %Y').strftime('%y%m%d'))

        return (resp)

    def time(self):
        '''
        Obtains the time information from all boards.

        For each board a dict with the following structure is returned::

            'timestamp' (time.struct_time): the timestamp
            'timestampAsString' (str): the timestamp in string representation %Y-%m-%dT%H:%M:%S

        In the OCT mode (version 110) the dict contains the following additional fields::

            'seconds'(int): seconds since the beginning of the current year
            'halfYearsSince2000' (int): number of half years since the year 2000
            'daysSince2000' (int): number of days since the year 2000

        Returns:
            time_list (:obj:`list` of :obj:`dict`): The list of time information dicts. One list element for every board (0=A).

        Raises:
            DBBC3Exception: in case no time information could be obtained


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
            elif "FiLa10G" in line: # new board entry
                if not entry:
                    raise DBBC3Exception("time: did not receive any time information for a board")
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
                
        if not resp:
            raise DBBC3Exception("time: Did not receive any time information")
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

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A
            inputType (int): 1 = IF input without downconversion; 
                       2 = IF input after downconversion
            mode (int or str): "agc" = automatic gain control (default if not specified); "man" = manual attenuation (retains last agc value); numeric value = attenuation step (0-63) in steps of 0.5 dB
            target (int): the target power level for the "agc" mode

        Returns:
            dictionary holding the values reported by dbbcif with the following structure::

            "inputType" (int): see parameter description for meaning of returned value
            "attenuation" (int): the current attenuation level
            "mode" (str): the current agc mode 
            "count" (int): the current IF level
            "target" (int): the target IF level

        Raises:
            ValueError: in case any arguments exceeds the valid range

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

                resp['inputType'] = int(match.group(1))
                resp['attenuation'] = int(match.group(2))
                resp['mode'] = match.group(3)
            #    resp['filter'] = int(match.group(4))   # no function for the DBBC3 do not return
                resp['count'] = int(match.group(5))
                resp['target'] = int(match.group(6))

        return ( resp )

    def reconfigure(self):
        '''
        Reconfigures the core3h boards 

        Reloads the firmware, then reinitializes the ADB3L and core3h and finally does a PPS sync.
        '''

        self.sendCommand("reconfigure")

    def adb3linit(self):
        '''
        Performs full reset of all ADB3L boards

        All ADB3L boards are fully reinitialized to the setting defined in the configuration file.

        Returns:
            boolean: True if the ADB3L boards were successfully reinitialized; False otherwise
        '''
        ret = self.sendCommand("adb3linit")

        # adb3linit/ Samplers initialized;
        pattern = re.compile("adb3linit\/\s*Samplers initialized;")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                return(True)

        return (False) 

    def core3hinit(self, board=None):
        '''
        Reinitializes the CORE3H board(s)

        If called without the optional board parameter reinitialization is performed for all CORE3H boards present
        in the system; otherwise only the specified board is bein initialized.
        The boards are reset to their default settings as specified in the configuration files. 

        Args:
            board (int or str, optional): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            boolean: True if the reinitialization was successful; False otherwise
        '''
        cmd = "core3hinit"
        
        if board:
            board = self.boardToDigit(board)
            cmd += "=%d" % board
        ret = self.sendCommand(cmd)

        #  core3hinit/ Core3H initialized;
        pattern = re.compile("core3hinit\/\s*Core3H initialized;")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                return(True)

        return (False)

    def synthinit(self):
        '''
        Reinitiliases the synthesizers

        All synthesizers of the GCoMo boards are reset to their initial state as defined in the configuration files

        Returns:
            boolean: True if the synthesizers were successfully reinitialized; False otherwise
        '''
        ret = self.sendCommand("synthinit")

        #  synthinit/ Synthesizers configured;
        pattern = re.compile("synthinit\/\s*Synthesizers configured;")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                return(True)

        return (False) 

        
#    def cal_offset(self, board):
#        '''
#        Calibrates the sampler offsets
#
#        Calibrates the offsets of the 4 samplers of the specified board. The corresponding
#        GCoMo should be set to maximum attenuation when executing the offset calibration
#
#        ToDo:
#            Write up calibration instructions and put a reference here
#
#        Args:
#            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
#    
#        '''

    def checkphase(self):
        '''
        Checks whether all samplers of all core boards are in sync

        Warning:
            Do not execute checkphase while observing/recording data! Data will be invalid while checkphase is running due to 
            phase shifting of the sampler outputs.

        In case one or more samplers are not in sync use lastResponse to receive information on the failed board(s)

        Returns:
            bool: True if all samplers are in sync, False otherwise
        '''
        ret = self.sendCommand("checkphase")

        if "out of sync" in ret:
                return(False)
        else:
                return(True)

    def synthLock(self, board):
        '''
        Gets the lock state of the GCoMo synthesizer serving the given core board

        Each sythesizer has two outputs (source=1 or 2)
        board A is served by synth 1 source 1
        board B is served by synth 1 source 2
        board C is served by synth 2 source 1
        etc.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
        Returns:
            boolean: True if the synthesizer is locked; False otherwise

        Raises:
            DBBC3Exception: in case the lock state of the synthesizer cannot be obtained
        '''

        board = self.boardToDigit(board)

        synthNum = int(board / 2) +1
        sourceNum = board % 2 + 1

        locked = [-1,-1,-1,-1]
        ret = self.sendCommand("synth=%d,lock" % synthNum)

        lines = ret.split("\n")
        for line in lines:
                if line.startswith("S1 not locked"):
                        locked[0]=False
                elif line.startswith("S1 locked"):
                        locked[0]=True
                if line.startswith("S2 not locked"):
                        locked[1]=False
                elif line.startswith("S2 locked"):
                        locked[1]=True
                if line.startswith("S3 not locked"):
                        locked[2]=False
                elif line.startswith("S3 locked"):
                        locked[2]=True
                if line.startswith("S4 not locked"):
                        locked[3]=False
                elif line.startswith("S4 locked"):
                        locked[3]=True
        if (locked[sourceNum-1] == -1):
            raise DBBC3Exception("Cannot determine synthesizer lock state of board %d" % (board))

        return locked[sourceNum-1]

    def synthFreq(self, board, freq=None):
        ''' 
        Gets / sets the frequency in MHz of the synthesizer serving the given board.
        
        If the freq parameter is not given or is set to None the current frequency is reported

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            freq (int, optional): the synthesizer frequency in MHz

        Returns:
            dict: A dictionary with the following structure::

                "target" (int): the target frequency in MHz
                "actual" (int): the actual frequency in MHz

        Raises:
            DBBC3Exception: In case the frequency could not be set or determined
        '''

        resp = {}
        boardNum = self.boardToDigit(board)

        # board A is served by synth 1 source 1
        # board B is served by synth 1 source 2
        # board C is served by synth 2 source 1
        # etc.
        synthNum = int(boardNum / 2) +1
        sourceNum = boardNum % 2 + 1

        # first enable the source of the given synthesizer corresponding to the selected board
        self.sendCommand("synth=%d,source %d" % (synthNum, sourceNum))
        cmd = "synth=%d,cw " % synthNum

        if freq is not None:
            # valon frequencies are half of the target value
            cmd += str(freq /2)

        ret = self.sendCommand(cmd)

        lines = ret.split("\n")
        # output: ['cw\r', 'F 4524 MHz; // Act 4524 MHz\r', '\r-2->']
        for line in lines:
                if "MHz" in line:
                        # F 4524 MHz; // Act 4524 MHz
                        tok = line.split(" ")
                        resp['target'] = float(tok[1]) * 2
                        resp['actual'] = float(tok[5]) * 2
        if not resp:
            raise DBBC3Exception("The synthesizer frequency for board %d could not be determined" % (board))

        return(resp)

    def synthOen (self, board, state=None):

        '''
        Enables/disables the synthesizer output that serves the given board.
    
        Warning:
            Disabling the output will switch off the downconversion stage of the DBBC3.

        If called without the state argument the current output setting is reported.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            state (str, optional): the output state. Can be either "on" or "off"

        Returns:
            int: the current state of the synthesizer output; 0=off, 1=off
            None: in case the state could not be determined

        Raises:
            ValueError: In case an illegal state argument has been supplied
        '''

        #print ("state: ", state)
        resp = {}
        boardNum = self.boardToDigit(board)

        # determine synthesizer and output for the given board
        synthNum = int(boardNum / 2) +1
        sourceNum = boardNum % 2 + 1

        cmd = "synth=%d,oen" % (synthNum)
        if state is not None:
            if not d3u.validateOnOff(state):
                raise ValueError("synthOen: state  must be 'on' or 'off'")
            if state == "on":
                cmd += " 1"
            else:
                cmd += " 0"

        # first enable the source of the given synthesizer corresponding to the selected board
        self.sendCommand("synth=%d,source %d" % (synthNum, sourceNum))
        ret = self.sendCommand(cmd)

        pattern = re.compile("\s*OEN\s+(\d)\s*;")
        # OEN 1;
        for line in ret.split("\n"):
                match =  pattern.match(line)
                if match:
                    return(match.group(1))

        return(None)

    def synthAtt (self, board):

        '''
        Gets the current attenuation setting of the synthesizer output serving the given board

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            float: the attenuation level in dB of the synthesizer ouput serving the given board
            
        '''

        resp = {}
        boardNum = self.boardToDigit(board)

        # determine synthesizer and output for the given board
        synthNum = int(boardNum / 2) +1
        sourceNum = boardNum % 2 + 1

        # first enable the source of the given synthesizer corresponding to the selected board
        self.sendCommand("synth=%d,source %d" % (synthNum, sourceNum))

        cmd = "synth=%d,att" % (synthNum)

        ret = self.sendCommand(cmd)

        # ATT 30.0; // dB
        # -2->;
        pattern = re.compile("\s*ATT\s+(\d+\.\d+)\s*;")
        for line in ret.split("\n"):
                match =  pattern.match(line)
                if match:
                    return(match.group(1))

        return (None)


    def enableloop(self):
        '''
        Starts the automatic calibration loop

        For changing the parameters of the calibration loop use the :py:func:`enablecal` method
        
        Returns:
            str: Response message from the control software
        '''
        return self.sendCommand("enableloop")

    def disableloop(self):
        '''
        Stops the automatic calibration loop

        Returns:
            str: Response message from the control software
        '''
        return self.sendCommand("disableloop")

    def enablecal(self, threshold="on", gain="off", offset="off"):
        '''
        Switches on/off  the threshold, gain and offset calibration for the automatic calibration loop

        The loop must be activated with the :py:func:`enableloop` command.
        If called without the optional parameters the defaults will be used (see below)

        Args:
            threshold (optional, default=on): switch threshold calibration [on/off]
            gain (optional, default=off): switch gain calibration [on/off]
            offset (optional, default=off): switch offset calibration [on/off]

        Returns:
            dict: a dictionary with the following structure::

                "threshold":
                "gain":
                "offset":
        Raises:
            DBBC3Exception: * if the state of the calibration loop could not be queried * if the reported state differs from what was requested

        '''

        #Calibration enabled:
        #threshold=ON
        #gain=OFF
        #offset=OFF
        threshold = threshold.lower()
        gain = gain.lower()
        offset = offset.lower()

        resp = {}
        ret = self.sendCommand("enablecal=%s,%s,%s" % (threshold,gain,offset))
        for line in ret.split("\n"):
            line = line.strip()
            try:
                (key,val) = line.split("=")
                resp[key] = val.lower()
            except:
                pass
        
        if not resp:
            raise DBBC3Exception("enablecal: the settings for the calibration loop could not be determined")

        if threshold != resp["threshold"]:
            raise DBBC3Exception("enablecal: requested threshold=%s, but received threshold=%s" % (threshold, resp["threshold"]))
        if gain != resp["gain"]:
            raise DBBC3Exception("enablecal: requested gain=%s, but received gain=%s" % (gain, resp["gain"]))
        if offset != resp["offset"]:
            raise DBBC3Exception("enablecal: requested offset=%s, but received offset=%s" % (offset, resp["offset"]))
                
        return (resp)

    # CORE3H commands

    def core3h_regread(self, board, regNum, device="core3"):
        '''
        Reads the value of the device register

        Note:
            Not all devices have readable registers. See the DBBC3 documentation for the core3h "devices" command.
            The list of available devices can be obtained with the :py:func:`core3h_devices` command.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            regNum (int): the index of the device register to read
            device (str): the name of the device (as returned by the :py:func:`core3h_devices` command). default = core3

        Returns:
            tuple (str,str,int): tuple containing::

                register value in hexadecimal string format
                register value in binary string format
                register value in decimal format (signed 32-bit)
        '''

        boardNum = self.boardToDigit(board) +1

        ret = self.sendCommand("core3h=%d,regread %s %d" % (boardNum, device, regNum))

        # 0xBFBFBFBF / 0b10111111101111111011111110111111 / -1077952577
        lines = ret.split("\n")
        for line in lines:
            fields = line.split("/")
            if len(fields) == 3:
                return hex(int(fields[0], 16)), bin(int(fields[1],2)), int(fields[2])

    def core3h_regread_dec(self, board, regNum, device="core3"):
        '''
        Reads the decimal value of the device register

        Note:
            Not all devices have readable registers. See the DBBC3 documentation for the core3h "devices" command.
            The list of available devices can be obtained with the :py:func:`core3h_devices` command.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            regNum (int): the index of the device register to read
            device (str): the name of the device (as returned by the :py:func:`core3h_devices` command). default = core3

        Returns:
            int: The decimal value of the device register
        '''

        boardNum = self.boardToDigit(board) +1

        ret = self.sendCommand("core3h=%d,regread_dec %s %d" % (boardNum, device, regNum))
        lines = ret.split("\n")

        return int(lines[2].strip())

    def core3h_regwrite(self, board, device, regNum, value):
        '''
        Writes a value into the device register

        Note:
            Not all devices have writeable registers. See the DBBC3 documentation for the core3h "devices" command.
            The list of available devices can be obtained with the :py:func:`core3h_devices` command.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            device (str): the name of the device (as returned by the :py:func:`core3h_devices` command). default = core3
            regNum (int): the index of the device register to read
            value (hex): the register value to write; must be a 32-bit hexadecimal string, e.g. 0x01020304

        Returns:
            boolean: True if value was changed; False otherwise

        Raises:
            ValueError: in case the supplied value is not in hex format
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

        Note:
             Not all devices have writable registers. See DBBC3 documentation for "devices" command

        The bitmask must be in hexadecimal format.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            device (str): the name of the device (as returned by the :py:func:`core3h_devices` command). default = core3
            regNum (int): the index of the device register to read
            value (hex): the register value to write; must be 32-bit hexadecimal string, e.g. 0x01020304
            bitmask (hex): the 32-bit hexadecimal bitmask; 1=overwrite 0=leave unchanged

        Returns:
            boolean: True if value was changed; False otherwise

        Raises:
            ValueError: in case the supplied value is not in hex format
            ValueError: in case the supplied bitmask is not in hex format
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
        
        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampleRate (int, optional): the input sampling rate in samples per second
            decimation (int, optional): a divisor in the range 1..255; default=1

        Returns:
            dict: dictionary with the following structure:: 

                "sampleRate" (int): sample rate in Hz
                "decimation" (int): decimation factor

    
        Raises:
            DBBC3Exception: in case the sample rate could not be set
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,vsi_samplerate" % (boardNum)
        if sampleRate:
            cmd += " %d %d" % (sampleRate, decimation)

        ret = self.sendCommand(cmd)

        if "Failed" in ret:
            raise DBBC3Exception("core3h_vsi_samplerate: Error setting vsi_samplerate (check lastResponse)" )

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

    def core3h_vsi_bitmask(self, board):
        '''
        Gets the vsi input bitmask.

        The eight - up to 32 bit wide - bitmasks specify which bits of the eight vsi input streams
        are active and will be processed. Inactivated bits will be discarded which effectively reduces
        the total amount of data.

        Note: 
            Currently setting of the bit mask is not supported by the python package

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
    
        Returns:
            list (str): a list of hex representations of the bitmasks for all active vsi inputs

        '''
        
        boardNum = self.boardToDigit(board)+1

#        if vsi is not None:
#            vsiStr = str(vsi)
#            if (not vsiStr.isdigit()):
#                ValueError("core3h_vsi_bitmask: vsi must be numeric")
#
#            if mask is None:
#                ValueError("core3h_vsi_bitmask: missing mask for vsi: %d" % (vsi))
#        else:
#            if mask is not None:
#                ValueError("core3h_vsi_bitmask: no vsi was specified")

#        if mask is not None:
#            valStr = self._valueToHex(mask)
#            if (int(valStr, 16) > 0xffffffff):
#                raise ValueError("core3h_vdif_bitmask: the supplied mask is longer than 32 bit")
#    
        cmd = "core3h=%d,vsi_bitmask" % (boardNum)
        ret = self.sendCommand(cmd)

        response = ""
        #VSI input bitmask : 0xFFFFFFFF 0xFFFFFFFF
        pattern = re.compile("\s*VSI input bitmask\s*:(\s+0x\d{8}.*)")
#        if "Failed" in ret:
#            raise ValueError("core3h_inputselect: Illegal source supplied: %s" % (source))

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                response = match.group(1).split()
        
        return(response)
        
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

        The command implicitly resets the VSI bitmask, input width and VSI swap settings to their
        respective defaults.

        The input width is reset to:
            * 32bit for tvg, vsi1 and vsi2  
            * 64bit for vsi1-2
            * 128bit for vsi1-2-3-4

        TODO: update the documentation
        TODO: Find out about "vsi1-2-3-4-5-6-7-8"

        Note:
            It is recommended to execute :py:func:`core3h_reset`
            (with or without the keepsync option) after changing the input source

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            source (str): one of "tvg","vsi1","vsi2","vsi1-2","vsi1-2-3-4","vsi1-2-3-4-5-6-7-8"

        Returns:
            str: the current split mode setting; "unknown" if the mode could not be determined

        Raises:
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

        Note:
            Raw and vdif format can be applied independently to each split
            stream with the help of the :py:func:`core3h_start` command syntax

        Note:
            In order to specify a correct VDIF frame setup you have to take
            into account that the effective input width is halved when the 
            split mode is enabled.

        Note:
            A restriction of the split mode is that only output0 is capable
            of producing multi-threaded VDIF data. At output1 the data will 
            always be forced to be single-threaded, regardless of the chosen frame setup.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            mode (str): "on" or "off"

        Returns:
            str: the current split mode setting ("on"/"off"); "unknown" if the mode could not be determined

        Raises:
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
        Gets / sets the test vector generator (tvg) mode for the given board.

        mode can be one of:
            * all-0:  all bits = 0
            * all-1:  all bits = 1
            * vsi-h:  VSI-H test vector pattern
            * cnt:    pattern with four 8-bit counters

        If called without the mode parameter the current setting is returned.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            mode (str): the tvg mode identifier (see above)
    
        Returns:
            str: the current tvg mode; "unknown" if the mode could not be determined

        Raises:
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

        The displayed time is the (synchronized) VDIF time in UTC format.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            datetime: the current UTC timestamp of the active 1PPS source
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
            #print (ret)
            timestamp = d3u.parseTimeResponse(ret)
            item["success"] = True
            item["timestampUTC"] = timestamp
            #print timestamp, datetime.now()

                
        return (item)

    def core3h_vdif_frame(self, board, channelWidth=None, numChannels=None, payloadSize=None):
        '''
        Gets / sets the VDIF frame properties for the specified core3H board

        If the command is called without the channelWidth parameter the current
        properties will be returned.

        If successful the command returns the resulting number of frames per second
        and the number of data threads, according to the currently selected input
        (see :py:func:`core3h_inputselect` for details).

        If the VDIF frame properties do not match the currently selected input the
        "compatible" flag in the return dictionary is set to "False". The command
        fails if the desired frame setup is not supported. The frame setup is not
        changed in this case.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            channelWidth (int, optional): the size of each channel in bits (allowed values: 1,2,4,8,16,32,64)
            numChannels (int, optional): number of channels per VDIF frame (allowed values: 1,2,4,8,16,32,64,128)
            payloadSize (int, optional): the total payload size in bytes (=frame size without header) of the VDIF frame

        Returns:
            dict: dictionary with the following structure::

                "compatible" (boolean): False in case an incompatible setup was requested, True otherwise
                "channelWidth" (int): the size of each channel in bits
                "numChannels" (int): number of channels per VDIF frame
                "payloadSize" (int): the total payload size in bytes
                "frameSize" (int): the size of the VDIF frame in bytes
                "numThreads" (int, optional): the number of threads
                "framesPerSecond" (int, optional): the number of frames per second
                "framesPerThread" (int, optional): the number of frames per thread
        Raises:
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
        Gets / sets the VDIF station ID for the specified core3h board

        If the method is called without supplying the stationID parameter the
        current station ID will be reported.

        Note: 
            Setting this value directly affects the header data of 
            the VDIF data format

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            stationId (str, optional): The two-letter station code to set

        Returns:
            str: the two-letter station code; "unknown" if the code could not be determined

        Raises:
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


        Possible return values::
            * on: VDIF encoding is switched on
            * off: VDIF encoding is switched off
            * unknown: in case the VDIF encoding could not be determined

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
           str: current state of the VDIF encoding (for possible values see above)
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

        d0 - d3 are optional. If not specified the current value of the fields are reported

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A") 
            d0 (int, optional): the value of the first user data field
            d1 (int, optional): the value of the second user data field
            d2 (int, optional): the value of the third user data field
            d3 (int, optional): the value of the fourth user data field

        Returns:
            list: list containing the current content of all 4 user data fields

        Raises:
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

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            outputId (int): the index of the Core3h output device (starting at 0)
            ip (str): the destination IP address 
            port (int, optional): the destination IP port number (default = 46227)
            threadId (int): the id of the tread for which to set the destination
        
        Returns: 
            dict: dictionary with the following structure::

                "ip" (str): the IP address
                "port" (int): the port 
                "output" (int): the index of the core3h output port (starting at 0)
                "thread_0" (dict, optional): dictionary holding destination "ip" and "port" for thread 0 (if defined)
                "thread_1" (dict, optional): dictionary holding destination "ip" and "port" for thread 1 (if defined)
                "...."

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
        ''' Retrieve the current parameters of the specified 10Gb ethernet device
        
        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            device (str): the ethernet device name, e.g. eth0

        Returns:
            dict: a dictionary containing all configuration parameters as key/value pairs. The arp_cache key contains a list of arp entries ("mac","ip")

        Raises:
            ValueError: in case an unknown ethernet device has been given
        '''

        response = {} 
        arpTable = []
        boardNum = self.boardToDigit(board)+1
        ret = self.sendCommand("core3h=%d,tengbinfo %s " % (boardNum, device))

        if "not found" in ret:
            raise ValueError("Unknown ethernet device specified (%s) in call to core3h_tengbinfo." % (device))

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
        "ip": IP address
        "mac": MAC address
        "nm": netmask
        "port":  UDP port
        "gateway": IP adress of gateway

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            device (str): the ethernet device name, e.g. eth0
            key (str): the name of the parameter to set (see above)
            value (str): the new parameter value

        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3h=%d,tengbcfg %s %s=%s" % (boardNum, device, str(key), str(value))
        ret = self.sendCommand(cmd)

        return

    def core3h_tengbarp(self, board, device, arpId, mac):
        '''
        Sets one ARP entry for a 10Gb ethernet device

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            device (str): the ethernet device name, e.g. eth0
            arpId (int): index of the ARP table entry to be modified
            mac (str): MAC address to be set (must be in format xx:xx:xx:xx:xx:xx)

        Raises:
            ValueError: in case an invalid MAC address was given
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateMAC(mac)
        
        cmd = "core3h=%d,tengbarp %s %d %s" % (boardNum, device,arpId, mac)
        ret = self.sendCommand(cmd)
        
        return

    def core3h_arp(self, board, mode=None):
        '''
        Enables or disables ARP queries on all ethernet cores.

        If called without the mode parameter the current setting is reported

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            mode (str, optional): Can be "on" or "off". 

        Returns:
            str: the current ARP mode ("on" / "off") or "unknown" in case the arp mode could not be determined

        Raises:
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
        Starts/restarts sending of formatted output data
        
        The output data format can be either:
            * vdif:   VDIF format
            * raw:    unformatted
        
        In case a single output format is given, this will be used for all outputs.
        Formats can be set for each of the outputs individually by separating
        the format specifiers by "+" e.g. vdif+raw+vdif+raw
        if not explictely specified "vdif" will be used for all outputs.

        Raw format requires no time synchronization whereas vdif format requires
        the respective timer to be synchronized (see :py:func:`core3h_timesync`)

        For fast testing: set the force parameter to True to automatically synchronize the
        timer to "zero" time(='2000-01-01T00:00:00'). Provided that a valid 1PPS signal
        is available this will always be successful.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            format (str, optional): a single format specifier or several concatenated by +. Default is "vdif"
            force (boolean, optional): if set to True synchronize time to '2000-01-01T00:00:00'. Default is False

        Returns:
            list: list of format specifiers for all outputs of the specified board

        Raises:
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

        The opposite of :py:func:`core3h_start`

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            boolean: True in case the output of data was stopped; False otherwise
        '''

        boardNum = self.boardToDigit(board)+1
        ret = self.sendCommand("core3h=%d,stop" % (boardNum))
        for line in ret.split("\n"):
            if "Stopped" in line:
                return(True)
        return(False)
        

    def core3h_output(self, board, outputIdx=0, frameId=0):
        '''
        Displays output debug information.

        The command displays the first 16 words of the first frame that was sent
        within the current second interval. The frame is recorded at the output
        specified by outputIdx. 
        
        In addition the following data is displayed:
        1PPS/frame-header/end-of-frame/frame-drop bits

        TODO: implement output parsing
        '''

        boardNum = self.boardToDigit(board)+1
        cmd = "core3h=%d,output %d %d"  %(boardNum, outputIdx, frameId)
        ret = self.sendCommand(cmd)

        return(ret)
        # output

        #Searching for output frames...
        #2020-05-06T07:01:15
        #
        #Frame ID 0 (t=1s):
        #Word | PPS/Hdr/EoF/Drop | Data (hex)
        #------|------------------|------------------
        #0 |  1   1   0   0   | 00000000 6E887E41
        #1 |  0   1   0   0   | 28000000 00A67FBB
        #2 |  0   1   0   0   | 04004E41 04000404
        #3 |  0   1   0   0   | 00000000 00000000
        #4 |  0   1   0   0   | 00000000 00000000
        #5 |  0   0   0   0   | 627665F1 9A701495
        #6 |  0   0   0   0   | 556DAD8E 556DAD8E
        #7 |  0   0   0   0   | 95458139 6995555A
        #8 |  0   0   0   0   | 60851289 AAAAAAAA
        #9 |  0   0   0   0   | AD265969 1126AFDC
        #10 |  0   0   0   0   | BCFBD022 8C9E1C76
        #11 |  0   0   0   0   | 97826F37 E9D7D166
        #12 |  0   0   0   0   | 1638AA49 AB652942
        #13 |  0   0   0   0   | A526A2A1 67AEB375
        #14 |  0   0   0   0   | 25E80D58 3D50588E
        #15 |  0   0   0   0   | 9DEAA9F6 0287D639

    def core3h_reset(self, board, keepsync=False):
        '''
        Resets the FiLa10G datapath

        If called without arguments the complete datapath is reset and time 
        synchonization is lost.

        If called with keepsync=True, FiLa10G tries to maintain the current 
        time synchronization. For this to work the input stage of the data path
        and the timers are not reset.

        Warning: 
            Time synchronization will not be correct
            anymore in the rare but possible case that a data sample with a 1PPS
            flag is lost during the reset process.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            keepsync (boolean, optional): keeps the time synchronization if set to True. Default=False

        Returns:
            boolean: True: if successful False: otherwise
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
        Reboots the system.

        The FiLa10G hardware and software for the given board is reset to 
        its initial state, i.e. as it was directly after the programming of the FPGA and
        lets the FiLa10G system boot again.

        Warning:
            All previously configured settings and states are lost when rebooting!

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            boolean: True: if successful False: otherwise
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

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            boolean: True if successful False otherwise
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
        If specified mode must be a valid core3h mode (as listed in :py:attr:`DBBC3.core3hModes`)

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            mode (str, optional): if ommited gets the currently active mode

        Returns:
            str: the current mode
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
        Displays the FILA10G versions of the specified board

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            dict: a dictionary with the following structure::

                "systemName" (str): the FILA10G system name
                "compileDate" (str): the date string of the firmware compile date
                "versionSW" (str): the version string of the FILA10G firmware
                "versionHW" (str): the version string of the FILA10G hardware
        
        '''
        boardNum = self.boardToDigit(board)+1

        resp = {}

        ret = self.sendCommand("core3h=%d,version" % (boardNum))
        # version
        # System name : FiLa10GS4+
        # Compiled on : Apr 18 2016 15:17:17
        # SW version  : 2.8.0-S4+
        # HW version  : 2.8-S4+
        for line in ret.split("\n"):
            tok = line.split(":")
            if (len(tok) == 2):
                if (tok[0].strip().startswith("System name")):
                    resp["systemName"] = tok[1].strip()
                elif (tok[0].strip().startswith("Compiled on")):
                    resp["compileDate"] = tok[1].strip()
                elif (tok[0].strip().startswith("SW version")):
                    resp["versionSW"] = tok[1].strip()
                elif (tok[0].strip().startswith("HW version")):
                    resp["versionHW"] = tok[1].strip()
            
        return (resp)


    def core3h_sysstat(self, board):
        ''' 
        Displays information about the current status of the system and
        gives an overview of the state of the most important user 
        settings.

        All key value pairs of the sysstat output are returned as a dictionary. All whitespaces 
        have been converted to '_' all characters have been converted to lower-space. 

        Args:
            board: the board number (starting at 0=A) or board ID (e.g "A")

        Returns: 
            dict: a dictionary with the systat key value pairs with whitespaces converted to '_' 

            example: 
                [{'selected_input': 'vsi1', 'input_sample_rate': '128000000 Hz / 2', 'vsi_input_swapped': 'no', 'vsi_input_bitmask': '0xFFFFFFFF', 'vsi_input_width': '32 bit', 'pps_count': '0', 'tvg_mode': 'vsi-h', 'mk5b_timesync': 'no', 'vdif_timesync': 'no', 'gps_receiver': 'installed', 'output': 'stopped', 'output_0_format': 'raw', 'output_0_dest': '192.168.1.2:46220', 'output_1_format': 'raw', 'output_1_dest': '192.168.1.3:46227', 'output_2_format': 'raw', 'output_2_dest': '192.168.1.4:46227', 'output_3_format': 'raw', 'output_3_dest': '192.168.1.5:46227', 'ethernet_arps': 'on', 'selected_vsi_output': 'vsi1-2-3-4'}]
        '''
        boardNum = self.boardToDigit(board)+1

        resp = {}

        ret = self.sendCommand("core3h=%d,sysstat" % (boardNum))
        # sysstat

        # System status:
        # Selected input      : vsi1
        # Input sample rate   : 128000000 Hz / 2
        # VSI input swapped   : no
        # VSI input bitmask   : 0xFFFFFFFF
        # VSI input width     : 32 bit
        # PPS count           : 59051
        # 
        # TVG mode            : vsi-h
        # 
        # MK5B timesync       : yes
        # VDIF timesync       : yes
        # GPS receiver        : installed
        # 
        # Output              : started
        # Output 0 format     : vdif
        # Output 0 dest.      : 172.16.3.24:46220
        # Output 1 format     : vdif
        # Output 1 dest.      : 192.168.1.3:46227 (rewriting enabled)
        # Output 2 format     : vdif
        # Output 2 dest.      : 192.168.1.4:46227 (rewriting enabled)
        # Output 3 format     : vdif
        # Output 3 dest.      : 192.168.1.5:46227 (rewriting enabled)
        # Ethernet ARPs       : off (during data transfer)
        # Selected VSI output : vsi1-2-3-4
        
        for line in ret.split("\n"):
            tok = line.strip().split(":",1)
            if tok[0].startswith("Core3H") or tok[0].startswith("System status"):
                continue
        #    print (tok[0])
            if len(tok) == 2:
                # replace space by underscore, make lower case
                key = (' '.join(tok[0].split())).replace(" ", "_",2).replace(".","").lower()
                value = tok[1].strip()
                resp[key] = value

                
        return (resp)
        

    def core3h_sysstat_fs(self, board):
        ''' 
        Identical to core3h_sysstat but returns machine (fields-system)
        readable output
        
        TODO: implement parsing code

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,sysstat_fs" % (boardNum))

    def core3h_mode_fs(self, board):
        ''' 
        Returns mode information in a machine-readble form (field-system)

        TODO: implement parsing codes

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,mode_fs" % (boardNum))

        # mode_fs
        # vsi1,128000000/2,0xFFFFFFFF,vdif,2,16,1024

    def core3h_status_fs(self, board):
        ''' 
        Returns time sync information in a machine-readble form (field-system)

        TODO: implement parsing codes

        Parameters:
        board: the board number (starting at 0=A) or board ID (e.g "A")
        '''
        boardNum = self.boardToDigit(board)+1
        return self.sendCommand("core3h=%d,status_fs" % (boardNum))

        # status_fs
        # synced,vdif,started

    def core3h_devices(self, board):
        ''' 
        Lists all devices of the the current system and their corresponding memory address ranges

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
        
        Returns:
            dict: dictionary with the following structure::

                "devicename" (str): the name of the device
                "value" (str): memory address range
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
        Obtains the 2-bit sampler statistics for the given core board and sampler.

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A
            sampler (int): the sampler number (starting at 0)


        Returns:
            list: list containing the count of the 4 levels or None if the core board is not connected
        '''

        boardNum = self.boardToDigit(board) +1

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

        return (bstats)

    def core3h_core3_power(self, board):
        '''
        Obtains the gains of all 4 samplers of the given board

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A

        Returns:
            list: list containing the gains for all samplers (a[0] = sampler1 etc.) or None in case the core3 board is not connected
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

        return(pow)

    def core3h_core3_corr(self, board):
        '''
        Performs cross-correlation between the samplers of the given board.

        Correlation products are calculated between these sampler pairs:
             * 0-1
             * 1-2
             * 2-3 
        
        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A
        
        Returns:
            list: List containing the three cross-correlation coefficients in the order described above
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

        Returns:
            None
        '''
        self.sendCommand("adb3l=reset")
        return

    def adb3l_reseth(self):
        '''
        Resets all ADB3L boards, but does NOT change/reset any register settings

        Returns:
            None
        '''
        self.sendCommand("adb3l=reseth")
        return 

    def adb3l_resets(self, board, sampler=None):
        '''
        Resets the ADB3L registers to default values for the specified board and sampler

        If called without the optional sampler parameter a reset is performed for all samplers
        of the specified board. 
    
        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int, optional): sampler number (0-3)

        Returns:
            None
        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "adb3l=resets=%d" % boardNum

        if sampler:
            cmd += ",%d" % sampler
            
        self.sendCommand(cmd)
        return 

    def adb3l_biston(self, board):
        '''
        Turns on BIST-mode for all samplers on the specified board.

        Note:
             after enabling the BIST-mode the samplers must be reset by calling :py:func:`adb3l_reseth` 

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
        '''

        boardNum = self.boardToDigit(board)+1
        self.sendCommand("adb3l=biston=%d" % boardNum)
        return

    def adb3l_bistoff(self, board):
        '''
        Turns off BIST-mode for all samplers on the specified board.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
        '''

        boardNum = self.boardToDigit(board)+1
        self.sendCommand("adb3l=bistoff=%d" % boardNum)

        return

    def adb3l_SDA_on(self, board, sampler):
        '''
        Turns on SDA Mode (Sampler Delay Adjust) for the specified board and sampler.

        This method must be called prior to adjusting the delay of a sampler with the :py:func:`adb3l_delay` command.
        Introduces a delay offset of 60ps.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int): sampler number (0-3)

        Raises:
            ValueError: in case the specified sampler is out of range
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateSamplerNum(sampler)

        cmd = "adb3l=SDA_on=%d,%d" % (boardNum, sampler)

        self.sendCommand(cmd)
        return


    def adb3l_delay(self, board, sampler, value=512):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Sets the sampler delay for the specified board and sampler.

        The allowed range is 0-1023 which corresponds to -60ps to +60ps with a stepping size of 120fs.
        The default is 512 = 0ps.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int): sampler number (0-3)
            value (int, optional): the delay value in steps of 120fs. Default is 512 (=0ps)

        Returns:
            None

        Raises:
            ValueError: in case the specified sampler is out of range
            ValueError: in case the specified value parameter is out of range
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateSamplerNum(sampler)
    
        if value < 0 or value>1023:
            raise ValueError("sampler delay value must be in the range 0-1023")

        cmd = "adb3l=delay=%d,%d,%d" % (boardNum, sampler,value)

        self.sendCommand(cmd)
        return

    def adb3l_offset(self, board, sampler, value=128):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Sets the sampler offset value for the specified board and sampler.

        The allowed range is 0-255 which corresponds to -20mV to +20mV with a stepping size of 156microV.
        The default is 128 = 0mV.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int): sampler number (0-3)
            value (int, optional): the offset value in steps of 156 microV. Default is 128 (=0 mV)

        Returns:
            None

        Raises:
            ValueError: in case the specified sampler is out of range
            ValueError: in case the specified value parameter is out of range
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateSamplerNum(sampler)

        if value < 0 or value>255:
            raise ValueError("sampler offset value must be in the range 0-255")

        cmd = "adb3l=offset=%d,%d,%d" % (boardNum, sampler,value)

        self.sendCommand(cmd)
        return

    def adb3l_gain(self, board, sampler, value=512):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Sets the sampler gain value for the specified board and sampler.

        The allowed range is 0-255 which corresponds to -0.5dB to +0.5dB with a stepping size of 0.004dB.
        The default is 128 = 0dB.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int): sampler number (0-3)
            value (int, optional): the offset value in steps of 0.004dB. Default is 128 (=0 dB)

        Returns:
            None

        Raises:
            ValueError: in case the specified sampler is out of range
            ValueError: in case the specified value parameter is out of range
        '''

        boardNum = self.boardToDigit(board)+1
        self._validateSamplerNum(sampler)

        if value < 0 or value>255:
            raise ValueError("sampler gain value must be in the range 0-255")

        cmd = "adb3l=gain=%d,%d,%d" % (boardNum, sampler,value)

        self.sendCommand(cmd)
        return

class DBBC3Commandset_DDC_Common (DBBC3CommandsetDefault):
    '''
    Implementation of the DBBC3Commandset with methods common to all
    DDC modes of the DBBC3. Subclasses that implement special methods
    of the various DDC modes; e.g. DDC_V, DDC_L or DDC_U should derive
    from this class.
    '''

#    def __init__(self, clas):
#
#        DBBC3CommandsetDefault.__init__(self,clas)


    def __init__(self, clas):

        DBBC3CommandsetDefault.__init__(self,clas)

        clas.dbbc = types.MethodType (self.dbbc.__func__, clas)
        clas._dbbc = types.MethodType (self._dbbc.__func__, clas)
        clas.dbbcgain = types.MethodType (self.dbbcgain.__func__, clas)
#        clas.dbbcstat = types.MethodType (self.dbbcstat.__func__, clas)
        clas.cont_cal = types.MethodType (self.cont_cal.__func__, clas)
        clas.dbbctp = types.MethodType (self.dbbctp.__func__, clas)
        clas.dsc_tp = types.MethodType (self.dsc_tp.__func__, clas)
        clas.dsc_corr = types.MethodType (self.dsc_corr.__func__, clas)
        clas.dsc_bstat = types.MethodType (self.dsc_bstat.__func__, clas)
        clas.mag_thr = types.MethodType (self.mag_thr.__func__, clas)
        clas.pps_delay = types.MethodType (self.pps_delay.__func__, clas)
        clas.core3hread = types.MethodType (self.core3hread.__func__, clas)
        clas.core3hwrite = types.MethodType (self.core3hwrite.__func__, clas)

    def pps_delay(self, board=None):
        '''
        Retrieves the delay of the internally generated vs. the external 1PPS signal

        The delay is calculated as the time difference internal - external 1PPS and is returned in ns.

        In case the method is called without the optional board parameter the PPS delays are returned
        for all the core boards present in the current system.

        If the optional board parameter is used one delay value will be returned for each of the
        PPS groups each serving 4 BBCs. Group 1: BBCs 1-4; group 2: BBCs 5-8 etc.

        Parameters:
            board: (int or str, optional): if specified returns the PPS values for the PPS groups (4 BBCs) of the given core3H board

        Returns:
            list: list holding the delays of the internal-external PPS in nanoseconds. One value for each Core3H board if called without the optional board parameter.
            list: list holding the delays of the internal-external PPS in nanoseconds. Two values for the two PPS groups if called with the optional board parameter.
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

        for i in range(numVals):
                patStr += "\s+\[(\d+)\]:{0,1}\s+(\d+)\s+ns,"
        patStr = patStr[:-1] + ";"
        pattern = re.compile(patStr)

        delays = []
        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                for i in range(retVals):
                    # convert into signed 
                    delay = int(match.group(2+i*2))
                    # account for negative delays
                    if delay > 500000000:
                        delay = int(match.group(2+i*2)) - 1000000000
                    delays.append(delay)
        return(delays)

    def dbbctp0 (self, bbc, tp0=None):
        '''
        Set the TP0 value for a given or all of the BBCs

        The TP0 value will be used for the determination of Tsys values that are broadcasted via multicast.
        The TP0 value has the same dimension as the total power values given by :py:func:`dbbc` command

        If called without supplying tp0 value the current setting is returned

        Args:
            bbc (int/str): the BBC number (starts at 1) or 'all' in case the TP0 should be applied to all BBCs
            tp0 (int, optional): the TP0 value

        Returns:
            int: the current tp0 value
        '''

        if (bbc != "all"):
            self._validateBBC(bbc)
            bbc = str(bbc)

        cmd = "dbbctp0=%s" % (bbc)
        if tp0:
            cmd += ",%d" % (tp0)
        ret = self.sendCommand(cmd)
        # dbbctp0/ all,10;
        # dbbctp0/ 1,10;
        pattern = re.compile("dbbctp0\/\s*(.+?),(\d+);")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if (match):
                return match.group(2)

        return(None)


    def dbbctdiode (self, bbc, tdiodeUSB=None, tdiodeLSB=None):
        '''
        Sets the t_diode value for a given or all of the BBCs

        The t_diode value will be used for calculating the Tsys values that are broadcasted via multicast.
        Separate t_diode for USB and LSB can be supplied. The t_diode should be given in units of K.

        If called without supplying t_diode values the current setting is returned

        Args:
            bbc (int/str): the BBC number (starts at 1) or 'all' in case the t_diode should be applied to all BBCs
            tdiodeUSB (int, optional): the t_diode value to use for the USB
            tdiodeLSB (int, optional): the t_diode value to use for the LSB

        Returns:
            tuple (int,int): current t_diode values (USB, LSB)
        '''

        mode = "get"
        # both values have been set
        if (all([tdiodeUSB, tdiodeLSB])):
            mode = "set"
        # only one has been set
        elif (any([tdiodeUSB, tdiodeLSB])):
            raise ValueError("dbbctdiode: t_diode values must be given both for USB and LSB")

        if (bbc != "all"):
            self._validateBBC(bbc)
            bbc = str(bbc)
        elif (mode == "get"):
            raise ValueError("dbbctdiode: option 'all' is only allowed when setting t_diode  values")

        cmd = "dbbctdiode=%s" % (bbc)

        if (mode == "set"):
            cmd += ",%d,%d" % (tdiodeUSB, tdiodeLSB)

        ret = self.sendCommand(cmd)
        # dbbctdiode/ all,20,30;
        # dbbctdiode/ 1,20,30;
        pattern = re.compile("dbbctdiode\/\s*(.+?),(\d+),(\d+);")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if (match):
                return match.group(2), match.group(3)
            
        return(None)


    def dbbcdpfu (self, bbc, dpfuUSB=None, dpfuLSB=None):
        '''
        Sets the DPFU value for a given or all of the BBCs

        The DPFU value will be used for calculating the SEFD values that are broadcasted via multicast.
        Separate DPFU for USB and LSB can be supplied. The DPFU should be given in units of K/Jy.

        If called without supplying the DPFU values the current setting is returned

        Args:
            bbc (int/str): the BBC number (starts at 1) or 'all' in case the DPFU should be applied to all BBCs
            dpfuUSB (int, optional): the DPFU value to use for the USB
            dpfuLSB (int, optional): the DPFU value to use for the LSB

        Returns:
            tuple (int,int): current DPFU values (USB, LSB)

        '''

        mode = "get"

        # both values have been set
        if (all([dpfuUSB, dpfuLSB])):
            mode = "set"
        # only one has been set
        elif (any([dpfuUSB, dpfuLSB])):
            raise ValueError("dbbcdpfu: DPFU values must be given both for USB and LSB")

        if (bbc != "all"):
            self._validateBBC(bbc)
            bbc = str(bbc)
        elif (mode == "get"):
            raise ValueError("dbbcdpfu: option 'all' is only allowed when setting DPFU values")

        cmd = "dbbcdpfu=%s" % (bbc)

        if (mode == "set"):
            cmd += ",%d,%d" % (dpfuUSB, dpfuLSB)

        ret = self.sendCommand(cmd)

        # dbbcdpfu/ all,20,30;
        # dbbcdpfu/ 1,20,30;
        pattern = re.compile("dbbcdpfu\/\s*(.+?),(\d+),(\d+);")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if (match):
                return match.group(2), match.group(3)
            
        return(None)
    
        
    def dbbc (self, bbc, freq=None, bw=None, ifLabel=None, tpint=None):
        ''' 
        Gets / sets the parameters of the specified BBC.

        If called without passing the freq parameter the current settings are returned.

        The frequency must be specified in units of MHz.

        Args:
            bbc (int): the BBC number (starts at 1) 
            freq (optional, float): the BBC frequency. If not specified the current setting is returned
            ifLabel (optional, str): the IF label to be used for the BBC (relevant e.g. for FS log). Must be single letter a-h
            tpint (optional,int): total power integration time in seconds (default = 1 second)

        Returns:
            dict: a dictionary with the following structure::
                
                "freq" (float):  the frequency of the BBC in MHz
                "ifLabel" (str): the label of the ascociated IF (a-h)
                "bw" (int): the bandwidth
                "tpint" (int): the total power integration time in seconds
                "mode" (str): the current gain control mode (agc / manual)
                "gainUSB" (int): the gain of the USB (0-255)
                "gainLSB" (int): the gain of the LSB (0-255)
                "tpUSBOn" (int): the total power of the USB with cal diode on
                "tpLSBOn" (int): the total power of the LSB with cal diode on
                "tpUSBOff" (int): the total power of the USB with cal diode off
                "tpLSBOff" (int): the total power of the LSB with cal diode off

        Raises:
            ValueError: in case an invalid BBC number has been specified
            ValueError: in case an invalid BBC frequency has been specified
            ValueError: in case an invalid tpint value has been specified
        '''

        # first obtain the current settings
        ret = self._dbbc(bbc, None, None, None, None)

        if (freq):
            ret["freq"] = freq 

            if (bw):
                ret["bw"] = bw 
            if (ifLabel):
                ret["ifLabel"] = ifLabel 
            if (tpint):
                ret["tpint"] = tpint 
            ret = self._dbbc(bbc,ret["freq"],ret["bw"],ret["ifLabel"],ret["tpint"])

        return(ret)


    def _dbbc(self, bbc, freq, bw, ifLabel, tpint):

        self._validateBBC(bbc)

        resp = {}

        if (ifLabel):
            ifLabel = ifLabel.lower()
            if (ifLabel not in str("abcdefgh")):
                raise ValueError("dbbc: ifLabel must be one of abcdefgh")

        cmd = "dbbc{:02d}".format(bbc)

        if (freq):
            self._validateBBCFreq(freq)
            
            cmd += "=%f" %(freq)

            if (bw):
                # bw cannot be set with empty ifLabel due to control software parameter order
                if not ifLabel:
                    ifLabel = 'a'
                cmd += ",%s,%d" % (ifLabel,bw)

                if (tpint):
                    self._validateTPInt(tpint)
                    cmd += ",%d" % (tpint)

        ret = self.sendCommand(cmd)

        #  dbbc001/ 2992.000000,a,32,1,agc,142,123,14855,14753,14866,14749;
        pattern = re.compile("dbbc{:03d}\/\s*(\d+\.\d+),(.?),(\d+),(\d+),(.+?),(\d+),(\d+),(\d+),(\d+),(\d+),(\d+);".format(bbc))

        for line in ret.split("\n"):
            match = pattern.match(line)
            if (match):
                resp['freq'] = match.group(1)
                resp['ifLabel'] = match.group(2)
                resp['bw'] = match.group(3)
                resp['tpint'] = match.group(4)
                resp['mode'] = match.group(5)
                resp['gainUSB'] = match.group(6)
                resp['gainLSB'] = match.group(7)
                resp['tpUSBOn'] = match.group(8)
                resp['tpLSBOn'] = match.group(9)
                resp['tpUSBOff'] = match.group(10)
                resp['tpLSBOff'] = match.group(11)

        return(resp)

    def dbbcgain(self, bbc, mode=None, target= None, gainU=None, gainL=None):
        '''
        Gets / sets the gain levels and gain control mode for a single BBC.

        If the command is called with only the bbc parameter the current settings will be returned.

        If the command is being called with the mode=agc the automatic gain control is switched on.
        If the target parameter is also set then the levels are automatically adjusted to reach the
        given target otherwise the target specified in the DBBC configuration file is being used.

        If the command is being called with mode=man the automatic gain control is switched off
        and the current gain levels are being frozen. In case also the gainU and gainL parameters
        are set then these values will be used as the gain levels for the USB and LSB respectively.

        Args:
            bbc (int): the BBC number (starts at 1) 
            mode (str, optional): the gain control mode. Can be "agc" (automatic gain control) or "man" to freeze the current gain settings.
            target (int, optional): the target count level when running in "agc" mode
            gainU (int, optional): the gain level for the USB
            gainL (int, optional): the gain level for the LSB
        

        Returns:
            dict: a dictionary with the following structure::

                "bbc" (int):         The currently selected BBC number (starts at 1)
                "mode" (str):        The currently selected mode 
                "target" (int):      The current target count level (only returned when mode=agc)
                "gainUSB" (int):     The gain level of the USB
                "gainLSB" (int):     The gain level of the LSB

        Raises:
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
        '''
        DEPRECATED
        Returns the bit statistics of a single BBC.

        Bit statistics are obained for the sign and magnitude portions.
            * sign: the fraction of positive values (should be around 50%)
            * magnitude:: the sum of the 00 and 11 states (should be around 36%)
        
        For each BBC sign and magnitude statistics are obtained for both sidebands
        of the specified BBC.

        The results are passed back as a dictionary with the following structure::
    
            "s" (tuple of float): sign statistics (USB, LSB)
            "m" (tuple of float): magnitude statistics (USB, LSB)

        e.g. {'s': (49.85, 49.86), 'm': (34.82, 34.66)}

        Args:
            bbc: the BBC number (starts at 1)
            
        Returns:
            dict: the dictionary containing the sign and magnitude bit statistics (for structure see description above)
        Raises:
            ValueError: in case the specified bbc index is out of range
        '''

        self._validateBBC(bbc)

        resp = {}

        # Received from DBBC: dbbcstat/ 16,S,34.67,34.53;
        pattern = re.compile("dbbcstat\/\s+(\d+),([SM]),(\d+\.\d+),(\d+\.\d+);")

        for mode in ["s", "m"]:
            cmd = "dbbcstat=%d,%s" % (bbc, mode)
            ret = self.sendCommand(cmd)

            for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                    resp[mode] = (float(match.group(3)), float(match.group(4)))
                
        return(resp)

    def cont_cal(self, mode=None, *args):
        '''
        Turns continuous calibration on or off.

        If called without the mode parameter the current setting of the 
        continous calibration is returned

        If executing with mode='on' up to three extra parameters can be supplied:
            polarity, freq, option

        The optional polarity parameter  can have the following values:
            * 0: no polarity change, no display swap
            * 1: polarity change, no display swap
            * 2: no polarity change, display swap
            * 3: polarity change, display swap

        The optional freq parameter specifies the cal frequency in Hz.
        
        The optional option parameter can have the following values:
            * 0: cal is pulsed
            * 1: cal is always on

        Args:
            mode (str, optional): can be either "on" or "off"
            *args (int): up to three extra parmeters (see description above)
        
        Returns:
            dict: A dictionary with the following structure::
        
                "mode" (str): the current continuous cal mode 
                "polarity" (int): the current polarity setting (see above)
                "freq" (int): the current continuous cal frequency in Hz
                "option" (int): the current option setting (see above)
        '''


        resp = {}
        cmd = "cont_cal"
        
        if (mode):
            if not d3u.validateOnOff(mode):
                raise ValueError("cont_cal: mode must be 'on' or 'off'")
            #cmd += "=%s,%d,%d,%d" % (mode,polarity,freq,0)
            cmd += "=%s" % (mode)
            
            if (mode == "on"):
                if (len(args) > 3):
                    raise ValueError("cont_cal: too many arguments given (max 4)")

                if args[0]:
                    if (args[0] not in range(0,4)):
                        ValueError("cont_cal: polarity must be in range 0-3")
                if args[1]:
                    if (args[1] < 0):
                        ValueError("cont_cal: freq must be positive")
                if args[2]:
                    if (args[2] not in [0,1]):
                        ValueError("cont_cal: option must be 0 or 1")

                for arg in args:
                    cmd += ",%d" % arg

        ret = self.sendCommand(cmd)

        # cont_cal/ off,0,80,0; 
        pattern = re.compile("cont_cal\/\s+(.+?),(\d),(\d+),(\d);")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                resp["mode"] = match.group(1)
                resp["polarity"] = int(match.group(2))
                resp["freq"] = int(match.group(3))
                resp["option"] = int(match.group(4))

        return(resp)

    def dbbctp(self, board):
        '''
        Obtains the DSC total power values

        Separate DSC power values are returned for the three cases:
            * DSC total power
            * DSC total power off
            * DSC total power on

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            tuple: (dsc_power, dsc_power_off, dsc_power_on)

        Raises:
            ValueError: in case the requested board is out of range
        '''

        resp = None

        board = self.boardToChar(board).lower()
        cmd = "dbbctp%s" % (board)
        ret = self.sendCommand(cmd)

        #dbbctpd/ 0, 0, 0;
        pattern = re.compile("%s\/\s*(\d+),\s*(\d+),\s*(\d+);" % (cmd))

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                resp = (match.group(1), match.group(2),match.group(3))
                
        return(resp)

    def dsc_tp(self, board):
        '''
        Gets the DSC total power values

        Power values are obtained for all 4 samplers of the selected board.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            list:  a list holding the power values for all four samplers

        Raises:
            ValueError: in case the requested board is out of range
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
        Cross-correlates the signals of the 4 samplers

        Performs cross-correlation between the 4 samplers of the given board. Correlation
        products are between these samplers:

            * 0-1
            * 1-2
            * 2-3

        The values can be used to check if the samplers are in the correct phase (=synchronized).

        Note:
             The absolute numbers returned depend on the input power and IF bandwidth. However the values obtained for a board should not deviate by more than 10%.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            list: list containing the three cross-correlations in the order described above

        Raises:
            ValueError: in case the requested board is out of range
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

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            sampler (int): the sampler number (0-3)

        Returns:
            list: list of dictionaries with the following keys::

                "count":  count for the given state
                "perc":   percentage for the given state

            the list indices are
                0: ++ state
                1: + state
                2: - state
                3: -- state

            return example:
                [{'count': 1413, 'perc': 9}, {'count': 6358, 'perc': 40}, {'count': 6392, 'perc': 40}, {'count': 1459, 'perc': 9}]
        
        Raises:
            ValueError: in case the requested board is out of range
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
#                print (line)
                if (match.group(1) == "11"):
                    stat[0] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "10"):
                    stat[1] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "01"):
                    stat[2] = {"count":int(match.group(2)), "perc":int(match.group(3))}
                elif (match.group(1) == "00"):
                    stat[3] = {"count":int(match.group(2)), "perc":int(match.group(3))}

        return(stat)

    def mag_thr(self, bbc, threshold=None):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Gets/sets the threshold factor for the continuous threshold calibration

        if called without the threshold parameter, the current threshold factor is returned.

        Args:
            bbc (int): the BBC number (starts at 1) 
            threshold (float): the threshold factor to apply

        Returns:
            float: the threshold factor; None if the threshold could not be obtained or set

        Raises:
            ValueError: in case an invalid BBC number has been specified
        '''

        self._validateBBC(bbc)

        cmd = "mag_thr=%d" % (bbc)
        if threshold:
            cmd += ",%d" % (threshold)

        ret = self.sendCommand(cmd)
        # mag_thr/ 1,75.000000;

        pattern = re.compile("mag_thr\/\s*(\d+),(\d+\.\d+)")

        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                return(float(match.group(2)))

        return(None)


    def core3hread(self, board, block, bbc, register):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Reads a core3h register value

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            block (int): the block index of the register to read (starts at 1)
            bbc (int): the bbc index within the block (starts at 1)
            register (int): the register index within the block (starts at 1)

        Returns:
            str: hex representation of the register value, or None if the regsiter could not be read

        '''

        value = None

        boardNum = self.boardToDigit(board)+1

        cmd = "core3hread=%d,%d,%d,%d" % (boardNum, block,bbc,register)
        ret = self.sendCommand(cmd)

        # core3hread/ Core3H[1],Block[1],BBC[5000],Reg[1] = 00000077;
        pattern = re.compile("core3hread/.+?\s*=\s*(.+);")
        for line in ret.split("\n"):
            match = pattern.match(line)
            if (match):
                value = hex(int(match.group(1),16))

        return(value)

    def core3hwrite(self, board, block, bbc, register, value):
        '''
        Warning:
             This is an expert level method and is intended for debugging purposes only.
             Wrong usage could bring the DBBC3 system into an unstable state and could lead to
             unwanted or unexpected results. Use only if you know what you are doing!

        Writes a value to a core3h register 


        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            block (int): the block index of the register to read (starts at 1)
            bbc (int): the bbc index within the block (starts at 1)
            register (int): the register index within the block (starts at 1)
            value (int): the register value to write

        '''

        boardNum = self.boardToDigit(board)+1

        cmd = "core3hwrite=%d,%d,%d,%d,%d" % (boardNum, block,bbc,register,value)
        ret = self.sendCommand(cmd)

        return

class DBBC3Commandset_DDC_V_123(DBBC3Commandset_DDC_Common):
    '''
    Implementation of the DBBC3 commandset for the 
    DDC_V mode version 123
    '''

    def __init__(self, clas):

        DBBC3Commandset_DDC_Common.__init__(self,clas)

    def dbbc (self, bbc, freq=None, ifLabel=None, tpint=None):
        ''' 
        Gets / sets the parameters of the specified BBC.

        If called without passing the freq parameter the current settings are returned.

        The frequency must be specified in units of MHz.
        
        The bandwidth is fixed to 32 MHz for the DDC_V mode

        Args:
            bbc (int): the BBC number (starts at 1) 
            freq (optional, float): the BBC frequency. If not specified the current setting is returned
            ifLabel (optional, str): the IF label to be used for the BBC (relevant e.g. for FS log). Must be single letter a-h.
            tpint (optional,int): total power integration time in seconds (default = 1 second)

        Returns:
            settings (dict): dictionary containting the settings of the specified BBC

        Raises:
            ValueError: in case an invalid BBC number has been specified
            ValueError: in case an invalid BBC frequency has been specified
            ValueError: in case an invalid tpint value has been specified
        '''

        return(self._dbbc(bbc,freq,32,ifLabel,tpint))


class DBBC3Commandset_DDC_V_124(DBBC3Commandset_DDC_V_123):

    def __init__(self, clas):

        DBBC3Commandset_DDC_V_123.__init__(self,clas)

        if (clas.config.cmdsetVersion["minorVersion"] >= 200618):
            clas.dbbcdpfu = types.MethodType (self.dbbcdpfu.__func__, clas)
            clas.dbbctp0 = types.MethodType (self.dbbctp0.__func__, clas)
            clas.dbbctdiode = types.MethodType (self.dbbctdiode.__func__, clas)



    
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

class DBBC3Commandset_OCT_D_120(DBBC3CommandsetDefault):

    def __init__(self, clas):

        DBBC3CommandsetDefault.__init__(self,clas)

        clas.tap = types.MethodType (self.tap.__func__, clas)
        clas.samplerstats = types.MethodType (self.samplerstats.__func__, clas)
        clas.core3hstats = types.MethodType (self.core3hstats.__func__, clas)
        clas.time = types.MethodType (self.time.__func__, clas)
        clas.core3h_core3_bstat = types.MethodType (self.core3h_core3_bstat.__func__, clas)
        clas.core3h_core3_power = types.MethodType (self.core3h_core3_power.__func__, clas)
        clas.core3h_sampler_offset = types.MethodType (self.core3h_sampler_offset.__func__, clas)
        clas.core3h_sampler_power = types.MethodType (self.core3h_sampler_power.__func__, clas)
        clas.pps_delay = types.MethodType (self.pps_delay.__func__, clas)

        # core3h_output was dropped from the command set of OCT_D_120
        del clas.core3h_output

    def pps_delay(self):
        '''
        Determines the delay between the internal vs. the external PPS.
        A positive value indicates that the internal PPS is delayed with respect to the external signal.
        All delays are in units of ns.

        Returns:
            list (float): List containing the pps delays for all 8 core3h boards (unit: ns)
        '''

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
                    # convert into signed
                    delay = int(match.group(2+i*2))
                    # account for negative delays
                    if delay > 500000000:
                        delay = int(match.group(2+i*2)) - 1000000000
                    delays.append(delay)
        return(delays)

    def core3h_sampler_offset(self, board):
        '''
        Obtains the offset statistics for each of the four samplers of the specified board.

        Note:
            Usage of :py:func:`core3h_sampler_offset` is deprecated. Use :py:func:`samplerstats` to obtain
            the statistics, power, offset and delay of the individual samplers.

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A

        Returns:
            list: list containing the sampler offsets; the values will be None in case of error
            None if the core board is not connected
        '''
        boardNum = self.boardToDigit(board) +1

        # sampler_offset
        # Sampler offset levels:
        # Offset at sampler 0 = 63860074
        # Offset at sampler 1 = 63739766
        # Offset at sampler 2 = 64068670
        # Offset at sampler 3 = 64170648

        res = [None] *4
        ret = self.sendCommand("core3h=%d,sampler_offset"  % (boardNum))

        if "not connected" in ret:
                return(None)

        pattern = re.compile("\s*Offset\s+at\s+sampler\s+(\d)\s*=\s*(\d+)")

        for line in ret.split('\n'):
            #print (line)
            match = pattern.match(line)
            if match:
                res[int(match.group(1))] = int(match.group(2))

        return (res)


    def core3h_sampler_power(self, board):
        '''
        Obtains the power levels for each of the four samplers of the specified board.

        Note:
            Usage of :py:func:`core3h_sampler_power` is deprecated. Use :py:func:`samplerstats` to obtain
            the statistics, power, offset and delay of the individual samplers.

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A

        Returns:
            list: list containing the sampler powers; the values will be None in case of error
            None if the core board is not connected
        '''
        boardNum = self.boardToDigit(board) +1

        # Sampler power levels:
        # Power at sampler 0 = 106798846
        # Power at sampler 1 = 107664014
        # Power at sampler 2 = 106424473
        # Power at sampler 3 = 107536015

        res = [None] *4
        ret = self.sendCommand("core3h=%d,sampler_power"  % (boardNum))

        if "not connected" in ret:
                return(None)

        pattern = re.compile("\s*Power\s+at\s+sampler\s+(\d)\s*=\s*(\d+)")

        for line in ret.split('\n'):
            #print (line)
            match = pattern.match(line)
            if match:
                res[int(match.group(1))] = int(match.group(2))

        return (res)

    def core3h_core3_power(self, board):
        '''
        Obtains the power statistics of the selected board for both filters.

        The powers reported separately for the two VSI channels resulting 
        in a total of 4 values:
            * filter 0: 0a & 0b 
            * filter 1: 1a & 1b 

        Note:
            Usage of :py:func:`core3h_core3_power` is deprecated. Use :py:func:`core3hstats` to obtain
            bit statistics and power levels of the filtered outputs.

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A

        Returns:
            dict : dictionary containing the powers for the two filters (split up over two VSI channels), None in case the core3 board is not connected
        '''

        boardNum = self.boardToDigit(board) +1

        pow = {}
        ret = self.sendCommand("core3h=%d,core3_power" % (boardNum))

        if "not connected" in ret:
                return None

        #CORE3 filter power levels:
        #Power at filter 0a = 62066749
        #Power at filter 1a = 299796534
        #Power at filter 0b = 110171088
        #Power at filter 1b = 300520436

        pattern = re.compile("\s*Power\s+at\s+filter\s+([01][ab])\s+=\s+(\d+)")
        for line in ret.split('\n'):
            #print (line)
            match = pattern.match(line)
            if (match):
                #print (match.group(3))
                pow[match.group(1)] = int(match.group(2))

        return(pow)

    def core3h_core3_bstat(self, board, filter):
        '''
        Obtains the 2-bit statistics for the selected core board and filter

        Note:
            Usage of :py:func:`core3h_core3_bstat` is deprecated. Use :py:func:`core3hstats` to obtain
            bit statistics and power levels of the filtered outputs.

        Args:
            board (int or str): can be given as a number (0 = board A) or as char e.g. A
            filter (int): the selected filter (can be 0 or 1)

        Returns:
            list: list containing the count of the 4 levels or None if the core board is not connected
        '''

        boardNum = self.boardToDigit(board) +1

        #self._validateSamplerNum(sampler)

        bstats = []
        ret = self.sendCommand("core3h=%d,core3_bstat %d" % (boardNum, filter))

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

        return (bstats)

    def checkphase(self, board=None):
        '''
        Checks the delay phase calibration for the specified board or for all boards if the board parameter is not specified.

        Warning:
            Do not execute checkphase while observing/recording data! Data will be invalid while checkphase is running due to 
            phase shifting of the sampler outputs. During scans the delay output of the :py:func:`samplerstats` command can be
            used to evaluate the sampler synchronisation state.

        Returns:
            bool: True if all samplers are in sync, False otherwise
        '''

        cmd = "checkphase"
        if board is not None :
            boardNum = self.boardToDigit(board) +1
            cmd += "=%d" % (boardNum)
        ret = self.sendCommand(cmd)

        if "successful" in ret:
                return(True)
        else:
                return(False)

    def core3hstats(self, board):
        '''
        Retrieves the power levels and bit statistics of the two FIR filters


        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns:
            dictionary with the following structure::

            ["filter1"]["power"] (int): the power value for filter 1
            ["filter1"]["bstat_val"] (list of int): the 2-bit statistics; 4 values representing [11, 10, 01, 00]
            ["filter1"]["bstat_frac"] (list of float): the fractional 2-bit statistics; 4 values representing [11, 10, 01, 00]
            ["filter2"]["power"] (int): the power value for filter 1
            ["filter2"]["bstat_val"] (list of int): the 2-bit statistics; 4 values representing [11, 10, 01, 00]
            ["filter2"]["bstat_frac"] (list of float): the fractional 2-bit statistics; 4 values representing [11, 10, 01, 00]

        '''
        stats = {'filter1': {}, 'filter2': {}}
        boardNum = self.boardToDigit(board) +1
        cmd = "core3hstats=%d" % (boardNum)
        ret = self.sendCommand(cmd)

        pattern = {}
        pattern["power"] = re.compile("\s*Filter\s*(\d)\s*:\s*(\d+)")
        pattern["bstat"] = re.compile("\s*(\d{2})\s*:\s*(\d+)\s+(\d+\.\d+)\%")

        parse = ""
        for line in ret.split("\n"):
            if "Power" in line:
                parse = "power"
                continue
            elif "Bstat" in line:
                parse = "bstat"
                stats["filter1"]["bstat_val"] = []
                stats["filter2"]["bstat_val"] = []
                stats["filter1"]["bstat_frac"] = []
                stats["filter2"]["bstat_frac"] = []
                continue
            
            if parse == "bstat":
                if "Filter 1" in line:
                    filter = 1
                elif "Filter 2" in line:
                    filter = 2
            if parse == "":
                continue
            else:
                match = pattern[parse].match(line)
                if match:
                    if parse == "power": 
                        stats["filter%s" % (match.group(1))]["power"] = int(match.group(2))
                    elif parse == "bstat":
                        stats["filter%s" % (filter)]["bstat_val"].append(int(match.group(2)))
                        stats["filter%s" % (filter)]["bstat_frac"].append(float(match.group(3)))
        return (stats)


    def samplerstats(self, board):
        '''
        Retrieves and validates sampler statistics: gain, offset and delay.

        Warning: 
            The reported delay states can be incorrect in case reduced band widths are
            inserted into the DBBC3; in particular if low parts of the input bands are missing.
            In this case use :py:func:`checkphase` to validate sampler synchronisation.

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")

        Returns: 
            2-D dictionary with the following structure::

            ["power"]["val"] (list of int): a list of 4 power values; one for each sampler
            ["power"]["state"] (list of str): a list of 4 power states; one for each sampler
            ["offset"]["val"] (list of int): a list of 4 offset values; one for each sampler
            ["offset"]["frac"] (list of float): a list of 4 offset fractional values; one for each sampler
            ["offset"]["state"] (list of str): a list of 4 offset states; one for each sampler
            ["delay"]["val"] (list of int): a list of 3 delay values; one for each sampler pair (0-1, 1-2, 2-3)
            ["delay"]["state"] (list of str): a list of 3 delay states; one for each sampler pair (0-1, 1-2, 2-3)

            any state other than "OK" indicates an error

        '''
        
        stats = {}
        boardNum = self.boardToDigit(board) +1 
        cmd = "samplerstats=%d" % (boardNum)
        ret = self.sendCommand(cmd)

        pattern = {}
        pattern["power"] = re.compile("\s*Sampler\s*(\d)\s*:\s*(\d+)\[(.*)\]")
        pattern["offset"] = re.compile("\s*Sampler\s*(\d)\s*:\s*(\d+)\s+(\d+\.\d+)\%\[(.*)\]")
        pattern["delay"] = re.compile("\s*Sampler\s*(\d\-\d)\s*:\s*(\d+)\[(.*)\]")

        parse = ""
        for line in ret.split("\n"):
            if "Power" in line:
                parse = "power"
                stats["power"] = {}
                stats["power"]["val"] = []
                stats["power"]["state"] = []
                continue
            elif "Offset" in line:
                parse = "offset"
                stats["offset"] = {}
                stats["offset"]["val"] = []
                stats["offset"]["frac"] = []
                stats["offset"]["state"] = []
                continue
            elif "Delay" in line:
                parse = "delay"
                stats["delay"] = {}
                stats["delay"]["val"] = []
                stats["delay"]["state"] = []
                continue
            if parse == "":
                continue
            else:
                match = pattern[parse].match(line)
                if match:
                    if parse == "power" or parse == "delay":
                        stats[parse]["val"].append (int(match.group(2)))
                        stats[parse]["state"].append(match.group(3))
                    elif parse == "offset":
                        stats["offset"]["val"].append (int(match.group(2)))
                        stats["offset"]["frac"].append (float(match.group(3)))
                        stats["offset"]["state"].append(match.group(4))

        return (stats)

    def time(self):
        '''
        Returns the VDIF time for all boards present in the DBBC3 

        Returns:
            List of dictionaries each element representing one board (0=A) with the following structure:
                "epoch" (int): the VDIF epoch
                "second" (int): the second since the beginning of the epoch

        Raises:
            DBBC3Exception: in case no time information could be obtained
        '''

        resp = []
        ret = self.sendCommand("time")

        pattern = re.compile("\s*Board\[(\d)\]\s*:\s*Epoch:\s*(\d+),\s*Second:\s*(\d+)")
        for line in ret.split("\n"):
            match = pattern.match(line)
            if match:
                resp.append({"epoch": match.group(2), "second": match.group(3)})
        
        if not resp:
            raise DBBC3Exception("time: Did not receive any time information")
        
        return (resp)

    def tap(self, board, filterNum=None, filterFile=None):
        '''
        Sets the tap filters when in OCT mode. 

        If called without the filterNum parameter the current filter setup is returned as a dictionary
        with the following structure:

            "filter1_file" (str): the currently loaded filter definition file for filter 1
            "filter2_file" (str): the currently loaded filter definition file for filter 2

        Args:
            board (int or str): the board number (starting at 0=A) or board ID (e.g "A")
            filterNum: the filter number to set; valid inputs are 1 or 2
            filterFile: the file containing the filter coefficients. The file needs to be present in the config folder: C:\DBBC_CONF\OCT_D_120\.

        Returns:
            dict: in case the method is called without the filterNum parameter (see description for structure)
            boolean: True if the tap filter was loaded correctly, False otherwise

        Raises:
            ValueError: in case an illegal value for filterNum has been given.
            ValueError: in case no filter file has been specified
            DBBC3Exception: in case the file containing the filter coeeficients does not exist."
        '''

        boardNum = self.boardToDigit(board) +1
        cmd = "tap=%d" % (boardNum)

        reportMode = False
        if filterNum:
            if filterNum not in [1,2]:
                raise ValueError("tap: filterNum must be 1 or 2")

            if not filterFile:
                raise ValueError("tap: missing required parameter filterFile")

            cmd += ",%s,%s" % (filterNum, filterFile)
        else:
            reportMode = True

        ret = self.sendCommand(cmd)

        if reportMode:
            #>> tap=1
            #Board[1], Filter 1 has file "[c:/DBBC_CONF/OCT_D_120/2000-4000_64taps.flt]" loaded
            #Board[1], Filter 2 has file "[c:/DBBC_CONF/OCT_D_120/0-2000_64taps.flt]" loaded;
            resp = {}
            pattern = re.compile(".*Filter\s+(\d+)\s+has\s+file\s+\"\[(.+)\]\"\s+loaded")
            for line in ret.split("\n"):
                match = pattern.match(line)
                if match:
                    resp["filter%s_file" % (match.group(1))] = match.group(2)
            return (resp)
            
        else:
            if "Error" in ret:
                raise DBBC3Exception("tap: Error in the call parameters. (check that filterFile exist on the DBBC3)" )
            
            if "Taps loaded correctly" in ret:
                return(True)
            else:
                return(False)

class DBBC3Commandset_DDC_U_125(DBBC3Commandset_DDC_Common):
    '''
    Implementation of the DBBC3 commandset for the
    DDC_U mode version 125
    '''

    def __init__(self, clas):
        '''
        '''

        DBBC3Commandset_DDC_Common.__init__(self,clas)

        if (clas.config.cmdsetVersion["minorVersion"] >= 200618):
            clas.dbbcdpfu = types.MethodType (self.dbbcdpfu.__func__, clas)
            clas.dbbctp0 = types.MethodType (self.dbbctp0.__func__, clas)
            clas.dbbctdiode = types.MethodType (self.dbbctdiode.__func__, clas)

class DBBC3Commandset_DDC_L_121(DBBC3Commandset_DDC_Common):
    '''
    Implementation of the DBBC3 commandset for the
    DDC_L mode version 121
    '''

    def __init__(self, clas):
        '''
        '''
        DBBC3Commandset_DDC_Common.__init__(self,clas)

    def pps_delay(self):
        '''
        Determines the delay between the internal vs. the external PPS.
        A positive value indicates that the internal PPS is delayed with respect to the external signal.
        All delays are in units of ns.

        Returns: 
            list (float): List containing the pps delays for all 8 core3h boards (unit: ns)
        '''

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


class DBBC3Commandset_DSC_110(DBBC3CommandsetDefault):
    '''
    Implementation of the DBBC3 commandset for the
    DSC mode version 110
    '''

    def __init__(self, clas):
        '''
        '''

        DBBC3CommandsetDefault.__init__(self,clas)
