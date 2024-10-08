#!/usr/bin/env python3

import argparse
import sys
import time
from dbbc3.DBBC3Multicast import DBBC3MulticastFactory
from datetime import datetime
from tkinter import *

args = None
doIgnoreFilters = True
f = None
activeBBCs = []

def parseCommandLine():

    parser = argparse.ArgumentParser("Log DBBC3 power readings to file")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    #parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", default=2, type=int, required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(int, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1,... (default: use 8 core boards)")
    parser.add_argument("-c", "--cadence", dest='cadence', type=int, required=False, default=5, help="The interval (in seconds) at which to log the power values (default: %(default)s)")
    parser.add_argument("-i", "--iface", default="0.0.0.0", type=str, required=False, help="The interface (IP) on which to listen for multicast messages (default: %(default)s; let the OS pick one.)")
    parser.add_argument("logfile", help="the output log file name")
    
    return(parser.parse_args())

def printLegendDDC_U():

    # write headline
    col = 1
    f.write("# column {}: time\n".format(col))
    for board in boards:
            col += 1
            f.write("# column {}: board {} counts\n".format(col, board))
            col += 1
            f.write("# column {}: board {} attenuation (0.5 dB steps)\n".format(col, board))
            for bbc in range(1,9):
                bbcIdx = bbc + (board)*8
                if bbcIdx not in activeBBCs:
                    continue
                
                col += 1
                f.write("# column {}: bbc {} power reported in LSB (cal on)\n".format(col, bbcIdx))
#                col += 1
#                f.write("# column {}: bbc {} power reported in LSB (cal off)\n".format(col, bbcIdx))
                col += 1
                f.write("# column {}: bbc {} power reported in USB (cal on)\n".format(col, bbcIdx))
#                col += 1
#                f.write("# column {}: bbc {} power reported in USB (cal off)\n".format(col, bbcIdx))
                col += 1
                f.write("# column {}: bbc {} LSB gain \n".format(col, bbcIdx))
                col += 1
                f.write("# column {}: bbc {} USB gain \n".format(col, bbcIdx))

    f.write("\n")

def getActiveBBCs(message):
    '''
    Determines the active BBCs based on whether the broadcasted BBC frequency is 0
    '''

    activeBBCs = []
    for board in range(1,9):
        for bbc in range(1,9):
            if message["if_{0}".format(board)]["bbc_{0}".format((board-1)*8+bbc)]["frequency"] != 0.0:
                activeBBCs.append((board-1)*8+bbc)
                #print (board, bbc, bbc+(board-1)*8, message["if_{0}".format(board)]["bbc_{0}".format(bbc+(board-1)*8)]["frequency"])

    return(activeBBCs)
        

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

 # obtain initial mc message
lastMessage = mc.poll()

f = open(args.logfile, "w")

# verify mode and version
versionFail = True
if lastMessage["mode"]  == "OCT_D" and lastMessage["majorVersion"] >= 120:
    versionFail = False
elif (lastMessage["mode"]  == "DDC_U") and (lastMessage["majorVersion"] > 125):
    versionFail = False
    activeBBCs = getActiveBBCs(lastMessage)
    printLegendDDC_U()

if versionFail:
    exit("Mode %s in version %s is not supported" % (lastMessage["mode"], lastMessage["majorVersion"]))

# for DDC_U mode determine the enabled BBCs
while True:
    mc.poll()

    f.write("{} ".format(datetime.now().replace(microsecond=0).isoformat()))
    line = ""
    print (mc.message["if_1"]["bbc_1"])
    for board in boards:
        # Per-whole-IF count and attenuation
        count = mc.message["if_{0}".format(board+1)]["count"]
        att = mc.message["if_{0}".format(board+1)]["attenuation"]
        line += "{} {} ".format(count, att)
        #print ("board: ", board+1);

        if mc.message["mode"] == "OCT_D":
            # power after applying the filters
            power1 = mc.message["if_{0}".format(board+1)]["filter1"]["power"]
            power2 = mc.message["if_{0}".format(board+1)]["filter2"]["power"]
            line += "{} {} ".format(power1, power2)
        elif mc.message["mode"] == "DDC_U":
            # loop over DDCs
            for bbc in range (1,9):
                bbcIdx = bbc + (board)*8
                if bbcIdx not in activeBBCs:
                    continue

                #print (board+1, bbc, bbcIdx)
                
                onLSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["powerOnLSB"]
#                offLSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["powerOffLSB"]
                onUSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["powerOnUSB"]
#                offUSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["powerOffUSB"]
                gainUSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["gainUSB"]
                gainLSB = mc.message["if_{0}".format(board+1)]["bbc_{0}".format(bbcIdx)]["gainLSB"]
                #line += "{} {} {} {} {} {} ".format(onLSB, offLSB, onUSB, offUSB, gainUSB, gainLSB)
                line += "{} {} {} {} ".format(onLSB, onUSB, gainLSB, gainUSB)

    f.write(line + "\n")
    f.flush()
    print (line)
    time.sleep (args.cadence)
f.close()

