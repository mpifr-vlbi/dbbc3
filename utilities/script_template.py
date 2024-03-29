#!/usr/bin/env python

import argparse
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation

parser = argparse.ArgumentParser(description="ADD DESCRIPTIONOF YOUR SCRIPT")

parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: %(default)s)")
parser.add_argument("-n", "--num-coreboards", default=8, type=int, help="The number of activated core boards in the DBBC3 (default: %(default)s)")
parser.add_argument("-i", "--if", dest='boards', nargs="+", help="A list of core boards to be used for setup and validation. (e.g. -i A C E). If not specified will use all activated core boards.")
parser.add_argument("--use-version", dest='ver', default= "", help="The software version of the DBBC3 DDC_V mode to use. Will assume the latest release version if not specified")
parser.add_argument("--ignore-errors", dest='ignoreErrors',default=False, action='store_true', help="Ignore any errors and continue with the validation")
parser.add_argument('ipaddress', help="the IP address of the DBBC3 running the control software")
parser.add_argument("-m", "--mode", required=False, default="DDC_V", help="The current DBBC3 mode (default: %(default)s)")

args = parser.parse_args()

try:

        print ("===Trying to connect to %s:%d" % (args.ipaddress, args.port))
        dbbc3 = DBBC3(host=args.ipaddress, port=args.port, mode=args.mode)
        print ("===Connected")

        ver = dbbc3.version()
        print ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))
       # print (dbbc3.version())
        
        val = DBBC3Validation(dbbc3, ignoreErrors=args.ignoreErrors)

        useBoards = []
        if args.boards:
            for board in args.boards:
                useBoards.append(dbbc3.boardToDigit(board))
        else:
            for board in range(args.num_coreboards):
                useBoards.append(dbbc3.boardToDigit(board)) 


        for board in useBoards:
                print ("=== Processing board %d" % (board))
                # add your code here 

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
