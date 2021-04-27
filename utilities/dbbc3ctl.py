#!/usr/bin/env python

import argparse
import subprocess
import sys
import dbbc3.DBBC3Util as d3u
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import DBBC3Validation
from cmd import Cmd
from signal import signal, SIGINT

from time import sleep

checkTree = {"recorder":"@host @interface", "system":"#board", "sampler":{"offset":"#board","gain":"#board","phase":"#board"}, "timesync":"#board", "synthesizer":{"lock":"#board", "freq":"#board"}, "bstate": "#board" }
printTree = {"setup":"#board"}
commandTree = {"check": checkTree }

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
            # parameters 
            elif (v.startswith('@')):
                subs = v.split(' ')
                self.cmdChains.append(" ".join(self.path))
                self.cmdList.append("{} {} ".format(" ".join(self.path)," ".join(subs)))
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
            if int(board) in self.boards:
                boards = [board]
            else:
                self.do_help("")
                return([])

        return(boards)
        
    def do_help (self, topic):
        for cmd in self.cmdList:
            if (cmd.startswith(topic)):
                print (cmd)

    def _checkSynthesizer(self, subcommand, boards):
        for board in boards:
            if subcommand == "lock":
                ret = self.val.validateSynthesizerLock(board)
            elif subcommand == "freq":
                ret = self.val.validateSynthesizerFreq(board)

           reportResult(ret) 
        
    def _checkRecorder(self, args):
        if len(args) != 3:
            self.do_help("check recorder")
            return
        d3u.checkRecorderInterface(args[1], args[2])
        print ("=== %s %s: %s" % (args[1], args[2], d3u.checkRecorderInterface (args[1], args[2])))

    def _checkSamplerGain(self, fields):

        boards = self.boards

        if len(fields) == 3:
            boards = self._resolveBoards(fields[2])
        
        for board in boards:
            reportResult(self.val.validateSamplerPower(board))
    def _checkSamplerOffset(self, fields):

        boards = self.boards

        if len(fields) == 3:
            boards = self._resolveBoards(fields[2])
        
        for board in boards:
            reportResults(self.val.validateSamplerOffsets(board))
        

    def do_check(self, args):

        fields = args.split()

        boards = self.boards
        
        if fields[0] == "sampler":
            if len(fields) == 1:
                self.do_help("check sampler")
                return

            if fields[1] == "phase":
                reportResult(self.val.validateSamplerPhases())
            elif fields[1] == "offset":
                ret = self._checkSamplerOffset(fields)
            elif fields[1] == "gain":
                reportResult(self._checkSamplerGain(fields))
        elif fields[0] == "timesync":
            if len(fields) == 2:
                boards = self._resolveBoards(fields[1])
            for board in boards:
                reportResult(self.val.validateTimesync(board))
        elif fields[0] == "synthesizer":
            if len(fields) == 3:
                boards = self._resolveBoards(fields[2])
            self._checkSynthesizer(fields[1], boards)
        elif fields[0] == "bstate":
            if len(fields) == 2:
                boards = self._resolveBoards(fields[1])
            for board in boards:
                reportResult(val.validateBitStatistics(board))
        elif fields[0] == "recorder":
            self._checkRecorder(fields)
        
        
    def do_quit(self,args ):
        exitClean() 


def exitClean():
    if 'dbbc3' in vars() or 'dbbc3' in globals():
        # re-enable the calibration loop
        if (dbbc3.config.mode.startswith("OCT")):
             dbbc3.enableloop()
         
        dbbc3.disconnect()
    print ("Bye")
    sys.exit()

def signal_handler(sig, frame):
    exitClean()

# handle SIGINT (Ctrl-C)
signal(SIGINT, signal_handler)

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="Setup and validate DBBC3 in OCT_D mode")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
        parser.add_argument("-y", "--yes", help="Answer yes to all interactive confirmations.")
        parser.add_argument("-c", "--command", action='append', type=str,  help="Exectute the given command(s). If this option is specified  multiple times the commands will be processed in the order they appear on the command line.")
        parser.add_argument('ipaddress',  help="the IP address of the DBBC3 running the control software")
        
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

                # for OCT mode disable the calibration loop to speed up processing
                if (dbbc3.config.mode.startswith("OCT")):
                    dbbc3.disableloop()

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
                    for command in args.command:
                        prompt.onecmd(command)

                prompt.cmdloop()

        except Exception as e:
           
           # make compatible with python 2 and 3
           if hasattr(e, 'message'):
                print(e.message)
           else:
                print(e)

           exitClean()
                    
                

        


