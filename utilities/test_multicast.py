#!/usr/bin/env python

import argparse
import json
import re
from dbbc3.DBBC3Multicast import DBBC3MulticastFactory

args = None

def parseCommandLine():

    parser = argparse.ArgumentParser("Check dbbc3 multicast")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")

    return(parser.parse_args())



    
args = parseCommandLine()

mcFactory = DBBC3MulticastFactory()
mc = mcFactory.create()


#mc = DBBC3Multicast(args.group, args.port, args.timeout)

while(True):
    print ("polling")
    ret = mc.poll(serialize=True)
    
    for key,value in ret.items():
        print (key, ": ", value)

    #out = json.dumps(ret, indent=2, sort_keys=True,separators=(', ', ': '))
    #print (out)



    
