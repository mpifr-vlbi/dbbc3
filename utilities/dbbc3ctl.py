#!/usr/bin/env python

import argparse
import time
import threading
import subprocess
import itertools
import logging
import sys
from datetime import datetime
import dbbc3.DBBC3Util as d3u
from dbbc3.DBBC3 import DBBC3
from dbbc3.DBBC3Config import DBBC3Config
from dbbc3.DBBC3Validation import ValidationFactory
from cmd import Cmd
from signal import signal, SIGINT

from time import sleep

checkTree = {"recorder":"@host @interface", "sampler":{"offset":"#board","gain":"#board","phase":"#board"}, "timesync":"#board", "synthesizer":{"lock":"#board", "freq":"#board"}, "bstate": "#board", "pps":"", "system": "#board" }
printTree = {"setup":"#board"}
commandTree = {"check": checkTree }

logger = None


def decorateEmit(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[0].levelno
        level = ""
        if(levelno >= logging.CRITICAL):
            color = '\x1b[31;1m'
            level = "[{}]".format(args[0].levelname)
        elif(levelno >= logging.ERROR):
            color = '\x1b[31;1m'
            level = "[{}]".format(args[0].levelname)
        elif(levelno >= logging.WARNING):
            color = '\x1b[35;1m'
            level = "[{}]".format(args[0].levelname)
        else:
            color = '\x1b[0m'

        args[0].msg = args[0].msg.replace("OK", "\033[1;32mOK\033[0m")
        args[0].msg = args[0].msg.replace("RESOLUTION", "\033[1;34mRESOLUTION\033[0m")

        # color the levelname
        args[0].msg = "{}{}\x1b[0m{}".format(color, level, args[0].msg)

        return fn(*args)
    return new

def reportResult(rep):
    
    if not rep:
        return

    for res in rep.result:

        if "INFO" in res.level:
            logger.info("[{0}] {1} - {2}".format(res.state,  res.action, res.message))
        elif ("WARN" in res.level ):
            logger.warn("[{0}]/[{1}] {2} - {3}".format(res.state, res.level, res.action, res.message))
        elif ("ERROR" in res.level ):
            logger.error("[{0}]/[{1}] {2} - {3}".format(res.state, res.level, res.action, res.message))

        if len(res.resolution) > 0:
            print("\033[1;34m[{0}] {1}\033[0m".format("RESOLUTION",  res.resolution))

class Spinner:

    def __init__(self, message, delay=0.1):
        self.spinner = itertools.cycle(['-', "-",'/', '|', '\\'])
        self.spinner = itertools.cycle(['-', '\\', '|','/'])
        self.delay = delay
        self.busy = False
        self.spinner_visible = False
        sys.stdout.write(message)

    def write_next(self):
        with self._screen_lock:
            if not self.spinner_visible:
                sys.stdout.write(next(self.spinner))
                self.spinner_visible = True
                sys.stdout.flush()

    def remove_spinner(self, cleanup=False):
        with self._screen_lock:
            if self.spinner_visible:
                sys.stdout.write('\b')
                self.spinner_visible = False
                if cleanup:
                    sys.stdout.write(' ')       # overwrite spinner with blank
                    sys.stdout.write('\r')      # move to next line
                sys.stdout.flush()

    def spinner_task(self):
        while self.busy:
            self.write_next()
            time.sleep(self.delay)
            self.remove_spinner()

    def __enter__(self):
        if sys.stdout.isatty():
            self._screen_lock = threading.Lock()
            self.busy = True
            self.thread = threading.Thread(target=self.spinner_task)
            self.thread.start()

    def __exit__(self, exception, value, tb):
        if sys.stdout.isatty():
            self.busy = False
            self.remove_spinner(cleanup=True)
        else:
            sys.stdout.write('\r')
class Prompt(Cmd):

    def __init__(self, dbbc3, boards, val):
        Cmd.__init__(self)
        self.intro = 'Welcome to the DBBC3.  Type help or ? to list commands'
        self.prompt = '(dbbc3ctl): '
        self.path = []
        self.cmdChains = []
        self.cmdList = []
        self.dbbc3 = dbbc3
        self.val = val
        self.boards = boards
        self.parseCmdTree(commandTree)
        #print (self.cmdChains)

    def parseCmdTree(self, tree):

        for k,v in tree.items():
          if isinstance(v, str) or isinstance(v, int) or isinstance(v, float):
            self.path.append(k)
            if (v =="#board"):
                self.cmdChains.append("{0} {1}".format(" ".join(self.path), "all")) 
                self.cmdList.append(("{0} [all,{1}]".format(" ".join(self.path), ",".join([str(board) for board in self.boards]) )))
                for board in self.boards:
                    self.cmdChains.append("{0} {1}".format(" ".join(self.path), board))
                #print (self.path)
                self.path.pop()
            # parameters 
            elif (v.startswith('@')):
                subs = v.split(' ')
                self.cmdChains.append(" ".join(self.path))
                self.cmdList.append("{0} {1} ".format(" ".join(self.path)," ".join(subs)))
                self.path.pop()
            else:
                self.cmdChains.append(" ".join(self.path))
                self.cmdList.append("{0}".format(" ".join(self.path)))
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
            print ("###Type {} not recognized: {0}.{1}={2}".format(type(v), ".".join(self.path),k, v))

        
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
        elif board.isdigit():
            if int(board) in self.boards:
                boards = [board]
            else:
                self.do_help("")
                return([])
        else:
            self.do_help("")
            return([])

        return(boards)
        
    def do_help (self, topic):
        for cmd in self.cmdList:
            if (cmd.startswith(topic)):
                print (cmd)

    def _checkSystemDDC_U(self, boards):

        logger.info ("=== Doing full system validation of {0} mode".format(self.dbbc3.config.mode))
        with Spinner(""):
            rep = val.validateSamplerPhases()
        reportResult(rep)

        for board in boards:
            logger.info ("=== Checking board {0}".format(board))
            reportResult(val.validatePPS())
            reportResult(val.validateTimesync(board))
            reportResult(val.validateSynthesizerLock(board))
            reportResult(val.validateSynthesizerFreq(board))
            reportResult(val.validateIFLevel(board))
            with Spinner(""):
                rep = val.validateSamplerPower(board)
            reportResult(rep)
            with Spinner(""):
                rep = val.validateSamplerOffsets(board)
            reportResult(rep)

            reportResult(val.validateBitStatistics(board)) 

    def _checkSynthesizer(self, subcommand, boards):
        for board in boards:
            if subcommand == "lock":
                ret = self.val.validateSynthesizerLock(board)
            elif subcommand == "freq":
                ret = self.val.validateSynthesizerFreq(board)

            reportResult(ret)
        
    def _noteSamplerTest(self):
        print ("==============================================")
        print ("NOTE: the following tests should be done with")
        print ("noise only fed to the IF inputs of the DBBC3.")
        print ("Injecting additional tones can lead to false")
        print ("results in the validation of the sampler states.")

        print ("==============================================")

    def _checkRecorder(self, args):
        if len(args) != 3:
            self.do_help("check recorder")
            return
        d3u.checkRecorderInterface(args[1], args[2])
        logger.info ("=== %s %s: %s" % (args[1], args[2], d3u.checkRecorderInterface (args[1], args[2])))

    def _checkSamplerGain(self, fields):

        self._noteSamplerTest()
        boards = self.boards

        if len(fields) == 3:
            boards = self._resolveBoards(fields[2])
        
        for board in boards:
            reportResult(self.val.validateSamplerPower(board))
    def _checkSamplerOffset(self, fields):

        self._noteSamplerTest()
        boards = self.boards

        if len(fields) == 3:
            boards = self._resolveBoards(fields[2])
        
        for board in boards:
            with Spinner(""):
                ret = self.val.validateSamplerOffsets(board)
            reportResult(ret)
        

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
                reportResult(self.val.validateBitStatistics(board))
        elif fields[0] == "pps":
            reportResult(self.val.validatePPS())
        elif fields[0] == "system":
            
            if len(fields) == 2:
                boards = self._resolveBoards(fields[1])
            if (self.dbbc3.config.mode == "DDC_U"):
                self._noteSamplerTest()
                self._checkSystemDDC_U(boards)
            else:
                print ("'check system' not yet supported for the current mode")
            
        elif fields[0] == "recorder":
            self._checkRecorder(fields)
        
        
    def do_quit(self,args ):
        exitClean() 



def exitClean():

    # reset to the state upon creating the Validation instance
    if 'val' in vars() or 'val' in globals():
        val.restoreState()

    if 'dbbc3' in vars() or 'dbbc3' in globals():

        # re-enable the calibration loop
        if (dbbc3.config.cmdsetVersion['mode'] == "OCT_D" and int(dbbc3.config.cmdsetVersion['majorVersion']) < 120):
             logger.info("=== Re-enabling  calibration loop")
             dbbc3.enableloop()
         
        dbbc3.disconnect()
    print ("Bye")
    sys.exit()

def signal_handler(sig, frame):
    exitClean()

def setupLogger():
    global logger

    logger = logging.getLogger(__name__)

    logger.setLevel(logging.DEBUG)
    if (args.log):
        # create file handler
        fh = logging.FileHandler("dbbc3ctl_%s.log" % (datetime.now().strftime("%Y%m%d_%H%M%S")))
        logformatter = logging.Formatter('%(asctime)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        fh.setFormatter(logformatter)
        logger.addHandler(fh)

    # create console handler
    ch = logging.StreamHandler()
    # create formatter and add it to the handlers
    scnformatter = logging.Formatter('%(message)s')
    ch.setFormatter(scnformatter)
    ch.emit = decorateEmit(ch.emit)
    # add the handlers to the logger
    logger.addHandler(ch)


# handle SIGINT (Ctrl-C)
signal(SIGINT, signal_handler)

if __name__ == "__main__":

        parser = argparse.ArgumentParser(description="DBBC3 Control and Monitoring Client")

        parser.add_argument("-p", "--port", default=4000, type=int, help="The port of the control software socket (default: 4000)")
        parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
        parser.add_argument("-y", "--yes", help="Answer yes to all interactive confirmations.")
        parser.add_argument("-c", "--command", action='append', type=str,  help="Exectute the given command(s). If this option is specified  multiple times the commands will be processed in the order they appear on the command line.")
        parser.add_argument("-r", "--repeat",
             type=int,
             help="Repeat the commands given by the -c option N times; For repeating indefinetly give -1")
        parser.add_argument("-l", "--log",
             action='store_true',
             help="Write log output to file.")
        parser.add_argument('ipaddress',  help="the IP address of the DBBC3 running the control software")
        
        args = parser.parse_args()

        if (args.repeat and not args.command):
            print ("Looping is only done on commands supplied by the -c option. Ignoring the --repeat switch")
            args.repeat = None

        setupLogger()

        try:

                logger.debug ("=== Trying to connect to %s:%d" % (args.ipaddress, args.port))
                dbbc3 = DBBC3(host=args.ipaddress, port=args.port)
                logger.info ("=== Connected")

                ver = dbbc3.version()
                logger.info ("=== DBBC3 is running: mode=%s version=%s(%s)" % (ver['mode'], ver['majorVersion'], ver['minorVersion']))

                valFactory = ValidationFactory()
                val = valFactory.create(dbbc3, True)

                # for OCT_D mode prior to version 120 disable the calibration loop to speed up processing
                if (ver['mode'] == "OCT_D" and int(ver['majorVersion']) < 120):
                    logger.info( "=== Disabling calibration loop  to speed up command processing")
                    dbbc3.disableloop()

                useBoards = []
                #print (dbbc3.config.numCoreBoards)
                if args.boards:
                    for board in args.boards:
                        useBoards.append(dbbc3.boardToDigit(board))
                else:
                    for board in range(dbbc3.config.numCoreBoards):
                        useBoards.append(dbbc3.boardToDigit(board))

                logger.info( "=== Using boards: %s" % str(useBoards))

                prompt = Prompt(dbbc3, useBoards, val)

                count = 0
                if (args.command):
                    if not args.repeat:
                        loop = 1
                    elif args.repeat == -1:
                        loop = 1e10
                    else:
                        loop = args.repeat
                            
                    while count < loop:
                        for command in args.command:
                            prompt.onecmd(command)
                        count += 1

                    exitClean()
                    

                prompt.cmdloop()

        except Exception as e:
           
           # make compatible with python 2 and 3
           if hasattr(e, 'message'):
                print("An error has occured: {0}".format(e.message))
           else:
                print(e)
#
           exitClean()
                    
                

        


