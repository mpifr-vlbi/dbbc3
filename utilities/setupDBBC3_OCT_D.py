#!/usr/bin/env python

import argparse
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
import re
import sys
import numpy as np

from time import sleep

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Setup and validate DBBC3 in OCT_D mode")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default 8)")
        parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
        parser.add_argument("--use-version", dest='ver', default= "", help="The software version of the DBBC3 DDC_V mode to use. Will assume the latest release version if not specified")
        parser.add_argument("--ignore-errors", action='store_true', help="Ignore any errors and continue with the validation")
        parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")

        args = parser.parse_args()

        try:
                config = DBBC3Config()

                config.numCoreBoards = args.num_coreboards

                config.host=args.ipaddress
                config.port=args.port

                #dbbc3 = DBBC3(config, mode="DDC_V", version=args.ver)


                dbbc3 = DBBC3(config, mode="OCT_D", version=args.ver)
                
                dbbc3.connect()


                print ("=== Disabling calibration loop")
                dbbc3.disableloop()

                val = DBBC3Validation(dbbc3, ignoreErrors=True)

                useBoards = []
                if args.boards:
                    for board in args.boards:
                        useBoards.append(dbbc3.boardToDigit(board))
                else:
                    for board in range(args.num_coreboards):
                        useBoards.append(dbbc3.boardToDigit(board))

                print (dbbc3.version())

                for board in useBoards:

                    val.validateSynthesizerLock(board)
                    val.validateSynthesizerFreq(board)
                    val.validateIFLevel(board)
                    val.validateSamplerPower(board)
                    val.validateSamplerOffsets(board)

                val.validateSamplerPhases()

                # load tap filters (extra script)
                response = input("Do you want to set the tap filters now? [y/n]")
                if response == "y":
                    for board in useBoards:
                        print ("=== Loading tap filters for board " + str(board+1))
                        dbbc3.tap(board+1,"2000-4000_floating.flt")
                        dbbc3.tap2(board+1,"0-2000_floating.flt")
                else:   
                        sys.exit(0)

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
                    val.validateSamplerOffsets(board)

                print ("=== Setting up calibration loop")
                dbbc3.enablecal()
                print ("=== Enabling calibration loop")
                dbbc3.enableloop()
                
                dbbc3.disconnect()
                print ("=== Done")

        except Exception as e:
               print (e.message)
               dbbc3.disconnect()
                

        
