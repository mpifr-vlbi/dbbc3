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
  This module is part of the DBBC3 package and provides utility methods
'''

__author__ = "Helge Rottmann"
__copyright__ = "2022, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

from datetime import datetime, timezone
import sys
import re
import subprocess


def vdiftimeToUTC(epoch, seconds):

    year = 0
    doy = 0
    hour = 0
    minute = 0
    second = 0
    timestamp = None

    year = epoch // 2 + 2000
    if (epoch % 2) == 0:
        # even epochs start at midnight (UTC) January 1st 
        halfYearDays = 1
    else:
        # odd epochs start at midnight (UTC) July 1st
        halfYearDays = 183

    doy = seconds // 86400 + halfYearDays

    remSecs = seconds - (doy - halfYearDays) * 86400
    hour = remSecs // 3600
    minute = (remSecs - hour*3600) // 60
    second = (remSecs - hour*3600 - minute*60)

    timestamp = datetime.strptime("%s %s %s %s %s UTC" %(year, doy, hour, minute, second), "%Y %j %H %M %S %Z")

    timestamp = timestamp.replace(tzinfo=timezone.utc)

    return(timestamp)


def parseTimeResponse(response):
    '''
    Parses response of the core3h timesync command (VDIF time) and converts it into datetime (UTC)

    Args:
        response (str): the reposnse string as provided by the core3h_timesync command

    Returns:
        datetime: the datetime representation of the returned timesync reponse; None in case of failure
    '''

#    year = 0
#    doy = 0
#    hour = 0
#    minute = 0
#    second = 0

    timestamp = None

    # Response in DSC_120 (with timestamp set and by GPS)
    # Time synchronization...
    # Mark5B time : years=23, MJD=60262, secs=51330
    # VDIF time   : epoch=47, secs=11801730
    # Time synchronization succeeded!

    #vdiftime:epoch=47,secs=11806973
    patVDIF = re.compile("vdiftime:epoch=(\d+),secs=(\d+)")

    for line in response.split("\n"):

        line = line.strip().lower().replace(" ","");

        tok = line.split("=")

        match = patVDIF.match(line)

        if (match):
            timestamp = vdiftimeToUTC(int(match.group(1)), int(match.group(2)))
         #   year = int(match.group(1)) // 2 + 2000
         #   if (int(match.group(1)) % 2) == 0:
         #       halfYearDays = 1
         #   else:
         #       halfYearDays = 182
#
#            doy = int(match.group(2)) // 86400 + halfYearDays

#            remSecs = int(match.group(2)) - (doy - halfYearDays) * 86400
#            hour = remSecs // 3600 
#            minute = (remSecs - hour*3600) // 60
#            second = (remSecs - hour*3600 - minute*60)
            #print (year, halfYearDays, doy, hour, minute, second)

#            timestamp = datetime.strptime("%s %s %s %s %s UTC" %(year, doy, hour, minute, second), "%Y %j %H %M %S %Z")
            break

#    print (val, timestamp)
    return(timestamp)


def parseTimeResponseLegacy(response):
    '''
    Parses response of the core3h timesync command (VDIF time) and converts it into datetime (UTC)

    Args:
        response (str): the reposnse string as provided by the core3h_timesync command

    Returns:
        datetime: the datetime representation of the returned timesync reponse
    '''


    year = 0
    doy = 0
    hour = 0
    minute = 0
    second = 0

    timestamp = None

    # Response in DSC_120 (with timestamp set and by GPS)
    # Time synchronization...
    # Mark5B time : years=23, MJD=60262, secs=51330
    # VDIF time   : epoch=47, secs=11801730
    # Time synchronization succeeded!

    for line in response.split("\n"):

        #halfYearsSince2000 = 47
        #seconds = 11790442
        #daysSince2000 = 8582

        line = line.strip()
        tok = line.split("=")

        if tok[0].strip() == "halfYearsSince2000":
            year = int(tok[1]) // 2 + 2000
            if (year % 2) == 0:
                halfYearDays = 1
            else:
                halfYearDays = 182

        elif tok[0].strip() == "seconds":
            # seconds are relative to VDIF epoch start
            seconds = int(tok[1])

            doy = seconds // 86400 + halfYearDays
            remSecs = int(tok[1]) - (doy - halfYearDays) * 86400
            hour = remSecs // 3600
            minute = (remSecs - hour*3600) // 60
            second = (remSecs - hour*3600 - minute*60)

    #        print (year, halfYearDays, doy, hour, minute, second)

    if year > 0:
        timestamp = datetime.strptime("%s %s %s %s %s UTC" %(year, doy, hour, minute, second), "%Y %j %H %M %S %Z")

    return(timestamp)

def validateOnOff(string):
    '''
    Validates the argument to be "on" or "off"

    Args:
       string (str): the input string to check

    Returns:
        boolean: True if input string is either "on" or "off". False otherwise

    '''

    return (string in ["on", "off"])


def checkRecorderInterface (host ,device, user="oper"):
    """
    Returns the state of the given ethernet device on the given host

    Args:
        host (str): the hostname or IP addres of the host to probe
        device (str): the name of the network device to check
        user (str, optional): the ssh user name to use to carry out the check

    Returns:
        str: the state of the given device as provided by the ip link show command
    """
    out = subprocess.Popen("ssh {user}@{host} ip link show {device}".format(user=user, host=host,  device=device), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    start = str(out[0]).find("state") + 6
    end = str(out[0]).find("qlen")
    state = str(out[0])[start:end]

    return(state)
