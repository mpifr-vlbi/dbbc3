#!/usr/bin/env python3

import copy
import collections
import time
import argparse
import json
import re
import threading
import queue
from tkinter import *
from tkinter import font
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animate
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dbbc3.DBBC3Multicast import DBBC3MulticastFactory
from datetime import datetime
import numpy as np
from matplotlib.figure import Figure
from random import seed, gauss
from operator import add
from abc import ABC

args = None


class Generic2DPlot (ABC):

    def __init__(self, ax, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.tdata = [0]
        self.ydata = [0]
        self.line = Line2D(self.tdata, self.ydata)
        self.ax.add_line(self.line)
        self.ax.set_ylim(-.1, 1.1)
        self.ax.set_xlim(0, self.maxt)


class PlotCounts ():
    def __init__(self, ax, activeBoards, maxt=2, dt=0.02):
        self.ax = ax
        self.dt = dt
        self.maxt = maxt
        self.activeBoards = activeBoards
        self.ydata = []
        self.lines = []

        self.tdata = [0]
        for board in self.activeBoards:
            if board:
                self.ydata.append([0])
                line = Line2D(self.tdata, [0])
                self.ax.add_line(line)
                self.lines.append(line)
        self.ax.set_ylim(0, 35000)
        self.ax.set_xlim(0, self.maxt)

    def update(self, y):
        lastt = self.tdata[-1]
        #if lastt > self.tdata[0] + self.maxt:  # reset the arrays
        #    self.tdata = [self.tdata[-1]]
            #self.ydata = [self.ydata[-1]]
        #    self.ax.set_xlim(self.tdata[0], self.tdata[0] + self.maxt)
            #self.ax.set_ylim(min(self.ydata), max(self.ydata))
            #self.ax.figure.canvas.draw()

        t = self.tdata[-1] + self.dt
        self.tdata.append(t)
        for i in range(len(self.lines)):
            self.ydata[i].append(y+i*1000)
            self.lines[i].set_data(self.tdata, self.ydata[i])
        #return self.lines,
        return self.lines


#def emitter(p=0.1):
#    """Return a random value in [0, 1) with probability p, else 0."""
#    while True:
#        v = np.random.rand(1)
#        if v > p:
#            yield 0.
#        else:
#            yield np.random.rand(1)
#
def thread_mcPoll(name, mc, q):
    """
    Thread that polls the latest multicast message
    """

    while True:
        print ("polling ", datetime.now())
        res = mc.poll()

        # include receive time in the message
        res["time"] = datetime.now()

        seed(datetime.now().microsecond)
        for board in range(1,9):
            # create random values when in simulation mode
            if (args.simulate):
                res["if_{}".format(board)]["count"] = int(32000 + gauss(0, 1000))
            # estimate total power from count values
            res["if_{}".format(board)]["power"] = float(mc.message["if_{}".format(board)]["count"]) / 1420.0 + float(mc.message["if_{}".format(board)]["attenuation"]) / 2.0

        q.put(res)

class MainWindow():

    def __init__(self, parent=None):

        self.root = Tk()

        self.messageVars={}

        if (args.boards):
            self.activeBoards = list(args.boards)
        else:
            self.activeBoards = [0,1,2,3,4,5,6,7]

        self.counts = {} 
        self.power = {} 
        self.pltCounts = {}
        self.pltPower = {}
        self.pltSamplerStats = {}
        #self.canvasSampler = {}
        for board in self.activeBoards:
            self.counts[board] = collections.deque(maxlen=100)
            self.power[board] = collections.deque(maxlen=100)
        
        mcFactory = DBBC3MulticastFactory()
        self.mc = mcFactory.create()

        # start multicast polling in its own thread
        self.q = queue.Queue(maxsize=1)
        mcThread = threading.Thread(target=thread_mcPoll, args=("mc", self.mc,  self.q), daemon = True)
        mcThread.start()
        
        # start the message parsing loop (1 sec)
        self.updateMessage()

        self.setActiveBoards()

        self._setupWidgets()
        self._setupTabIF() 
        #self.update2()
        self.root.mainloop()
        
    def setActiveBoards(self):

         # check if active / present boards are broadcasted over multicast
        if "boardPresent" in self.lastMessage.keys():
            present = np.array(list(self.lastMessage["boardPresent"]))
        else:
            present = np.array([1,1,1,1,1,1,1,1], dtype=bool)

        self.activeBoards =  np.array([0,0,0,0,0,0,0,0], dtype=bool)

        if (args.boards):
            for board in list(args.boards):
                if present[int(board)]:
                    self.activeBoards[int(board)] = True
        else:
            if "boardActive" in self.lastMessage.keys():
                self.activeBoards = np.array(list(self.lastMessage["boardActive"]), dtype=bool)
            else:
                self.activeBoards = present
            
        print ("present: ", present)
        print ("Active: ", self.activeBoards)

    def busy(self):
        self.root.config(cursor="watch")
        self.root.update()

    def notbusy(self):
        self.root.config(cursor="")

    def getSamplerStats(self,stats):

        total = float(sum(stats))
        perc = []       
        for level in stats:
            perc.append(float(level)/total*100.0)

        return(perc)
            

    def updateTabIF(self):
        # update tabIF (if visible)
        if self.notebook.index(self.notebook.select()) == 0:
            for board in self.activeBoards:
                fig = self.pltPower[board].figure
                self.pltCounts[board].set_xdata(list(range(-1*len(self.counts[board])+1,1,1)))
                self.pltCounts[board].set_ydata(list(self.counts[board]))
                self.pltPower[board].set_xdata(list(range(-1*len(self.power[board])+1,1,1)))
                self.pltPower[board].set_ydata(list(self.power[board]))
                #print (self.pltPower[board].figure.axes)
            for axis in fig.axes:
                axis.relim()
                axis.autoscale_view()
        #self.canvasCounts.draw()

    def updateTabSampler(self):

        # update tabSampler (if visible)
        if self.notebook.index(self.notebook.select()) == 1:
            for i in range(len(self.activeBoards)):
                b = self.activeBoards[i]

                states = []
                #rect = self.pltSamplerStats[b].get_children()
                #print (rect)
                #print (len(rect))
                for s in range(4):
                    key ="if_{}_sampler{}_statsFrac".format(b,s)
                    stats = self.messageVars[key].get()[1:-1].split(",")
                    #print (self.messageVars[key].get())
                    stats = list(map(float, stats))
                    #print (stats)
                    for j in range(4):
                        states.append(stats[j])
                   #     rect[7].set_width(stats[0])
                    
#
                #print (states)
                start = [0,0,0,0]
                for state in range(4):
                    rect = self.pltSamplerStats[b][state].get_children()
                   ## print (len(rect))
                    for s in range(4):
                       # print (b, state, s, states[state+4*s], start[s])
                        rect[s].set_width(states[state+4*s])
                        rect[s].set_x(start[s])
                        start[s] += states[state+4*s]
                    
#               # loop over states
                #start = 0
                #for rect in self.pltSamplerStats[b].get_children():
                #    for i in range(4):
                #        start = [0,0,0,0]
                #        for j in range(4):
                #            rect.set_width(states[i+4*j])
                #            rect.set_x(start[j])
                #            print ("boxes: ", b,i,j, i+4*j, states[i+4*j], start[j], rect.get_y())
                #            start[j] += states[i+4*j]
#
                    #for j in range(4):
                        #states[j].append(stats[j])
                    #    for rect in self.pltSamplerStats[b][sampler][j].get_children():
                    #        rect.set_width(stats[j])
                    #        rect.set_x(start)
                    #        print ("boxes: ", b,sampler,j, stats[j], start)
                    #        start += stats[j]

        #self.canvasSampler.draw()


    def update2(self):
        print("update2")
        self.root.after(2000, self.update2)

    def updateMessage(self):

        print ("updateMessage")
        # obtain new message from multicast reader thread
        self.lastMessage = self.q.get(block=True)

        #serialize the message
        self._initVars(self.lastMessage)

        print (self.messageVars["if_1_count"].get())

        # update the state of the various widgets
        #self._setWidgetStates()
        self.root.after(1000, self.updateMessage)

        #self.updateTabIF() 
#       #self.updateTabSampler() 
        #print (self.messageVars["if_1_count"].get())
        #print ("update")
    
    def _setWidgetStates(self):

        for board in self.activeBoards:
            board += 1
            # IF dashboard
            key = "if_{}_mode".format(board)
            val = self.messageVars[key].get()
            if val == 'agc':
                self.messageComp[key].configure(style="OK.TButton")
            else:
                self.messageComp[key].configure(style="WARN.TButton")

            # sampler dashboard
            #for s in range(4):
            #    key = "if_{}_sampler{}_state".format(board, s)
            #    state = self.messageVars[key].get()
            #  # print (state)
            #    if state == 'OK':
            #        self.messageComp[key].configure(style="OK.TButton")
            #    elif state == 'WARN':
            #        self.messageComp[key].configure(style="WARN.TButton")
            #    elif state == 'ERROR':
            #        self.messageComp[key].configure(style="ERROR.TButton")
            #    else:
            #        self.messageComp[key].configure(style="My.TButton")

        
    def _setStringVar(self, key, value):

        if not key in self.messageVars.keys():
            self.messageVars[key] = StringVar(value=str(value))
        else:
            self.messageVars[key].set(str(value))
    def _getSamplerState(self, board):

        ret = ["OK", "OK", "OK", "OK"]
        meanPower = 0
        power = []
        for s in range(4):
            key ="if_{}_sampler{}_statsFrac".format(board,s)
            stats = list(map(float, self.messageVars[key].get()[1:-1].split(",")))
            if abs(stats[0] +stats[1] -50.0) > 5.0:
                ret[s] = "warning"
            elif abs(stats[0] +stats[1] -50.0) > 10.0:
                ret[s] = "error"

            key ="if_{}_sampler{}_power".format(board,s)
            power.append(float(self.messageVars[key].get()))
            meanPower += float(self.messageVars[key].get()) / 4
            #print (self.messageVars[key].get(), meanPower)


        for s in range(4):
            if meanPower == 0.0:
                ret[s] = "--"
            elif abs(1 -  power[s]/ meanPower) > 0.05:
                ret[s] = "warning"
            elif abs(1 -  power[s]/ meanPower) > 0.2:
                ret[s] = "error"

        return ret

    def _initVars(self, message):

        # serialize multicast message 
        ret = self._parseMessage(message)

        # autoassign StringVars
        for train in ret:
            key = "_".join(train[:-1])
            self._setStringVar(key, train[-1])

        # special treatment for a number of message items
        for board in range(1,9):
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

            #store count and power values in list
            #self.counts[board-1].append(int(self.messageVars["if_{}_count".format(board)].get()))
            #self.power[board-1].append(float(self.messageVars["if_{}_power".format(board)].get()))

            # check sampler states
            #state = self._getSamplerState(board)
            #print (state)
            ##for s in range(4):
            #    self._setStringVar("if_{}_sampler{}_state".format(board,s), state[s])
                

        

    def _parseMessage(self, message, pre=None):
        # loop over mc message and serialize it.
        # the train of keys and values will be returned
        # and will be used as keys for the various tkinter variables and components

        pre = pre[:] if pre else []

        if isinstance(message, dict):
            for key, value in message.items():
            #    print (key, value)
                if isinstance(value, dict):
            #        print ("pre: ", pre, "key: ", key)
                    for d in self._parseMessage(value, pre + [key]):
            #            print (d)
                        yield d
                #elif isinstance(value, list) or isinstance(value, tuple):
                #elif isinstance(value, list):
                #    for v in value:
                #        for d in self._parseMessage(v, pre + [key]):
                #            print (v, d)
                #            yield d
                else:
            #        print (pre + [key, value])
                    yield pre + [key, value]
        else:
            #print (pre + [message])
            yield pre + [message]

        
    def _setupTabIF(self):

        tabIF = ttk.Frame(self.notebook, width=400, height=280)
        tabIF.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabIF, text='Total Power') 

        # tabIF 
#        fig,axes = plt.subplots(2,1,constrained_layout=True)
#        for board in self.activeBoards:
#            print(self.activeBoards, board)
            #self.pltCounts[board], = axes[0].plot([0],[32000], label=str(board), animated=False)
            #self.pltPower[board], = axes[1].plot([0],[1000], label=str(board), animated=False)
#            self.pltCounts[board], = axes[0].plot([0],[32000], label=str(board), animated=True)
#            self.pltPower[board], = axes[1].plot([0],[1000], label=str(board), animated=True)

#        axes[0].set_title ("Counts", fontsize=16)
#        axes[0].set_ylabel("counts", fontsize=11)
#        axes[0].set_xlabel("time[s]", fontsize=11)
#        axes[0].set_ylim([30000,40000])
#        axes[0].set_xlim([-100,0])
#        axes[0].grid(True)
#        axes[0].legend(fontsize='x-small', loc=2)
#        axes[1].set_title ("Total power", fontsize=16)
#        axes[1].set_ylabel("dBm", fontsize=11)
#        axes[1].set_xlabel("time[s]", fontsize=11)
##        axes[1].set_ylim([0,100])
#        axes[1].set_xlim([-100,0])
#        axes[1].grid(True)
#        axes[1].legend(fontsize='x-small', loc=2)
#

        fig, ax = plt.subplots()
        ax.set_title ("Counts", fontsize=16)
        ax.set_ylabel("counts", fontsize=11)
        ax.set_xlabel("time[s]", fontsize=11)
        ax.set_ylim([30000,40000])
        ax.set_xlim([-100,0])
        ax.grid(True)
        ax.legend(fontsize='x-small', loc=2)

        #pltCounts = PlotCounts(ax, self.activeBoards)
        #self.aniCounts = animate.FuncAnimation(fig, pltCounts.update, self.genCounts, interval=500, blit=True)
        #self.canvasCounts = FigureCanvasTkAgg(fig, master=tabIF)
        #self.canvasCounts.get_tk_widget().pack()
        #self.canvasCounts.draw()
#
    def genCounts(self):
        
        yield (float(self.messageVars["if_{}_count".format(1)].get()))

    def _setupTabSampler(self):

        tabSampler = ttk.Frame(self.notebook, width=400, height=280)
        tabSampler.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabSampler, text='Sampler Details') 

        # tabSampler
        frmSamplerPower = LabelFrame(tabSampler, text="Sampler powers")
        frmSamplerPower.grid(row=0,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmSamplerPower, text="samp. 0").grid(row=2,column=0, sticky=E+W)
        Label(frmSamplerPower, text="samp. 1").grid(row=3,column=0, sticky=E+W)
        Label(frmSamplerPower, text="samp. 2").grid(row=4,column=0, sticky=E+W)
        Label(frmSamplerPower, text="samp. 3").grid(row=5,column=0, sticky=E+W)

        frmSamplerStats = LabelFrame(tabSampler, text="Sampler offsets")
        frmSamplerStats.grid(row=10,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmSamplerStats, text="samp. 0").grid(row=2,column=0, sticky=E+W)
        Label(frmSamplerStats, text="samp. 1").grid(row=3,column=0, sticky=E+W)
        Label(frmSamplerStats, text="samp. 2").grid(row=4,column=0, sticky=E+W)
        Label(frmSamplerStats, text="samp. 3").grid(row=5,column=0, sticky=E+W)

        
        frmSamplerPlots = LabelFrame(tabSampler, text="Sampler stats")
        frmSamplerPlots.grid(row=20,column=0,sticky=E+W+S+N, padx=10, pady=10)

        labels = ["0", "1", "2", "3"]
        levels = ['--','-+','+-','++']
        stateColors = ["lightgreen","green","dodgerblue","lightblue"]

        fig,axes = plt.subplots(2, 4, constrained_layout=True, sharex='all', sharey='all', figsize=(7,3))
        #fig.set_size_inches(3,2)
        axes[0][0].set_xlim([0,100])

        #fig.set_size_inches(1, 1)
        for i in range(len(self.activeBoards)):
            b = self.activeBoards[i]
            Label(frmSamplerPower, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            states = [[],[],[],[]]
            self.pltSamplerStats[b] = []
            for sampler in range(4):
                key ="if_{}_sampler{}_power".format(b,sampler)
                self.messageComp[key] = ttk.Button(frmSamplerPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
                self.messageComp[key].grid(row=2+sampler,column=i+1, sticky=E+W)

                key ="if_{}_sampler{}_statsFrac".format(b,sampler)
                for state in range(4):
                    self.messageComp["{}_{}".format(key,state)] = ttk.Button(frmSamplerStats, style="My.TButton", state=DISABLED, width=6, textvariable=self.messageVars[key])
                    self.messageComp["{}_{}".format(key,state)].grid(row=2+sampler+state,column=i+1, sticky=E+W)
                stats = self.messageVars[key].get()[1:-1].split(",")
                stats = list(map(float, stats))
                
                col = i - int(i/4)*4
                for j in range(4):
                    states[j].append(stats[j])
                    plot = axes[int(i/4)][col].barh(labels, [0,0,0,0], height=0.5, edgecolor='black', color=stateColors[j])
                    axes[int(i/4)][col].axvline(47.5, linewidth=0.2, color='black', ls=":")
                    axes[int(i/4)][col].axvline(52.5, linewidth=0.2, color='black', ls=":")
                    axes[int(i/4)][col].title.set_text("board {}".format(b))
                    self.pltSamplerStats[b].append(plot)
        # hide unused subplots
        for i in range(len(self.activeBoards),8):
            col = i - int(i/4)*4
            axes[int(i/4)][col].axis('off')
 
        self.canvasSampler = FigureCanvasTkAgg(fig, master=frmSamplerPlots)
        self.canvasSampler.get_tk_widget().grid(row=30, column=i+1, sticky=E+W+N+S)
        #self.canvasSampler.draw()

    def _setupWidgets(self):

        # define styles
        self.style = ttk.Style()
        myfont = font.Font(family="Courier", size=11)
        self.style.configure("My.TButton",font=myfont, foreground="black", relief="sunken", background="white", justify="center", width=6)
        self.style.map( "My.TButton", foreground=[("disabled", "black")], justify=[("disabled", "center")])

        self.style.configure("OK.TButton",font=myfont, foreground="black", relief="sunken", background="lawn green", justify="center", width=6)
        self.style.map( "OK.TButton", foreground=[("disabled", "black")], background=[("disabled", "lawn green")],justify=[("disabled", "center")])

        self.style.configure("WARN.TButton",font=myfont, foreground="black", relief="sunken", background="orange", justify="center", width=6)
        self.style.map( "WARN.TButton", foreground=[("disabled", "black")], background=[("disabled", "orange")],justify=[("disabled", "center")])

        self.style.configure("ERROR.TButton",font=myfont, foreground="black", relief="sunken", background="red", justify="center", width=6)
        self.style.map( "ERROR.TButton", foreground=[("disabled", "black")], background=[("disabled", "red")],justify=[("disabled", "center")])

        # menubar setup
        menubar = Menu()
        optionmenu = Menu(menubar, tearoff=0)
        menubar.add_command(label="Exit", command=self.root.quit)
        self.root.config(menu=menubar)


        Label(self.root, textvariable=self.messageVars["time"]).grid(row=1, column=0)
        frmIf = LabelFrame(self.root, text="IF Power")
        frmIf.grid(row=10,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSynth = LabelFrame(self.root, text="Downconversion")
        frmSynth.grid(row=20,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSampler = LabelFrame(self.root, text="Sampler")
        frmSampler.grid(row=30,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmBBC = LabelFrame(self.root, text="BBCs")
        frmBBC.grid(row=40,column=0, sticky=E+W+N+S, padx=2,pady=2)

         
        self.messageComp = {}

        # frmIf setup
        Label(frmIf, text="counts").grid(row=2,column=0, sticky=W)
        Label(frmIf, text="target").grid(row=3,column=0, sticky=W)
        Label(frmIf, text="mode").grid(row=4,column=0, sticky=W)
        Label(frmIf, text="attenuation").grid(row=5,column=0, sticky=W)
        Label(frmSynth, text="enabled").grid(row=2,column=0, sticky=W)
        Label(frmSynth, text="locked").grid(row=3,column=0, sticky=W)
        Label(frmSynth, text="frequency").grid(row=4,column=0, sticky=W)

        # frmSampler setup
        Label(frmSampler, text="sampler 0 state").grid(row=2,column=0, sticky=W)
        Label(frmSampler, text="sampler 1 state").grid(row=3,column=0, sticky=W)
        Label(frmSampler, text="sampler 2 state").grid(row=4,column=0, sticky=W)
        Label(frmSampler, text="sampler 3 state").grid(row=5,column=0, sticky=W)

        #frmNotebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=10, column=10, rowspan=100, sticky=E+W+S+N)

        self._setupTabIF()
        #self._setupTabSampler()

        #frmIF
        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                print (i, self.activeBoards[i])
                continue
            b = i+1

            Label(frmIf, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSynth, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSampler, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            #frmIf.columnconfigure(i,minsize=100)
            #frmSynth.columnconfigure(i,minsize=100)
            #frmSampler.columnconfigure(i,minsize=100)

            #frmIf
            print (b, self.messageVars["if_{}_count".format(b)].get())
            self.messageComp["if_{}_count".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_count".format(b)])
            self.messageComp["if_{}_target".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_target".format(b)])
            self.messageComp["if_{}_mode".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_mode".format(b)])
            self.messageComp["if_{}_attenuation".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_attenuation".format(b)])

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
            #for s in range(4):
            #    self.messageComp["if_{}_sampler{}_state".format(b,s)] = ttk.Button(frmSampler, style="OK.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_sampler{}_state".format(b,s)])
            #    self.messageComp["if_{}_sampler{}_state".format(b,s)].grid(row=2+s, column=i+1, sticky=E+W)
#
    def updateBoardInfo(self, message):

        pass
        

def parseCommandLine():

    parser = argparse.ArgumentParser("Check dbbc3 multicast")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
#    parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("-s", "--simulate", action='store_true', required=False, help="Produce simulated IF counts.")
#    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")


    return(parser.parse_args())

args = parseCommandLine()

mainDlg = MainWindow(None)


