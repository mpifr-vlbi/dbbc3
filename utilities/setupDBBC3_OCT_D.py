#!/usr/bin/env python

import argparse
import subprocess
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import dbbc3.DBBC3Util as d3u
import re
import sys
import numpy as np
import traceback

from time import sleep

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Setup and validate DBBC3 in OCT_D mode")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument("-n", "--num-coreboards",  type=int, help="The number of activated core boards in the DBBC3 (default 8)")
        parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
        parser.add_argument("--use-version", dest='ver', default= "", help="The software version of the DBBC3 DDC_V mode to use. Will assume the latest release version if not specified")
        parser.add_argument("--ignore-errors", dest='ignoreErrors',default=False, action='store_true', help="Ignore any errors and continue with the validation")
        parser.add_argument('ipaddress',  help="the IP address of the DBBC3 running the control software")
        parser.add_argument("-m", "--mode", required=False, default="OCT_D", help="The current DBBC3 mode (default: %(default)s)")

        args = parser.parse_args()

        try:

                print ("===Trying to connect to %s:%d" % (args.ipaddress, args.port))
                dbbc3 = DBBC3(host=args.ipaddress, port=args.port, mode=args.mode)
                print ("===Connected")

                ver = dbbc3.version()
                print ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))

                val = DBBC3Validation(dbbc3, ignoreErrors=args.ignoreErrors)

                print ("=== Disabling calibration loop")
                dbbc3.disableloop()

                useBoards = []
                if args.boards:
                    for board in args.boards:
                        useBoards.append(dbbc3.boardToDigit(board))
                elif args.num_coreboards:
                    for board in range(args.num_coreboards):
                        useBoards.append(dbbc3.boardToDigit(board))
                else:
                    for board in range(dbbc3.config.numCoreBoards):
                        useBoards.append(dbbc3.boardToDigit(board))

                print ("=== Using boards: %s" % str(useBoards))

                print ("==============================================")
                print ("NOTE: the following tests should be done with")
                print ("only noise fed to the IF inputs of the DBBC3.")
                print ("Injecting additional tones can lead to false")
                print ("results in the validation of the sampler states.")
                print ("==============================================")


                print ("=== Checking sampler phase synchronisation")
                val.validateSamplerPhases()

                print ("=== Checking state of recorder interfaces" )
                print ("=== recorder1 eth3: %s" % d3u.checkRecorderInterface ("recorder1", "eth3"))
                print ("=== recorder1 eth5: %s" % d3u.checkRecorderInterface ("recorder1", "eth5"))
                print ("=== recorder2 eth3: %s" % d3u.checkRecorderInterface ("recorder2", "eth3"))
                print ("=== recorder2 eth5: %s" % d3u.checkRecorderInterface ("recorder2", "eth5"))
                print ("=== recorder3 eth3: %s" % d3u.checkRecorderInterface ("recorder3", "eth3"))
                print ("=== recorder3 eth5: %s" % d3u.checkRecorderInterface ("recorder3", "eth5"))
                print ("=== recorder4 eth3: %s" % d3u.checkRecorderInterface ("recorder4", "eth3"))
                print ("=== recorder4 eth5: %s" % d3u.checkRecorderInterface ("recorder4", "eth5"))
                
                for board in useBoards:

                    val.validateTimesync(board)
                    #print ("IF before offset check", dbbc3.dbbcif(board))
                    val.validateSynthesizerLock(board)
                    val.validateSynthesizerFreq(board)
                    val.validateIFLevel(board)
                    val.validateSamplerPower(board)
                    val.validateSamplerOffsets(board)
               #     print ("IF after offset check", dbbc3.dbbcif(board))


                # load tap filters (extra script)
                try: input = raw_input
                except NameError: pass
                response = input ("Do you want to load the tap filters now? [y/n]  ")
                if (response == "y"):
                    for board in useBoards:
                        print ("=== Loading tap filters for board " + str(board+1))
                        dbbc3.tap(board+1,"2000-4000_floating.flt")
                        dbbc3.tap2(board+1,"0-2000_floating.flt")
                    print ("=== Setting up calibration loop")
                    dbbc3.enablecal()
                    print ("=== Enabling calibration loop")
                    dbbc3.enableloop()

                    print ("=== Waiting for 2 minutes to allow adjusting the power levels")
                    for remaining in range(120, 0, -1):
                        sys.stdout.write("\r")
                        sys.stdout.write("{:2d} seconds remaining.".format(remaining))
                        sys.stdout.flush()
                        sleep(1)
                    
                    dbbc3.disableloop()

                print ("=== Now re-checking the bit statistics (should be proper 2-bit)")
                for board in useBoards:
                    val.validateBitStatistics(board)

                print ("=== Setting up calibration loop")
                dbbc3.enablecal()
                print ("=== Enabling calibration loop")
                dbbc3.enableloop()
                
                dbbc3.disconnect()
                print ("=== Done")

        except Exception as e:
               # make compatible with python 2 and 3
               if hasattr(e, 'message'):
                    print(e.message)
               else:
                    print(e)
                    
               if 'dbbc3' in vars() or 'dbbc3' in globals():
                       dbbc3.disconnect()
                

        
