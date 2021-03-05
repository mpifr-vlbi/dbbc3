#!/usr/bin/env python

import argparse
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import traceback
import numpy as np
import logging
from datetime import datetime
from time import sleep

args = None
logger = None
dbbc3 = None
val = None
resetPPS = False
resetAdb = False


class MyValidation(DBBC3Validation):
    def __init__(self, dbbc3, logger, ignoreErrors):
        DBBC3Validation.__init__(self,dbbc3,ignoreErrors) 

        self.logger = logger
        self.errorCount = 0
        self.warnCount = 0

    def report(self, level, check="", message="", resolutionMsg = "", exit=False):

        if ("OK" in level):
            self.logger.info ("%s - %s" % (check ,message))
        elif ("WARN" in level ):
            self.logger.warning ("%s - %s" % (check ,message))
            self.warnCount += 1
        elif ("ERROR" in level ):
            self.logger.error ("%s - %s" % (check ,message))
            self.errorCount += 1


def parseCommandLine():

    parser = argparse.ArgumentParser("Carry out stability test in OCT_D mode")

    parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: %(default)s)")
#    parser.add_argument("-m", "--mode", required=True, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default %(default)s)")
    parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
    parser.add_argument("-d", "--description", default="", help="Add a description for this script execution which will be included in the log.")
#    parser.add_argument("--interval", default=60, type=int, help="Cadence of monitoring in seconds (default: %(default)s)")
    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")
    parser.add_argument("--ignore-errors", dest='ignoreErrors', default=True, action='store_true', help="Ignore any errors and continue with the validation")
    parser.add_argument("--skip-reload", dest='skipReload', default=False, action='store_true', help="Do not reload firmware at the end of the loop. (default %(default)s)")
#    parser.add_argument("--on-sampler-error", dest='onSamplerError', choices=["reset","reload"], help="Action to execute on sampler error: reset will reset samplers, reload will reload the firmware")
#    parser.add_argument("--on-pps-error", dest='onPpsError', default="resync", choices=["resync","ignore"], help="Action to execute on PPS error. (default %(default)s)")
#    parser.add_argument("--reload-interval", dest='reloadInterval', type=int, help="The interval in seconds on which to automatically reload the firmware")
#    parser.add_argument("--sampler-threshold", dest='samplerThreshold', type=int, default=170000000, help="The threshold of the sampler correlation below which a sampler desynchronization will be assumed (default %(default)s)")
    parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

    return(parser.parse_args())

def testSynthLock(useBoards):

    for board in useBoards:
        val.validateSynthesizerLock(board)

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
        if (args.mode == "DDC_V"):
            ret = dbbc3.dsc_corr(board)
        else:
            ret = dbbc3.core3h_core3_corr(board)

        #print (ret)
        samplerState.append("OK")
        if (ret[0] < args.samplerThreshold) or (ret[1] < args.samplerThreshold) or (ret[2] < args.samplerThreshold):
            resetAdb = True
            samplerState[board] = "FAIL"
            #print (dbbc3.lastResponse)

        line = "sampler corr on board %d: %s %s %s %s" % (board, ret[0], ret[1], ret[2], samplerState[board])
        logger.debug(line)
    logger.info("sampler states  {}".format(samplerState))

def logValidation (message):

    global logger
    global val

    if ("OK" in val.lastLevel):
        logger.info(val.lastMessage)
    elif ("WARN" in val.lastLevel ):
        logger.warning(val.lastMessage)
    elif ("ERROR" in val.lastLevel ):
        logger.error(val.lastMessage)
        

def main():
    global args
    global logger
    global dbbc3
    global resetAdb
    global resetPPS
    global val
    
    args = parseCommandLine()
    
    logger = logging.getLogger("monitorStability")
    logger.setLevel(logging.DEBUG)
    # create file handler
    fh = logging.FileHandler("testStabilityOCT_%s.log" % (datetime.now().strftime("%Y%m%d_%H%M%S")))
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
        dbbc3 = DBBC3(host=args.ipaddress, port=args.port, mode="OCT_D", numBoards=args.num_coreboards, timeout=1200)
    except Exception as e:
        print ("ERROR: ", e.message)

    logger.info ("=== Connected to %s:%d" % (args.ipaddress, args.port))
    logger.info ("=== Description: %s" % (args.description))
    logger.info ("=== Parameters: {}".format(args))

    useBoards = []
    if args.boards:
        for board in args.boards:
            useBoards.append(dbbc3.boardToDigit(board))
    else:
        for board in range(args.num_coreboards):
            useBoards.append(dbbc3.boardToDigit(board)) 

    val = MyValidation(dbbc3, logger, ignoreErrors=True)
    count = 1
    while True:

        try:
            dbbc3.disableloop()
            ver = dbbc3.version()
            logger.info ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))

            logger.info("=== Starting loop %d (errors=%d warnings=%d)" % (count,val.errorCount, val.warnCount))
            #logger.info("=== Checking stability of IF power")
            #for i in range(20):
            #    logger.info("dbbcifa : " + str(dbbc3.dbbcif(0)))
            #    logger.info("dbbcifb : " + str(dbbc3.dbbcif(1)))
            #    logger.info("dbbcifc : " + str(dbbc3.dbbcif(2)))
            #    logger.info("dbbcifd : " + str(dbbc3.dbbcif(3)))
            #    sleep(1)

            for board in useBoards:
                val.validateSynthesizerLock(board)
                val.validateSynthesizerFreq(board)
                val.validateIFLevel(board)
                val.validateSamplerPower(board)
                val.validateSamplerOffsets(board)
                logger.info("=== Sampler delays {}".format(dbbc3.core3h_core3_corr(board)))

            logger.info("=== Checking sampler phase synchronization" )
            val.validateSamplerPhases()

            loopFilters = 1
            #loopFilters = 0

            for i in range(loopFilters):
                for board in useBoards:
                    logger.info ("=== Loading tap filters for board " + str(board+1))
                    dbbc3.tap(board+1,"2000-4000_floating.flt")
                    dbbc3.tap2(board+1,"0-2000_floating.flt")
    #
                logger.info ("=== Setting up calibration loop")
                dbbc3.enablecal()
                logger.info ("=== Enabling calibration loop")
                dbbc3.enableloop()

                logger.info ("=== Waiting for 2 minutes to allow adjusting the power levels")
                sleep(120)

                logger.info ("=== Disabling calibration loop")
                dbbc3.disableloop()

                logger.info ("=== Now re-checking the bit statistics (should be proper 2-bit)")
                for board in useBoards:
                    val.validateBitStatistics(board)
#
            logger.info("=== Checking stability of IF power")
            for i in range(10):
                logger.info("dbbcifa : " + str(dbbc3.dbbcif(0)))
                logger.info("dbbcifb : " + str(dbbc3.dbbcif(1)))
                logger.info("dbbcifc : " + str(dbbc3.dbbcif(2)))
                logger.info("dbbcifd : " + str(dbbc3.dbbcif(3)))
                sleep(1)
#
            if (not args.skipReload):
                logger.info("=== Reloading firmware")
                dbbc3.reconfigure()

            count += 1
        except Exception as e:

# make compatible with python 2 and 3
               if hasattr(e, 'message'):
                    print(e.message)
               else:
                    print(e)
               pass

    sys.exit()


if __name__ == "__main__":
    main()
