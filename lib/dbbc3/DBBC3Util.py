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
__copyright__ = "2019, Max-Planck-Institut für Radioastronomie, Bonn, Germany"
__contact__ = "rottmann[at]mpifr-bonn.mpg.de"
__license__ = "GPLv3"

from datetime import datetime
import sys
import re
import subprocess


def parseTimeResponse(response):

    year = 0
    doy = 0
    hour = 0
    minute = 0
    second = 0

    timestamp = None

    for line in response.split("\n"):
        line = line.strip()
        tok = line.split("=")

        if tok[0].strip() == "halfYearsSince2000":
            year = int(tok[1]) /2 + 2000
        elif tok[0].strip() == "seconds":
            doy = int(int(tok[1]) / 86400)
            remSecs = int(tok[1]) - doy * 86400
            hour = remSecs / 3600
            minute = (remSecs - hour*3600) / 60
            second = (remSecs - hour*3600 - minute*60)

    if year > 0:
        timestamp = datetime.strptime("%s %s %s %s %s UTC" %(year, doy+1, hour, minute, second), "%Y %j %H %M %S %Z")

    return(timestamp)

def validateOnOff(string):

    return (string in ["on", "off"])


def checkRecorderInterface (host ,device, user="oper"):
    out = subprocess.Popen("ssh {user}@{host} ip link show {device}".format(user=user, host=host,  device=device), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    start = str(out[0]).find("state") + 6
    end = str(out[0]).find("qlen")
    state = str(out[0])[start:end]

    return(state)
