#!/usr/bin/env python

import argparse
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import numpy as np

from datetime import datetime
from time import sleep

parser = argparse.ArgumentParser("Monitor and log the PPS delay values.")

parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
parser.add_argument("-m", "--mode", required=True, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default 8)")
parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")
parser.add_argument("--ignore-errors", action='store_true', help="Ignore any errors and continue with the validation")
parser.add_argument("--reset-on-error", action='store_true', help="Reset ADB3L boards in case of sampler drifts")
parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

args = parser.parse_args()
log = None

try:

        config = DBBC3Config()

        config.numCoreBoards = args.num_coreboards

        config.host=args.ipaddress
        config.port=args.port

        dbbc3 = DBBC3(config, mode=args.mode, version=args.ver)
        val = DBBC3Validation(dbbc3, ignoreErrors=args.ignore_errors)
        
        print ("===Trying to connect to %s:%d" % (config.host, config.port))
        dbbc3.connect()
        print ("===Connected")
        
        version = dbbc3.version()
        if (version["mode"] != args.mode):
            raise Exception("You requested mode %s but current firmware loaded is %s" %(args.mode, version["mode"]))    

        useBoards = []
        if args.boards:
            for board in args.boards:
                useBoards.append(dbbc3.boardToDigit(board))
        else:
            for board in range(args.num_coreboards):
                useBoards.append(dbbc3.boardToDigit(board)) 


        log = open("stability_%s_%s.log" % (args.mode, datetime.now().strftime("%Y%m%d_%H%M%S")), "w")

        if (args.mode.startswith("DDC")):
            dbbc3.pps_sync()

       # dbbc3.disableloop()

        ppsState = ""
        samplerState = ""
        while 1:
            line = str(datetime.now())
            resetPPS = False
            resetAdb = False
            for board in useBoards:
                    if (args.mode.startswith("DDC")):
                        ret = dbbc3.pps_delay(board)
                        line += " %d %d " % (ret[0], ret[1])
                        ppsState = " PPS: OK "
                        if  (ret[0] > 4000):
                            resetPPS = True
                            ppsState = " PPS: FAIL "
    #
                    ret = dbbc3.core3h_core3_corr(board)
                    line += " %s %s %s " % (ret[0], ret[1], ret[2])

                    samplerState = " Samplers: OK "
                    if (ret[0] < 170000000) or (ret[1] < 170000000) or (ret[2] < 170000000):
                        resetAdb = True
                        samplerState = " Samplers: FAIL "

            line += ppsState + samplerState
            log.write (line  + "\n")
            print (line)
            if (args.reset_on_error):
                if (resetAdb):
                    log.write (" # Resetting all ADB3L boards\n")
                    print ("# Resetting all ADB3L boards")
                    dbbc3.adb3l_reset()
                    resetAdb = False
                    resetPPS= True
                if (resetPPS):
                    log.write (" # Resyncing the PPS\n")
                    print ("# Resyncing the PPS")
                    dbbc3.pps_sync()
                    resetPPS= False
            sleep(60)

        dbbc3.disconnect()
        print ("=== Done")

except Exception as e:
        print (e)
        
finally:
        dbbc3.disconnect()
        if log:
            log.close()
        


