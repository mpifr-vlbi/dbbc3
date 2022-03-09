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


class PlotBstat ():

    def __init__(self, ax, messageVar):
        self.ax = ax
        self.messageVar = messageVar
#        self.data = [0,0,0,0]
        self.ax.set_ylim(0, 40)
        self.bar = self.ax.bar([0,1,2,3], [0,0,0,0], alpha=0.4, color="green", edgecolor="black", zorder=-1)
        self.ax.axhline(y=16,  color="black", linestyle="--", linewidth=0.5, zorder=10)
        self.ax.axhline(y=34,  color="black", linestyle="--", linewidth=0.5, zorder=10)
        self.ax.get_xaxis().set_ticks([])
        self.ax.get_yaxis().set_ticks([])
        self.ax.text(1.5, 16, "16%", fontsize='x-small', zorder=10)
        self.ax.text(1.5, 34, "34%", fontsize='x-small', zorder=10)

    def update(self, y):

        error = False
        y = [float(i) for i in self.messageVar.get()[1:-1].split(",")]
        print ("update", y)
#        self.data = y

        if abs(y[0]-16) > 3.2 or abs(y[3]-16) > 3.2:
            error = True

        for i in range(len(y)):
            self.bar[i].set_height(y[i])
            self.bar[i].set_zorder(-1)
            if error:
                self.bar[i].set(color="red")

#        self.ax.axhline(y=16,  color="black", linestyle="--", linewidth=0.5, zorder=10)
#        self.ax.axhline(y=34,  color="black", linestyle="--", linewidth=0.5, zorder=10)
#        self.ax.text(1.5, 16, "16%", fontsize='x-small', zorder=10)
#        self.ax.text(1.5, 34, "34%", fontsize='x-small', zorder=10)

        return (self.bar)


class PlotCounts ():
    def __init__(self, ax, activeBoards, maxX=100):
        self.ax = ax
        self.maxt = maxX
        self.activeBoards = activeBoards

        self.maxY = 0
        self.minY = 100000

        self.lines = []
        self.ydata = []

        count = 0
        colors = ['red','green', 'orange','blue', 'pink', 'violet', 'brown', 'gray']
        for board in self.activeBoards:
            if board:
                self.ydata.append(collections.deque([], maxlen=self.maxt))
                print (count)
                line = Line2D([],  [], color=colors[count], label="board {}".format(count+1))
                self.ax.add_line(line)
                self.lines.append(line)

            count +=1
        self.ax.legend(handles=self.lines, fontsize='x-small', loc=4, frameon=True)
        self.ax.set_ylim(30000, 35000)
        self.ax.set_xlim(-1*maxX, 0)


    def update(self, y):

        margin = 1000
        yminVals = []
        ymaxVals = []
        
        resize=False
        for i in range(len(self.lines)):
            self.ydata[i].append(y[i])
            self.tdata = list(range(-1*len(self.ydata[i])+1,1,1))
            self.lines[i].set_data(self.tdata, list(self.ydata[i]))

            ymaxVals.append( max(self.ydata[i]))
            if y[i] != 0:
                yminVals.append( min(self.ydata[i]))


        ymax = max (ymaxVals)
        ymin = min (yminVals)
#        print (ymin, ymax, yminVals, ymaxVals, self.minY, self.maxY)

        if ymax > self.maxY or ymax + 2*margin <  self.maxY:
            self.maxY = ymax + margin
            resize = True
        if ymin < self.minY or ymin - 2*margin > self.minY:
            self.minY = ymin - margin
            resize = True
        if resize:
            self.ax.set_ylim(self.minY, self.maxY)
            self.ax.figure.canvas.resize_event()
            

        return self.lines


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

   #     print (res)

        q.put(res)

class MainWindow():

    def __init__(self, parent=None):

            self.root = Tk()
            self.root.title ("dbbcmon")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            self.messageVars={}
            self.messageComp = {}

            # default width of output text widget
            self.txtWidth = 6

            # get the Multicast instance matching the currently loaded firmware
            mcFactory = DBBC3MulticastFactory()
            self.mc = mcFactory.create()

            # start multicast polling in its own thread
            self.q = queue.Queue(maxsize=1)
            mcThread = threading.Thread(target=thread_mcPoll, args=("mc", self.mc,  self.q), daemon = True)
            mcThread.start()
            
            # obtain initial mc message
            self.lastMessage = self.q.get(block=True)
            self._initVars(self.lastMessage)

            # determine the currently activated boards
            self.setActiveBoards()

            self.mode = self.messageVars["mode"].get()
            self.majorVersion = int(self.messageVars["majorVersion"].get())

            self._setupWidgets()

            # start the main widget updater loop (repeats every 1s)
            self.updateMessage()


            self.root.mainloop()
            
    def on_closing(self):
            self.root.quit()
            self.root.destroy()

    def setActiveBoards(self):

         # check if active / present boards are broadcasted over multicast
        if "boardPresent" in self.lastMessage.keys():
            present = np.array(list(self.lastMessage["boardPresent"]))
        else:
            present = np.array([1,1,1,1,1,1,1,1], dtype=bool)

        self.activeBoards =  np.array([0,0,0,0,0,0,0,0], dtype=bool)

        #present = np.array([1,1,1,1,1,1,1,1], dtype=bool)
        if (args.boards):
            for board in list(args.boards):
                if present[int(board)]:
                    self.activeBoards[int(board)] = True
        else:
            if "boardActive" in self.lastMessage.keys():
                self.activeBoards = np.array(list(self.lastMessage["boardActive"]), dtype=bool)
            else:
                self.activeBoards = present

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


    def updateMessage(self):

        # obtain new message from multicast reader thread
        self.lastMessage = self.q.get(block=True)

        # serialize the mc message and auto-populate StringVars
        self._initVars(self.lastMessage)

        # update the state of the various widgets
        self._setWidgetStates()

        self.root.after(1000, self.updateMessage)
    
    def _setWidgetStates(self):

        for board in range(8):

            if not self.activeBoards[board]:
                continue
            board += 1

            # adjust width of widget if content is longer than default width
            for k in self.messageVars.keys():
                    
                if len(self.messageVars[k].get()) > self.txtWidth:
                    #try:
                        if k in self.messageComp.keys():
                            print (k)
                            print (self.messageComp.keys())
                            self.messageComp[k].configure(width=len(self.messageVars[k].get()))
                    #except:
                    #    print ("error setting width for: ", k)
                    #    pass
                    
            # IF dashboard
            key = "if_{}_mode".format(board)
            if self.messageVars[key].get() == 'agc':
                self.messageComp[key].configure(style="OK.TButton")
            else:
                self.messageComp[key].configure(style="WARN.TButton")

            key = "if_{}_attenuation".format(board)
            att = int(self.messageVars[key].get())
            if att > 20 and att < 41:
                self.messageComp[key].configure(style="OK.TButton")
            else:
                self.messageComp[key].configure(style="WARN.TButton")

            key = "if_{}_count".format(board)
            att = self.messageVars[key].get()
            if abs(int(self.messageVars[key].get()) - int(self.messageVars["if_{}_target".format(board)].get())) < 1000:
                self.messageComp[key].configure(style="OK.TButton")
            else:
                self.messageComp[key].configure(style="WARN.TButton")

            # DC dashboard
            if self.messageVars["if_{}_synth_status".format(board)].get() ==  "on":
                # check lock state for boards with enabled DC
                key = "if_{}_synth_lock".format(board)
                if self.messageVars[key].get() == 'locked':
                    self.messageComp[key].configure(style="OK.TButton")
                else:
                    self.messageComp[key].configure(style="ERROR.TButton")


            # sampler dashboard
            for s in range(4):
                key = "if_{}_sampler{}_state".format(board, s)
                state = self.messageVars[key].get()
            #  # print (state)
                if state == 'OK':
                    self.messageComp[key].configure(style="OK.TButton")
                elif state == '--':
                    self.messageComp[key].configure(style="WARN.TButton")
                elif state == 'Error':
                    self.messageComp[key].configure(style="ERROR.TButton")
                else:
                    self.messageComp[key].configure(style="My.TButton")

        
    def _setStringVar(self, key, value):

        if not key in self.messageVars.keys():
            self.messageVars[key] = StringVar(value=str(value))
        else:
            self.messageVars[key].set(str(value))

    def _getSamplerState(self, board):
        '''
        Returns the state of all sampler of the given board.
        The sampler state is evaluated based on the
        gain, offset and delay.

        Possible states:
            OK:     all good
            --:     no IF power
            Error:  in case of error 

        Returns:
            list (str): 4 element list with a state identifier for the 4 samplers
        '''

        ret = ["OK", "OK", "OK", "OK"]


        # delay correlation
        corrs = list(self.messageVars["if_{}_delayCorr".format(board)].get()[1:-1].split(","))
        for corr in corrs: 
            if int(corr) < 160000000:
                return (["Error", "Error", "Error", "Error"])

        meanPower = 0
        power = []
        for s in range(4):
         #   key ="if_{}_sampler{}_statsFrac".format(board,s)
         #   stats = list(map(float, self.messageVars[key].get()[1:-1].split(",")))
         #   if abs(stats[0] +stats[1] -50.0) > 5.0:
         #       ret[s] = "warning"
         #   elif abs(stats[0] +stats[1] -50.0) > 10.0:
         #       ret[s] = "error"

            # power
            key ="if_{}_sampler{}_power".format(board,s)
            power.append(float(self.messageVars[key].get()))
            meanPower += float(self.messageVars[key].get()) / 4
            #print (self.messageVars[key].get(), meanPower)


        if meanPower == 0.0:
            return (["--", "--","--","--"])

        for s in range(4):
            if abs(1 -  power[s]/ meanPower) > 0.02:
                ret[s] = "Error"


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

            # check sampler states
            state = self._getSamplerState(board)
            #print (board, state)
            for s in range(4):
                self._setStringVar("if_{}_sampler{}_state".format(board,s), state[s])

            # process delay correlation (sampler phase)
            key = "if_{}_delayCorr".format(board)
            corrs = list(self.messageVars["if_{}_delayCorr".format(board)].get()[1:-1].split(","))
            self._setStringVar("if_{}_delayCorr_01".format(board,s), corrs[0].strip())
            self._setStringVar("if_{}_delayCorr_12".format(board,s), corrs[1].strip())
            self._setStringVar("if_{}_delayCorr_23".format(board,s), corrs[2].strip())
            

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

        
#
    def test(self):

        print ("update")
        yield [1,2,3,4]
    def getBstats(self, board, filter ):
#
       # stats = self.messageVars["if_{}_filter{}_statsFrac".format(board, filter)].get()[1:-1].split(",")
        stats = [float(i) for i in self.messageVars["if_{}_filter{}_statsFrac".format(board, filter)].get()[1:-1].split(",")]
        print (stats)
        yield  stats

    def getCounts(self):
        '''
        Generator method to supply the FuncAnimation with the latest dbbc if counts
        '''

        counts = []
        
        for i in range(1, 9):
            if (self.activeBoards[i-1]):
                counts.append(float(self.messageVars["if_{}_count".format(i)].get()))
        
        print (counts)
        yield counts

    def _setupTabFilter(self):

        tabFilter = ttk.Frame(self.notebook, height=280)
        tabFilter.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabFilter, text='Filter Details')

        frmPower = LabelFrame(tabFilter, text="Power")
        frmPower.grid(row=0,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmPower, text="filter 1").grid(row=2,column=0, sticky=E+W, padx=5)
        Label(frmPower, text="filter 2").grid(row=3,column=0, sticky=E+W, padx=5)

        frmPlots = LabelFrame(tabFilter, text="2-bit statistics")
        frmPlots.grid(row=10,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmPlots, text="filter 1").grid(row=2,column=0, sticky=E+W, padx=5)
        Label(frmPlots, text="filter 2").grid(row=3,column=0, sticky=E+W, padx=5)

        
        #ax.set_title ("Counts", fontsize=16)
        #ax.set_ylabel("counts", fontsize=11)
        #ax.set_xlabel("time[s]", fontsize=11)
        #ax.set_ylim([30000,40000])
        #ax.set_xlim([-100,0])
        #ax.grid(True)

        pltStats = []
        self.aniBstats = []
        count = 0
        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1

            Label(frmPower, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmPlots, text=str(b)).grid(row=1,column=i+1, sticky=E+W)

            for f in range(1,3):
                key ="if_{}_filter{}_power".format(b, f)
                #print (self.messageVars[key].get())
                self.messageComp[key] = ttk.Button(frmPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key]).grid(row=f+1, column=i+1, sticky=E+W)

                fig, ax = plt.subplots()
                fig.set_size_inches(0.8,0.8)
                pltStats.append (PlotBstat(ax, self.messageVars["if_{}_filter{}_statsFrac".format(b, f)]))
                self.aniBstats.append( animate.FuncAnimation(fig, pltStats[count].update, interval=2000, blit=True))
                canvasBstats = FigureCanvasTkAgg(fig, master=frmPlots)
                canvasBstats.get_tk_widget().grid(row=1+f, column=i+1, sticky=E+W+S+N)
                count += 1
        #self.canvasBstats.draw()
            
    def _setupTabIF(self):

        tabIF = ttk.Frame(self.notebook, height=280)
        tabIF.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabIF, text='Total Power') 

        fig, ax = plt.subplots()
        ax.set_title ("Counts", fontsize=16)
        ax.set_ylabel("counts", fontsize=11)
        ax.set_xlabel("time[s]", fontsize=11)
        ax.set_ylim([30000,40000])
        ax.set_xlim([-100,0])
        ax.grid(True)

        pltCounts = PlotCounts(ax, self.activeBoards, 30)
        self.aniCounts = animate.FuncAnimation(fig, pltCounts.update, self.getCounts, interval=2000, blit=True)
        self.canvasCounts = FigureCanvasTkAgg(fig, master=tabIF)
        self.canvasCounts.get_tk_widget().pack()
        self.canvasCounts.draw()

    def _setupTabSampler(self):

        tabSampler = ttk.Frame(self.notebook, height=280)
        tabSampler.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabSampler, text='Sampler Details') 

        # tabSampler
        frmSamplerPower = LabelFrame(tabSampler, text="Sampler power")
        frmSamplerPower.grid(row=0,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmSamplerPower, text="samp. 0").grid(row=2,column=0, sticky=E+W, padx=5)
        Label(frmSamplerPower, text="samp. 1").grid(row=3,column=0, sticky=E+W, padx=5)
        Label(frmSamplerPower, text="samp. 2").grid(row=4,column=0, sticky=E+W, padx=5)
        Label(frmSamplerPower, text="samp. 3").grid(row=5,column=0, sticky=E+W, padx=5)

        frmSamplerOffset = LabelFrame(tabSampler, text="Sampler offset")
        frmSamplerOffset.grid(row=10,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmSamplerOffset, text="samp. 0").grid(row=2,column=0, sticky=E+W, padx=5)
        Label(frmSamplerOffset, text="samp. 1").grid(row=3,column=0, sticky=E+W, padx=5)
        Label(frmSamplerOffset, text="samp. 2").grid(row=4,column=0, sticky=E+W, padx=5)
        Label(frmSamplerOffset, text="samp. 3").grid(row=5,column=0, sticky=E+W, padx=5)

        frmSamplerDelay = LabelFrame(tabSampler, text="Sampler phase")
        frmSamplerDelay.grid(row=20,column=0,sticky=E+W+S+N, padx=10, pady=10)
        Label(frmSamplerDelay, text="delay 0/1").grid(row=2,column=0, sticky=E+W, padx=5)
        Label(frmSamplerDelay, text="delay 1/2").grid(row=3,column=0, sticky=E+W, padx=5)
        Label(frmSamplerDelay, text="delay 2/3").grid(row=4,column=0, sticky=E+W, padx=5)

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                #print (i, self.activeBoards[i])
                continue
            b = i+1
            

            Label(frmSamplerPower, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSamplerOffset, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSamplerDelay, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            #Label(frmSampler, text=str(b)).grid(row=1,column=i+1, sticky=E+W)

            for sampler in range(4):
                key ="if_{}_sampler{}_power".format(b,sampler)
                self.messageComp[key] = ttk.Button(frmSamplerPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key]).grid(row=sampler+2, column=i+1, sticky=E+W)
            
            corrs = ["01","12","23"]
            row = 2
            for corr in corrs:
                key = "if_{}_delayCorr_{}".format(b, corr)
                self.messageComp[key] = ttk.Button(frmSamplerDelay, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key]).grid(row=row, column=i+1, sticky=E+W )
                row +=1
                

    def _setupWidgets(self):
        '''
        Define the widget layout common to all DBBC3 multicast modes.
        '''


        # define styles
        self.style = ttk.Style()
        myfont = font.Font(family="Arial", size=11)
        self.style.configure("My.TButton",font=myfont, foreground="black", relief="ridge", background="white", justify="center", width=self.txtWidth)
        self.style.map( "My.TButton", foreground=[("disabled", "black")], justify=[("disabled", "center")])

        self.style.configure("OK.TButton",font=myfont, foreground="black", relief="ridge", background="lime green", justify="center", width=self.txtWidth)
        self.style.map( "OK.TButton", foreground=[("disabled", "black")], background=[("disabled", "lime green")],justify=[("disabled", "center")])

        self.style.configure("WARN.TButton",font=myfont, foreground="black", relief="sunken", background="orange", justify="center", width=self.txtWidth)
        self.style.map( "WARN.TButton", foreground=[("disabled", "black")], background=[("disabled", "orange")],justify=[("disabled", "center")])

        self.style.configure("ERROR.TButton",font=myfont, foreground="black", relief="sunken", background="red", justify="center", width=self.txtWidth)
        self.style.map( "ERROR.TButton", foreground=[("disabled", "black")], background=[("disabled", "red")],justify=[("disabled", "center")])

        # menubar setup
        menubar = Menu()
        optionmenu = Menu(menubar, tearoff=0)
        menubar.add_command(label="Exit", command=self.root.quit)
        self.root.config(menu=menubar)

        #Notebook tab container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=10, column=10, rowspan=100, sticky=E+W+S+N)

        # define the frames
        frmInfo = LabelFrame(self.root, text="DBBC3")
        frmInfo.grid(row=5,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmTime = LabelFrame(self.root, text="Last Multicast")
        frmTime.grid(row=5,column=10, sticky=E+W+N+S, padx=2,pady=2)

        frmIf = LabelFrame(self.root, text="IF Power")
        frmIf.grid(row=10,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSynth = LabelFrame(self.root, text="Downconversion")
        frmSynth.grid(row=20,column=0, sticky=E+W+N+S, padx=2,pady=2)


        frmSampler = LabelFrame(self.root, text="Sampler")
        frmSampler.grid(row=30,column=0, sticky=E+W+N+S, padx=2,pady=2)

        # frmGeneral setup
        Label(frmInfo, text="mode").grid(row=2,column=0, sticky=W, padx=2)
        Label(frmInfo, text="FW Version").grid(row=3,column=0, sticky=W, padx=2)
        self.messageComp["mode"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["mode"]).grid(row=2,column=10, columnspan=2, sticky='ew' )
        self.messageComp["majorVersion"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["majorVersion"]).grid(row=3,column=10, sticky='ew')
        self.messageComp["minorVersion"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["minorVersion"]).grid(row=3,column=11, sticky='ew')

        # frmTime setup
        self.messageComp["time"] = Label(frmTime, textvariable=self.messageVars["time"]).grid(row=4,column=10, columnspan=10, sticky=E+W+N+S, padx=2,pady=2)

        # frmIf setup
        Label(frmIf, text="counts").grid(row=2,column=0, sticky=W)
        Label(frmIf, text="target").grid(row=3,column=0, sticky=W)
        Label(frmIf, text="mode").grid(row=4,column=0, sticky=W)
        Label(frmIf, text="attenuation").grid(row=5,column=0, sticky=W)
        Label(frmSynth, text="enabled").grid(row=2,column=0, sticky=W)
        Label(frmSynth, text="synth").grid(row=3,column=0, sticky=W)
        Label(frmSynth, text="frequency").grid(row=4,column=0, sticky=W)

        # frmSampler setup
        Label(frmSampler, text="s0 state").grid(row=2,column=0, sticky=W)
        Label(frmSampler, text="s1 state").grid(row=3,column=0, sticky=W)
        Label(frmSampler, text="s2 state").grid(row=4,column=0, sticky=W)
        Label(frmSampler, text="s3 state").grid(row=5,column=0, sticky=W)


        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                #print (i, self.activeBoards[i])
                continue
            b = i+1

            Label(frmIf, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSynth, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            Label(frmSampler, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            #frmIf.columnconfigure(i,minsize=100)
            #frmSynth.columnconfigure(i,minsize=100)
            #frmSampler.columnconfigure(i,minsize=100)

            #frmIf
            self.messageComp["if_{}_count".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_count".format(b)])
            self.messageComp["if_{}_target".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_target".format(b)])
            self.messageComp["if_{}_mode".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_mode".format(b)])
            self.messageComp["if_{}_attenuation".format(b)] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_attenuation".format(b)])

            self.messageComp["if_{}_count".format(b)].grid(row=2,column=i+1, sticky=E+W)
            self.messageComp["if_{}_target".format(b)].grid(row=3,column=i+1, sticky=E+W)
            self.messageComp["if_{}_mode".format(b)].grid(row=4,column=i+1, sticky=E+W)
            self.messageComp["if_{}_attenuation".format(b)].grid(row=5,column=i+1, sticky=E+W)

            # frmSynth
            self.messageComp["if_{}_synth_status".format(b)] = ttk.Button(frmSynth, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_synth_status".format(b)])
            self.messageComp["if_{}_synth_lock".format(b)] = ttk.Button(frmSynth, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_synth_lock".format(b)])
            self.messageComp["if_{}_synth_frequency".format(b)] = ttk.Button(frmSynth, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_synth_frequency".format(b)])

            self.messageComp["if_{}_synth_status".format(b)].grid(row=2,column=i+1,sticky=E+W)
            self.messageComp["if_{}_synth_lock".format(b)].grid(row=3,column=i+1,sticky=E+W)
            self.messageComp["if_{}_synth_frequency".format(b)].grid(row=4,column=i+1,sticky=E+W)

            # frmSampler
            for s in range(4):
                self.messageComp["if_{}_sampler{}_state".format(b,s)] = ttk.Button(frmSampler, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_sampler{}_state".format(b,s)])
                self.messageComp["if_{}_sampler{}_state".format(b,s)].grid(row=2+s, column=i+1, sticky=E+W)

        self._setupTabIF()
        self._setupTabSampler()

        if self.mode == "OCT_D" and self.majorVersion >= 120:
            self._setupTabFilter()
        

def parseCommandLine():

    parser = argparse.ArgumentParser("a graphical monitoring client for the DBBC3")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    parser.add_argument("-b", "--boards", dest='boards', type=lambda s: list(map(str, s.split(","))), help="A comma separated list of core boards to be used for setup and validation. Can be specified as 0,1 or A,B,.. (default: use all activated core boards)")
    parser.add_argument("-t", "--timeout", required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("-s", "--simulate", action='store_true', required=False, help="Produce simulated IF counts.")

    return(parser.parse_args())


args = parseCommandLine()

mainDlg = MainWindow(None)


