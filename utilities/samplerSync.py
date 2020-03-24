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

def parseCommandLine():

    parser = argparse.ArgumentParser("Check and establish sampler synchronization")

    parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: %(default)s)")
    parser.add_argument("-m", "--mode", required=True, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")
#    parser.add_argument("--ignore-errors", action='store_true', help="Ignore any errors and continue with the validation")
    parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

    return(parser.parse_args())


def main():
    global args
    global logger
    global dbbc3
    
    args = parseCommandLine()
    
    logger = logging.getLogger("samplerSync")
    logger.setLevel(logging.DEBUG)
    # create file handler
    fh = logging.FileHandler("samplerSync_%s.log" % (datetime.now().strftime("%Y%m%d_%H%M%S")))
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
            dbbc3 = DBBC3(host=args.ipaddress, port=args.port, mode=args.mode, version=args.ver)
            
            logger.info ("=== Connected to %s:%d" % (args.ipaddress, args.port))
            logger.info ("=== Parameters: {}".format(args))
            
            #useBoards = []
            #if args.boards:
            #    for board in args.boards:
            #        useBoards.append(dbbc3.boardToDigit(board))
            #else:
            #    for board in range(args.num_coreboards):
            #        useBoards.append(dbbc3.boardToDigit(board)) 

            count = 1
            logger.info("checking if samplers are in sync")
            while (dbbc3.checkphase() == False):
                logger.info ("checkphase: failed. Attempt %d" % count)
                logger.info ("resetting samplers")
                dbbc3.adb3l_reseth()
                count += 1

            logger.info("sync OK")
            dbbc3.disconnect()
            logger.info ("=== Done")

    except Exception as e:
            print ("ERROR: ", e.message)
            traceback.print_exc(file=sys.stdout)
            
    finally:
            if (dbbc3):
                dbbc3.disconnect()
            

if __name__ == "__main__":
    main()
