#!/usr/bin/env python

import logging
import argparse
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import traceback
import numpy as np

from datetime import datetime
from time import sleep

args = None
logger = None
dbbc3 = None
resetPPS = False
resetAdb = False

def parseCommandLine():

    parser = argparse.ArgumentParser("Monitor and log the PPS delay values.")

    parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: %(default)s)")
    parser.add_argument("-m", "--mode", required=True, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default %(default)s)")
    parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
    parser.add_argument("--interval", default=60, type=int, help="Cadence of monitoring in seconds (default: %(default)s)")
    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")
#    parser.add_argument("--ignore-errors", action='store_true', help="Ignore any errors and continue with the validation")
    parser.add_argument("--on-sampler-error", dest='onSamplerError', choices=["reset","reload"], help="Action to execute on sampler error: reset will reset samplers, reload will reload the firmware")
    parser.add_argument("--on-pps-error", dest='onPpsError', default="resync", choices=["resync","ignore"], help="Action to execute on PPS error. (default %(default)s)")
    parser.add_argument("--reload-interval", dest='reloadInterval', type=int, help="The interval in seconds on which to automatically reload the firmware")
    parser.add_argument("--sampler-threshold", dest='samplerThreshold', type=int, default=170000000, help="The threshold of the sampler correlation below which a sampler desynchronization will be assumed (default %(default)s)")
    parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

    return(parser.parse_args())

def resetPPSSync():
    if (args.onPpsError == "resync"):
        logger.info ("=== resyncing the PPS (pps_sync)")
        dbbc3.pps_sync()

def resetADB3L():
    
    if (args.onSamplerError == "reset"):
        logger.info ("=== resetting all ADB3L boards (reseth)")
        dbbc3.adb3l_reseth()

    elif (args.onSamplerError == "reload"):
        logger.info ("=== reloading firmware")
        dbbc3.core3h_reconfigure()


def testPPSSync(useBoards):
    global resetPPS

    ppsState = []
    for board in useBoards:
        ret = dbbc3.pps_delay(board)
        ppsState.append("OK")

        if  (ret[0] > 2000):
            resetPPS = True
            ppsState[board] = "FAIL"
        line = "pps_sync on board %d: %d %d %s" % (board, ret[0], ret[1], ppsState[board])
        logger.debug(line)
    logger.info("pps states  {}".format(ppsState))
#
def testSamplerSync(useBoards):
    global resetAdb

    samplerState = []
    for board in useBoards:
        ret = dbbc3.core3h_core3_corr(board)

        samplerState.append("OK")
        if (ret[0] < args.samplerThreshold) or (ret[1] < args.samplerThreshold) or (ret[2] < args.samplerThreshold):
            resetAdb = True
            samplerState[board] = "FAIL"

        line = "sampler corr on board %d: %s %s %s %s" % (board, ret[0], ret[1], ret[2], samplerState[board])
        logger.debug(line)
    logger.info("sampler states  {}".format(samplerState))

def main():
    global args
    global logger
    global dbbc3
    global resetAdb
    global resetPPS
    
    args = parseCommandLine()
    
    logger = logging.getLogger("monitorStability")
    logger.setLevel(logging.DEBUG)
    # create file handler
    fh = logging.FileHandler("stability_%s_%s.log" % (args.mode, datetime.now().strftime("%Y%m%d_%H%M%S")))
    # create console handler
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    try:

            logger.debug ("=== Trying to connect to %s:%d" % (args.ipaddress, args.port))
            dbbc3 = DBBC3(host=args.ipaddress, port=args.port, mode=args.mode, numBoards=args.num_coreboards, version=args.ver)
            #val = DBBC3Validation(dbbc3, ignoreErrors=args.ignore_errors)
            
            logger.info ("=== Connected to %s:%d" % (args.ipaddress, args.port))
            logger.info ("=== Test parameters: {}".format(args))
            
            useBoards = []
            if args.boards:
                for board in args.boards:
                    useBoards.append(dbbc3.boardToDigit(board))
            else:
                for board in range(args.num_coreboards):
                    useBoards.append(dbbc3.boardToDigit(board)) 

            testPPS = False
            testSamplers = True

            if (args.mode.startswith("DDC")):
                testPPS = True

           # dbbc3.disableloop()
            if (testPPS):
                dbbc3.pps_sync()

            reloadStart = datetime.now()

            while 1:
                line = ""
                resetPPS = False
                resetAdb = False

                samplerState = []

                # check for firmware reload
                if (args.reloadInterval):
                    if ((datetime.now() - reloadStart).total_seconds() > args.reloadInterval):
                        logger.info("reloading firmware (currently disabled)")
                        reloadStart = datetime.now()
                        #dbbc3.reconfigure()

                if (testSamplers):
                    testSamplerSync(useBoards)

                if (testPPS):
                    testPPSSync(useBoards)

                if (resetAdb):
                    if (args.onSamplerError):
                        resetADB3L()
                        resetPPS= True

                    resetAdb = False

                if (resetPPS):
                    resetPPSSync()
                    resetPPS= False
                    


                sleep(args.interval)

            dbbc3.disconnect()
            logger.info ("=== Done")

    except Exception as e:
            print ("ERROR: ", e.message)
    #        traceback.print_exc(file=sys.stdout)
            
    finally:
            if (dbbc3):
                dbbc3.disconnect()
            

if __name__ == "__main__":
    main()
