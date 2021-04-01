#!/usr/bin/env python

import argparse
from dbbc3.DBBC3 import DBBC3
from sys import stdin
import sys
import readline

from time import sleep

if __name__ == "__main__":

        command = ""
        parser = argparse.ArgumentParser(description="Simple client to send commands to the DBBC3")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument('ipaddress',  help="the IP address of the DBBC3 running the control software")

        args = parser.parse_args()

        try:

                print ("===Trying to connect to %s:%d" % (args.ipaddress, args.port))
                dbbc3 = DBBC3(host=args.ipaddress, port=args.port )
                print ("===Connected")
                ver = dbbc3.version()
                print ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))

#                readline.read_history_file(histfile)
                # default history len is -1 (infinite), which may grow unruly
#                readline.set_history_length(1000)
                readline.set_auto_history(1)


                while command.lower().strip() != 'quit':
                        command= input(">> ")
                        dbbc3.sendCommand(command)
                        print (dbbc3.lastResponse)


        except Exception as e:
               # make compatible with python 2 and 3
               if hasattr(e, 'message'):
                    print(e.message)
               else:
                    print(e)
                    
               if 'dbbc3' in vars() or 'dbbc3' in globals():
                       dbbc3.disconnect()
                

        
