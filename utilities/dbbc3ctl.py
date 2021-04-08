#!/usr/bin/env python

import argparse
import subprocess
import sys
import DBBC3Util as d3u
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
from cmd import Cmd

from time import sleep

checkTree = {"system":"#board", "sampler":{"offset":"#board","gain":"#board","phase":"#board"}, "timesync":"#board", "synthesizer":{"lock":"#board", "freq":"#board"}, "bstate": "#board" }
printTree = {"setup":"#board"}
commandTree = {"check": checkTree, "reconfigure": "", "print": printTree}

class Prompt(Cmd):

    def __init__(self, dbbc3, boards):
        Cmd.__init__(self)
        self.intro = 'Welcome to the DBBC3.  Type help or ? to list commands'
        self.prompt = '(dbbc3ctl): '
        self.path = []
        self.cmdChains = []
        self.cmdList = []
        self.dbbc3 = dbbc3
        self.val = DBBC3Validation(self.dbbc3, ignoreErrors=True)
        self.boards = boards
        self.parseCmdTree(commandTree)
        #print (self.cmdChains)

    def parseCmdTree(self, tree):

        for k,v in tree.items():
          if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
            self.path.append(k)
            if (v =="#board"):
                self.cmdChains.append("{} {}".format(" ".join(self.path), "all")) 
                self.cmdList.append(("{} [all,{}]".format(" ".join(self.path), ",".join([str(board) for board in self.boards]) )))
                for board in self.boards:
                    self.cmdChains.append("{} {}".format(" ".join(self.path), board))
            self.path.pop()
          elif v is None:
            self.path.append(k)
            ## do something special
            self.path.pop()
          elif isinstance(v, dict):
            self.path.append(k)
            self.parseCmdTree(v)
            self.path.pop()
          else:
            print ("###Type {} not recognized: {}.{}={}".format(type(v), ".".join(self.path),k, v))

        
    def completenames(self, text, *ignored):
        # Modified tab complete to add extra space after command
        dotext = 'do_'+text
        return [a[3:]+' ' for a in self.get_names() if a.startswith(dotext)]

    def default(self, line):
    
        print ("Usage:")
        for chain in self.cmdList:
            print (chain)
    
    def completedefault(self, text, line, start_index, end_index):

        matches = []
        for chain in self.cmdChains:
            if chain.startswith(line):
                matches.append(chain[start_index:])
        return(matches)
            
    def _resolveBoards(self, board):
        if board == "all":
            boards = self.boards
        else:
            boards = [board]

        return(boards)
        
    def do_help (self, topic):
        for cmd in self.cmdList:
            if (cmd.startswith(topic)):
                print (cmd)

    def _checkSynthesizer(self, subcommand, boards):
        for board in boards:
            if subcommand == "lock":
                self.val.validateSynthesizerLock(board)
            elif subcommand == "freq":
                self.val.validateSynthesizerFreq(board)
        
    def do_check(self, args):

        print (args)
        fields = args.split()

        boards = self.boards
        
        if fields[0] == "sampler":
            if len(fields) == 1:
                self.do_help("check sampler")
                return

            if fields[1] == "phase":
                self.val.validateSamplerPhases()
            else:
                if len(fields) == 3:
                    boards = self._resolveBoards(fields[2])
                for board in boards:
                    if fields[1] == "offset":
                        self.val.validateSamplerOffsets(board)
                    elif fields[1] == "gain":
                        self.val.validateSamplerPower(board)
        elif fields[0] == "timesync":
            if len(fields) == 2:
                boards = self._resolveBoards(fields[1])
            for board in boards:
                self.val.validateTimesync(board)
        elif fields[0] == "synthesizer":
            if len(fields) == 3:
                boards = self._resolveBoards(fields[2])
            self._checkSynthesizer(fields[1], boards)
        elif fields[0] == "bstate":
            if len(fields) == 2:
                boards = self._resolveBoards(fields[1])
            for board in boards:
                val.validateBitStatistics(board)
                

        
        
    def do_quit(self,args ):
        sys.exit(0)



if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Setup and validate DBBC3 in OCT_D mode")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
        parser.add_argument("-y", "--yes", help="Answer yes to all interactive confirmations.")
        parser.add_argument("-c", "--command", type=str,  help="exectute the given commandi.")
        parser.add_argument('ipaddress',  help="the IP address of the DBBC3 running the control software")
        

        #parser.add_argument("--ignore-errors", dest='ignoreErrors',default=False, action='store_true', help="Ignore any errors and continue with the validation")
        #parser.add_argument("-m", "--mode", required=False, default="OCT_D", help="The current DBBC3 mode (default: %(default)s)")
        #parser.add_argument("-n", "--num-coreboards",  type=int, help="The number of activated core boards in the DBBC3 (default 8)")

        args = parser.parse_args()
        
        #prompt = Prompt(None, [0,1,2,3])
        #prompt.cmdloop()
        
        try:

                print ("===Trying to connect to %s:%d" % (args.ipaddress, args.port))
                dbbc3 = DBBC3(host=args.ipaddress, port=args.port)
                print ("===Connected")

                ver = dbbc3.version()
                print ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))

                val = DBBC3Validation(dbbc3, ignoreErrors=True)


                useBoards = []
                if args.boards:
                    for board in args.boards:
                        useBoards.append(dbbc3.boardToDigit(board))
                else:
                    for board in range(dbbc3.config.numCoreBoards):
                        useBoards.append(dbbc3.boardToDigit(board))

                print ("=== Using boards: %s" % str(useBoards))

                prompt = Prompt(dbbc3, useBoards)

                if (args.command):
                    prompt.onecmd(args.command)

                prompt.cmdloop()

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
                

        


