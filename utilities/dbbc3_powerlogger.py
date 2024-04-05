#!/usr/bin/env python3

import argparse
import sys
from dbbc3.DBBC3Multicast import DBBC3MulticastFactory
from datetime import datetime
from tkinter import *

args = None
doIgnoreFilters = False

def parseCommandLine():

    parser = argparse.ArgumentParser("Log DBBC3 power readings to file")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    #parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", default=2, type=int, required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(int, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1,... (default: use 8 core boards)")
    parser.add_argument("-i", "--iface", default="0.0.0.0", type=str, required=False, help="The interface (IP) on which to listen for multicast messages (default: %(default)s; let the OS pick one.)")
    parser.add_argument("logfile", help="the output log file name")
    
    return(parser.parse_args())

args = parseCommandLine()

mcFactory = DBBC3MulticastFactory()
print ("Trying to connect....", end='', flush=True)
mc = mcFactory.create(args.group, args.port, args.timeout, args.iface)
print ("connected")

board = 1
if args.boards:
    boards = args.boards
else:
    boards = [0,1,2,3,4,5,6,7]

f = open(args.logfile, "w")


# write headline
col = 1
f.write("# column {}: time\n".format(col))
if doIgnoreFilters:
    for board in boards:
        col += 1
        f.write("# column {}: board {} counts\n".format(col, board))
        col += 1
        f.write("# column {}: board {} attenuation (0.5 dB steps)\n".format(col, board))
else:
    for board in boards:
        col += 1
        f.write("# column {}: board {} power reported in filter1\n".format(col, board))
        col += 1
        f.write("# column {}: board {} power reported in filter2\n".format(col, board))
        col += 1
        f.write("# column {}: board {} attenuation (0.5 dB steps)\n".format(col, board))
f.write("\n")

while True:
    mc.poll()
    f.write("{} ".format(datetime.now().replace(microsecond=0).isoformat()))
    line = ""
    for board in boards:
        if doIgnoreFilters:
            # Per-whole-IF count and attenuation
            count = mc.message["if_{0}".format(board+1)]["count"]
            att = mc.message["if_{0}".format(board+1)]["attenuation"]
            line += "{} {} ".format(count, att)
            #f.write("{} {} ".format(count, att))
        else:
            power1 = mc.message["if_{0}".format(board+1)]["filter1"]["power"]
            power2 = mc.message["if_{0}".format(board+1)]["filter2"]["power"]
            att = mc.message["if_{0}".format(board+1)]["attenuation"]
            line += "{} {} {}".format(power1, power2, att)
            #f.write("{} {} {}".format(power1, power2, att))
    f.write(line + "\n")
    f.flush()
    print (line)

f.close()

