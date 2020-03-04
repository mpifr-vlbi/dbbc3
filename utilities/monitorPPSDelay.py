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
parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default 8)")
parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
parser.add_argument("--use-version", dest='ver', default= "", help="The software version of the DBBC3 DDC_V mode to use. Will assume the latest release version if not specified")
parser.add_argument("--ignore-errors", action='store_true', help="Ignore any errors and continue with the validation")
parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

args = parser.parse_args()
log = None

try:

        config = DBBC3Config()

        config.numCoreBoards = args.num_coreboards

        config.host=args.ipaddress
        config.port=args.port

        dbbc3 = DBBC3(config, mode="DDC_V", version=args.ver)
        val = DBBC3Validation(dbbc3, ignoreErrors=args.ignore_errors)
        
        print ("===Trying to connect to %s:%d" % (config.host, config.port))
        dbbc3.connect()
        print ("===Connected")
        

        useBoards = []
        if args.boards:
            for board in args.boards:
                useBoards.append(dbbc3.boardToDigit(board))
        else:
            for board in range(args.num_coreboards):
                useBoards.append(dbbc3.boardToDigit(board)) 

        log = open("dbbc3.ppsdelays", "w")
        while 1:
            line = str(datetime.now())
            for board in useBoards:
                    ret = dbbc3.pps_delay(board)
                    #print (ret)
                    line += " %d %d " % (ret[0], ret[1])

                    #ret = dbbc3.dsc_tp(board)
                    #line += " %d %d %d %d" % (ret[0], ret[1], ret[2], ret[3])
            log.write (line +"\n")
            print (line)
            sleep(1)
            


        dbbc3.disconnect()
        print ("=== Done")

except Exception as e:
        print (e)
finally:
        dbbc3.disconnect()
        if log:
            log.close()
        


