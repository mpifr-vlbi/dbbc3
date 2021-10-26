#!/usr/bin/env python3

import copy
import time
import argparse
import json
import re
import threading
import queue
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dbbc3.DBBC3Multicast import DBBC3Multicast
from datetime import datetime


from tkinter import *

args = None

def thread_mcPoll(name, mc, q):
    while True:
        print ("polling ", datetime.now())
        res = mc.poll()
        res["time"] = datetime.now()
        q.put(res)
        print ("result: ", mc.message["if_1"]["mode"])

class GenericWindow(object):
    zest = "" 

    def __init__(self, parent=None, rootWidget=None):

        self.rootWidget = rootWidget
        self.parent = parent
        self.config = None
    def busy(self):
        self.rootWidget.config(cursor="watch")
        self.rootWidget.update()

    def notbusy(self):
        self.rootWidget.config(cursor="")
        self.rootWidget.update()

class MainWindow(GenericWindow):

    def __init__(self, parent=None):

        self.root = Tk()
        # call super class constructor
        super( MainWindow, self ).__init__(parent, self.root)

        self.messageVars={}
        self.activeBoards = [1,2,3,4]

        self.mc = DBBC3Multicast(args.group, args.port, args.timeout)

        # start multicast polling in its own thread
        self.q = queue.Queue(maxsize=1)
        mcThread = threading.Thread(target=thread_mcPoll, args=("mc", self.mc,  self.q), daemon = True)
        mcThread.start()
        
        # get initial mc message
        self.message = self.q.get(block=True)

        self._initVars(self.message)
        #print (self.message)

        #self.messageVars = copy.deepcopy(self.message)
        #for k, v in self.messageVars.items():
        #    print (k, v)
        #    if isinstance(v, str):
        #        self.messageVars[k] = StringVar(value=v)
        #print (self.messageVars)

        self._setupWidgets()
        self.update()
        self.root.mainloop()
        

    def show(self):
        
        self._setupWidgets()

    def getSamplerStats(self,stats):

        total = float(sum(stats))
        perc = []       
        for level in stats:
            perc.append(float(level)/total*100.0)

        return(perc)
            

    def update(self):

        message = self.q.get(block=True)
        self._initVars(message)
        self._setWidgetStates()
        #print (self.messageVars["if_1_count"].get())
        #print ("update")
        self.root.after(1000, self.update)
    
    def update2(self):

            start = time.time()
            message = self.q.get()
            print (message["mode"])
            print (message["majorVersion"])
            print (message["minorVersion"])
            print (message["minorVersionString"])
            print (datetime.now(), message["if_1"]["mode"])

            for board in self.activeBoards:
                    self.varIfCounts[board-1].set(message["if_{0}".format(board)]["count"])
                    self.varIfTarget[board-1].set(message["if_{0}".format(board)]["target"])
                    self.varIfMode[board-1].set(message["if_{0}".format(board)]["mode"])
                    self.varIfAtt[board-1].set(message["if_{0}".format(board)]["attenuation"])

                    # downconversion state
                    if message["if_{0}".format(board)]["synth"]['status'] == 1:
                        dcState = "on"
                    else:
                        dcState = "off"
                    self.varSynthState[board-1].set(dcState )

                    # synthesizer lock state
                    if dcState == "off":
                        state = ""
                        freq = ""
                        bgcolor = self.lblSynthFreq[board-1]['bg']
                    else:
                        freq = message["if_{0}".format(board)]["synth"]['frequency']*2
                        if message["if_{0}".format(board)]["synth"]['lock'] == 1:
                            state = "locked"
                            bgcolor = "green"
                        else:
                            state = "unlocked"
                            bgcolor = "red"
                    self.lblSynthLock[board-1].config(bg=bgcolor)
                    self.varSynthLock[board-1].set(state)
                    self.varSynthFreq[board-1].set(freq)

                    #color code agc settings
                    if message["if_{0}".format(board)]["mode"] != "agc":
                        self.lblMode[board-1].config(bg="red")
                    else:
                        self.lblMode[board-1].config(bg="green")

                    # color code attenuation
                    if abs(message["if_{0}".format(board)]["attenuation"] - 31) < 10:
                        self.lblAtt[board-1].config(bg="green")
                    elif abs(message["if_{0}".format(board)]["attenuation"] - 31) < 15:
                        self.lblAtt[board-1].config(bg="orange")
                    elif abs(message["if_{0}".format(board)]["attenuation"] - 31) < 20:
                        self.lblAtt[board-1].config(bg="red")
                    
                    # sampler stat plots
                    stats0 = list(message["if_{0}".format(board)]["sampler0"]["stats"])
                    stats1 = list(message["if_{0}".format(board)]["sampler1"]["stats"])
                    stats2 = list(message["if_{0}".format(board)]["sampler2"]["stats"])
                    stats3 = list(message["if_{0}".format(board)]["sampler3"]["stats"])
                    perc0 = list(message["if_{0}".format(board)]["sampler0"]["statsFrac"])
                    perc1 = list(message["if_{0}".format(board)]["sampler1"]["statsFrac"])
                    perc2 = list(message["if_{0}".format(board)]["sampler2"]["statsFrac"])
                    perc3 = list(message["if_{0}".format(board)]["sampler3"]["statsFrac"])
                    canvas0 = self.lblSampler0Stats[board-1]
                    canvas1 = self.lblSampler1Stats[board-1]
                    canvas2 = self.lblSampler2Stats[board-1]
                    canvas3 = self.lblSampler3Stats[board-1]
                    self.pltSampler0Stats[board-1].clear()
                    self.pltSampler0Stats[board-1].bar(['--','-','+','++'], stats0)
                    for index, value in enumerate(stats0):
                        print (index, value)
                        self.pltSampler0Stats[board-1].text(index-0.3, value, str(round(perc0[index],0)), fontsize='xx-small')

                    #self.pltSampler1Stats[board-1].clear()
                    #self.pltSampler1Stats[board-1].bar(['--','-','+','++'], stats1)
                    #for index, value in enumerate(stats1):
                    #    print (index, value)
                    #    self.pltSampler1Stats[board-1].text(index-0.3, value, str(round(perc1[index],0)), fontsize='xx-small')
                    #self.pltSampler2Stats[board-1].clear()
                    #self.pltSampler2Stats[board-1].bar(['--','-','+','++'], stats2)
                    #for index, value in enumerate(stats2):
                    #    print (index, value)
                    #    self.pltSampler2Stats[board-1].text(index-0.3, value, str(round(perc2[index],0)), fontsize='xx-small')
                    #self.pltSampler3Stats[board-1].clear()
                    #self.pltSampler3Stats[board-1].bar(['--','-','+','++'], stats3)
                    #for index, value in enumerate(stats3):
                    #    print (index, value)
                    #    self.pltSampler3Stats[board-1].text(index-0.3, value, str(round(perc3[index],0)), fontsize='xx-small')
                    canvas0.draw()
                    canvas1.draw()
                    canvas2.draw()
                    canvas3.draw()
                    
                    #print (message["if_{0}".format(board)]["count"])
                    #print (message["if_{0}".format(board)]["target"])
                    #print (message["if_{0}".format(board)]["attenuation"])
                    #print (message["if_{0}".format(board)]["mode"])
                    # HR
                    #print ("tsys: ", message["if_{0}".format(board)]["tsys"])
                    #print ("delayCorr: ", message["if_{0}".format(board)]["delayCorr"])
                    #print ("synth: ", message["if_{0}".format(board)]["synth"])
                    #print ("tpOn: ", message["if_{0}".format(board)]["tpOn"])
                    #print ("tpOff: ", message["if_{0}".format(board)]["tpOff"])
                    #print ("time: ", message["if_{0}".format(board)]["time"])
                    #print ("ppsDelay: ", message["if_{0}".format(board)]["ppsDelay"])
                    #print (message["if_{0}".format(board)].keys())
                    #print (message["if_1"]["bbc_1"].keys())

                    #for sNum in range(4):
                    #        print (message["if_{0}".format(board)]["sampler{0}".format(sNum)])

                    #HRfor bbc in range(8):
                        # first eight BBCs
                    #    print ("bbc_{0}".format(bbc+1+(int(board)-1)*8), message["if_{0}".format(board)]["bbc_{0}".format(bbc+1+(int(board)-1)*8)])
                        # second eight BBCs
                        #print ("bbc_{0}".format(bbc+65+(int(board)-1)*8), message["if_{0}".format(board)]["bbc_{0}".format(bbc+65+(int(board)-1)*8)])
            end = time.time()
            print("Execution time: " , end - start)        
            self.root.after(0, self.update)


    def my_callback(self, var, indx, mode):
        print ("Traced variable {} {} {}".format(var, indx, mode))

    def _setWidgetStates(self):

        for board in self.activeBoards:
            if self.messageVars["if_{}_synth_status".format(board)].get() == '1':
                pass

        
    def _initVars(self, message):

        ret = self._parseMessage(message)
        for train in ret:
            key = "_".join(train[:-1])
            if not key in self.messageVars.keys():
                self.messageVars[key] = StringVar(value=str(train[-1]))
            else:
                self.messageVars[key].set(str(train[-1]))

        # special treatment of a few fields
        for board in self.activeBoards:
            # synthesizer status
            if self.messageVars["if_{}_synth_status".format(board)].get() == '1':
                self.messageVars["if_{}_synth_status".format(board)].set("on")
                #self.messageVars["if_{}_synth_status".format(board)].trace_add('write', self.my_callback)
            else:
                self.messageVars["if_{}_synth_status".format(board)].set("off")
            # synthesizer lock
            if self.messageVars["if_{}_synth_lock".format(board)].get() == '1':
                self.messageVars["if_{}_synth_lock".format(board)].set("locked")
            else:
                self.messageVars["if_{}_synth_lock".format(board)].set("not locked")
            # synthesizer lock
            freq = float(self.messageVars["if_{}_synth_frequency".format(board)].get()) * 2
            self.messageVars["if_{}_synth_frequency".format(board)].set(str(freq))
        
        

    def _parseMessage(self, message, pre=None):
        # loop over mc message and initialize tkinter variables
        pre = pre[:] if pre else []
        if isinstance(message, dict):
            for key, value in message.items():
            #    print (key, value)
                if isinstance(value, dict):
            #        print ("pre: ", pre, "key: ", key)
                    for d in self._parseMessage(value, pre + [key]):
            #            print (d)
                        yield d
                elif isinstance(value, list) or isinstance(value, tuple):
                    for v in value:
                        for d in self._parseMessage(v, pre + [key]):
            #                print (d)
                            yield d
                else:
            #        print (pre + [key, value])
                    yield pre + [key, value]
        else:
            #print (pre + [message])
            yield pre + [message]

        
    def _setupWidgets(self):

        # menubar setup
        menubar = Menu(self.parent)
        optionmenu = Menu(menubar, tearoff=0)
        menubar.add_command(label="Exit", command=self.root.quit)

        self.root.config(menu=menubar)

        #self.btnExpert = Button(text="Toggle Expert Mode")
        #self.btnExpert.grid (row=1,column=0)

        Label(self.root, textvariable=self.messageVars["time"]).grid(row=1, column=0)
        frmIf = LabelFrame(self.root, text="IF Power")
        frmIf.grid(row=10,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSynth = LabelFrame(self.root, text="Downconversion")
        frmSynth.grid(row=20,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSampler = LabelFrame(self.root, text="Sampler")
        frmSampler.grid(row=30,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmBBC = LabelFrame(self.root, text="BBCs")
        frmBBC.grid(row=40,column=0, sticky=E+W+N+S, padx=2,pady=2)

        #self.lblCount = []
        #self.lblTarget = []
         
        self.messageComp = {}
        self.lblMode = []
        self.lblAtt = []
        self.lblName = []
        self.lblSynthState = []
        self.lblSynthLock = []
        self.lblSynthFreq = []
        self.pltSampler0Stats = []
        self.pltSampler1Stats = []
        self.pltSampler2Stats = []
        self.pltSampler3Stats = []
        self.lblSampler0Stats = []
        self.lblSampler1Stats = []
        self.lblSampler2Stats = []
        self.lblSampler3Stats = []
        self.varIfCounts = []
        self.varIfTarget = []
        self.varIfMode = []
        self.varIfAtt = []
        self.varSynthState = []
        self.varSynthLock = []
        self.varSynthFreq = []
        

        # frmIf setup
        Label(frmIf, text="counts").grid(row=2,column=0, sticky=W)
        Label(frmIf, text="target").grid(row=3,column=0, sticky=W)
        Label(frmIf, text="mode").grid(row=4,column=0, sticky=W)
        Label(frmIf, text="attenuation").grid(row=5,column=0, sticky=W)
        Label(frmSynth, text="enabled").grid(row=2,column=0, sticky=W)
        Label(frmSynth, text="locked").grid(row=3,column=0, sticky=W)
        Label(frmSynth, text="frequency").grid(row=4,column=0, sticky=W)

        # frmSampler setup
        Label(frmSampler, text="sampler 0 stats").grid(row=2,column=0, sticky=W)
        Label(frmSampler, text="sampler 1 stats").grid(row=3,column=0, sticky=W)
        Label(frmSampler, text="sampler 2 stats").grid(row=4,column=0, sticky=W)
        Label(frmSampler, text="sampler 3 stats").grid(row=5,column=0, sticky=W)
    
        for i in range(len(self.activeBoards)):
            b = self.activeBoards[i]
            frmIf.columnconfigure(i,minsize=100)
            frmSynth.columnconfigure(i,minsize=100)
            frmSampler.columnconfigure(i,minsize=100)

            Label(frmIf, text=str(i)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSynth, text=str(i)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSampler, text=str(i)).grid(row=1,column=i+1, sticky=E+W)

            #frmIf
            self.messageComp["if_{}_count".format(b)] = Button(frmIf, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_count".format(b)])
            self.messageComp["if_{}_target".format(b)] = Button(frmIf, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_target".format(b)])
            self.messageComp["if_{}_mode".format(b)] = Button(frmIf, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_mode".format(b)])
            self.messageComp["if_{}_attenuation".format(b)] = Button(frmIf, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_mode".format(b)])

            self.messageComp["if_{}_count".format(b)].grid(row=2,column=i+1, sticky=E+W)
            self.messageComp["if_{}_target".format(b)].grid(row=3,column=i+1, sticky=E+W)
            self.messageComp["if_{}_mode".format(b)].grid(row=4,column=i+1, sticky=E+W)
            self.messageComp["if_{}_attenuation".format(b)].grid(row=5,column=i+1, sticky=E+W)

            # frmSynth
            self.messageComp["if_{}_synth_status".format(b)] = Button(frmSynth, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_synth_status".format(b)])
            self.messageComp["if_{}_synth_lock".format(b)] = Button(frmSynth, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_synth_lock".format(b)])
            self.messageComp["if_{}_synth_frequency".format(b)] = Button(frmSynth, relief=SUNKEN,state=DISABLED, disabledforeground="black", textvariable=self.messageVars["if_{}_synth_frequency".format(b)])

            self.messageComp["if_{}_synth_status".format(b)].grid(row=2,column=i+1,sticky=E+W)
            self.messageComp["if_{}_synth_lock".format(b)].grid(row=3,column=i+1,sticky=E+W)
            self.messageComp["if_{}_synth_frequency".format(b)].grid(row=4,column=i+1,sticky=E+W)

            # frmSampler
            fig = plt.Figure(figsize=(0.8,0.8))
            ax = fig.add_subplot(111)
            self.pltSampler0Stats.append(ax)
            self.lblSampler0Stats.append(FigureCanvasTkAgg(fig,frmSampler))
            self.lblSampler0Stats[i].get_tk_widget().grid(row=2,column=i+1,sticky=E+W)
            #fig = plt.Figure(figsize=(0.8,0.8))
            #ax = fig.add_subplot(111)
            #self.pltSampler1Stats.append(ax)
            #self.lblSampler1Stats.append(FigureCanvasTkAgg(fig,frmSampler))
            #self.lblSampler1Stats[i].get_tk_widget().grid(row=3,column=i+1,sticky=E+W)
            #fig = plt.Figure(figsize=(0.8,0.8))
            #ax = fig.add_subplot(111)
            #self.pltSampler2Stats.append(ax)
            #self.lblSampler2Stats.append(FigureCanvasTkAgg(fig,frmSampler))
            #self.lblSampler2Stats[i].get_tk_widget().grid(row=4,column=i+1,sticky=E+W)
            #fig = plt.Figure(figsize=(0.8,0.8))
            #ax = fig.add_subplot(111)
            #self.pltSampler3Stats.append(ax)
            #self.lblSampler3Stats.append(FigureCanvasTkAgg(fig,frmSampler))
            #self.lblSampler3Stats[i].get_tk_widget().grid(row=5,column=i+1,sticky=E+W)

            #boardFrames.append(tmpFrame)

    def updateBoardInfo(self, message):

        pass
        

def parseCommandLine():

    parser = argparse.ArgumentParser("Check dbbc3 multicast")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
#    parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", required=False, help="The maximum number of seconds to wait for a multicast message.")
#    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")

    return(parser.parse_args())

args = parseCommandLine()

mainDlg = MainWindow(None)


