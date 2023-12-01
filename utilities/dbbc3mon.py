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

        if abs(y[0]-16) > 3.2 or abs(y[3]-16) > 3.2:
            error = True
#        print (y[0], y[1], y[2], y[3], error)

        for i in range(len(y)):
            self.bar[i].set_height(y[i])
            self.bar[i].set_zorder(-1)
            if error:
                self.bar[i].set(color="red")
            else:
                self.bar[i].set(color="green")

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
                #print (count)
                line = Line2D([],  [], color=colors[count], label="board {}".format(count+1))
                self.ax.add_line(line)
                self.lines.append(line)

            count +=1
        self.ax.legend(handles=self.lines, fontsize='x-small', loc=4, frameon=True)
        self.ax.set_ylim(30000, 35000)
        self.ax.set_xlim(-1*maxX, 0)


    def update(self, y):

#        margin = 1000
        yminVals = []
        ymaxVals = []
        
        resize=False
        for i in range(len(self.lines)):
            #print (self.lines[i])
            #print (self.ydata[i])
            self.ydata[i].append(y[i])
            self.tdata = list(range(-1*len(self.ydata[i])+1,1,1))
            self.lines[i].set_data(self.tdata, list(self.ydata[i]))

            ymaxVals.append( max(self.ydata[i]))
            if y[i] != 0:
                yminVals.append( min(self.ydata[i]))


        ymax = max (ymaxVals)
        ymin = min (yminVals)

        #margin = max([ymax*0.2, 1000])
        margin = 1000
        #print (ymin, ymax, yminVals, ymaxVals, self.minY, self.maxY)

        if ymax >= self.maxY or ymax + 2*margin <  self.maxY:
            self.maxY = ymax + margin
            resize = True
        if ymin <= self.minY or ymin - 2*margin > self.minY:
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
        #print ("polling ", datetime.now())
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
            self.root.title ("dbbc3mon")
            self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

            style = ttk.Style(self.root)
            print(style.lookup('Label.label', 'background'))
            #self.root.tk_setPalette(background='#F0F0F0', foreground='black', activeBackground='black', activeForeground="blue")
            self.root.tk_setPalette(background='#d9d9d9', foreground='black')

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

            # determine mode and version
            self.mode = self.lastMessage["mode"]
            self.majorVersion = int(self.lastMessage["majorVersion"])

            self._setDisplayOptions()

            self._initVars(self.lastMessage)

            # determine the currently activated boards
            self.setActiveBoards()

#            self.mode = self.messageVars["mode"].get()
#            self.majorVersion = int(self.messageVars["majorVersion"].get())



            self.hideBBCVar = IntVar()
            self.hideBBCVar.set(1)
            self._setupWidgets()

            # start the main widget updater loop (repeats every 1s)
            self.updateMessage()


            self.root.mainloop()
            
    def on_closing(self):
        self.root.quit()
        self.root.destroy()

    def _setDisplayOptions(self):

        self.displayOptions = {
            'samplerOffset' : False,
            'tabBBC' : False,
            'tabFilter' : False,
            'samplerBstate' : False,
            'samplerBstateOffset' : False
            }

        if self.mode == "OCT_D":
            self.displayOptions['samplerOffset'] = True
            if self.majorVersion >= 120:
                self.displayOptions['tabFilter'] = True
        elif self.mode == "DDC_U":
            self.displayOptions['tabBBC'] = True
            self.displayOptions['samplerBstateOffset'] = True
        
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
        self._setDashboardStates()
        self._setTabSamplerStates()

        self.root.after(1000, self.updateMessage)
    
    def _setTabSamplerStates(self):

        for board in range(8):
            if not self.activeBoards[board]:
                continue
            board += 1
        
            # delta power
            self._setSamplerPowerState(board)
                
            # delay sync
            colType = "My.TButton"
            states = self._getSamplerDelayState(board)

            key ="if_{}_sync".format(board)
            if ("Error" in states):
                self.messageComp[key].configure(style="ERROR.TButton")
            elif "OK" in states:
                self.messageComp[key].configure(style="OK.TButton")
            else:
                self.messageComp[key].configure(style="OFF.TButton")
                colType = "OFF.TButton"

            corrs = ["01","12","23"]
            for i in range(len(corrs)):
                key = "if_{}_delayCorr_{}".format(board, corrs[i])
                self.messageComp[key].configure(style=colType)

            # offset asymmetry
            if "if_{}_sampler0_asymmetry".format(board) in self.messageComp.keys():
                self._setSamplerOffsetAsymmetryState(board)


    def _setDashboardStates(self):

        for board in range(8):

            if not self.activeBoards[board]:
                continue
            board += 1

            # adjust width of widget if content is longer than default width
            #for k in self.messageVars.keys():
            #        
            #    if len(self.messageVars[k].get()) > self.txtWidth:
            #        #try:
            #            if self.messageComp[k]:
            #                print (k)
            #                print (self.messageComp.keys())
            #                self.messageComp[k].configure(width=len(self.messageVars[k].get()))
            #        #except:
            #        #    print ("error setting width for: ", k)
            #        #    pass
                    
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
      #      for s in range(4):
      #          key = "if_{}_sampler{}_state".format(board, s)
      #          state = self.messageVars[key].get()
      #      #  # print (state)
      #          if state == 'OK':
      #              self.messageComp[key].configure(style="OK.TButton")
      #          elif state == '--':
      #              self.messageComp[key].configure(style="WARN.TButton")
      #          elif state == 'Error':
      #              self.messageComp[key].configure(style="ERROR.TButton")
      #          else:
      #              self.messageComp[key].configure(style="My.TButton")

        
    def _setStringVar(self, key, value):

        if not key in self.messageVars.keys():
            self.messageVars[key] = StringVar(value=str(value))
        else:
            self.messageVars[key].set(str(value))


    def _getSamplerOffsetAsymmetry(self, board):

        if not "if_{}_sampler0_statsFrac".format(board) in self.messageVars.keys():
            return (None)

        devs = []
        for s in range(4):
            bstats = eval(self.messageVars["if_{}_sampler{}_statsFrac".format(board, s)].get())
            
            if (max(bstats) == 0.0):
                devs.append(0.0)
            else:
                # Asymmetry between low / high states
                devs.append( abs((bstats[0] + bstats[1] - bstats[2] - bstats[3]) / float(bstats[0] + bstats[1] + bstats[2] + bstats[3])))

        return (devs)

        
    def _getSamplerPowerDelta(self, board):
        '''
        Calculates the percentage deviation of the power values of the
        four samplers of the specified board with respect to the mean 
        power over all four samplers.

        Returns:
            list (float): 4 element list containing the percentage deviations
        '''

        meanPower = 0
        power = []
        deltas = []

        for s in range(4):
            # power
            key ="if_{}_sampler{}_power".format(board,s)
            power.append(float(self.messageVars[key].get()))
            meanPower += float(self.messageVars[key].get()) / 4

        for s in range(4):
            if (meanPower == 0.0):
                deltas.append(0.0)
            else:
                deltas.append( abs(1 -  power[s]/ meanPower)*100)

        return(deltas)

    def _setSamplerOffsetAsymmetryState(self, board):

        state = []
        for s in range(4):
            key = "if_{}_sampler{}_asymmetry".format(board,s)
            val = float(self.messageVars[key].get())
            if val > 10.0:
                self.messageComp[key].configure(style="ERROR.TButton")
            elif val > 5.0:
                self.messageComp[key].configure(style="WARN.TButton")
            elif val == 0.0:
                self.messageComp[key].configure(style="OFF.TButton")
            else:
                self.messageComp[key].configure(style="OK.TButton")
                
    

        
    def _setSamplerPowerState(self, board):
        '''
        Sets the state of the sampler powers of the specified board

        The state is evaluated based on the deviation of the power values of
        all four samplers with respect to the mean power value.

        '''

        deltas = self._getSamplerPowerDelta (board)

        key ="if_{}_sampler_delta_power".format(board) 
        
        # checks that sampler power does not deviate from the mean by more than 2%
#        print (board, power, meanPower)
        maxDelta = max(deltas)

        colType = "My.TButton"
        if maxDelta > 20.0:
            self.messageComp[key].configure(style="ERROR.TButton")
        elif (maxDelta > 5.0):
            self.messageComp[key].configure(style="WARN.TButton")
        elif (maxDelta == 0.0):
            colType = "OFF.TButton"
            self.messageComp[key].configure(style="OFF.TButton")
        else:
            self.messageComp[key].configure(style="OK.TButton")

        for i in range(4):
            key = "if_{}_sampler{}_power".format(board, i)
            self.messageComp[key].configure(style=colType)
        

    def _getSamplerDelayState(self, board):
        
        ret = ["OK","OK","OK"]


        # delay correlation checks if board is in sync
        corrs = list(map(int, self.messageVars["if_{}_delayCorr".format(board)].get()[1:-1].split(",")))
        if max(corrs) ==  0:
            return(["--", "--", "--", "--"])

        for i in range(len(corrs)):
            if int(corrs[i]) < 160000000:
                ret[i] = "Error"

        return(ret)
                

 #   def _getSamplerState(self, board):
 #       '''
 #       Returns the state of all sampler of the given board.
 #       The sampler state is evaluated based on the gain, offset and delay.
#
#        
#
#        Possible states:
#            OK:     all good
#            --:     no IF power
#            Error:  in case of error 
#
#        Returns:
#            list (str): 4 element list with a state identifier for the 4 samplers
#        '''
#
#        ret = ["OK", "OK", "OK", "OK"]
#
#
#        # delay correlation checks if board is in sync
#        corrs = list(map(int, self.messageVars["if_{}_delayCorr".format(board)].get()[1:-1].split(",")))
#        if max(corrs) > 0:
#            for corr in corrs: 
#                if int(corr) < 160000000:
#                    # if board not in sync return Error for all 4 samplers 
#                    return (["Error", "Error", "Error", "Error"])
#        else:
#            ret = ["--", "--", "--", "--"]
#
#        meanPower = 0
#        power = []
#        for s in range(4):
#         #   key ="if_{}_sampler{}_statsFrac".format(board,s)
#         #   stats = list(map(float, self.messageVars[key].get()[1:-1].split(",")))
#         #   if abs(stats[0] +stats[1] -50.0) > 5.0:
#         #       ret[s] = "warning"
#         #   elif abs(stats[0] +stats[1] -50.0) > 10.0:
#         #       ret[s] = "error"
#
#            # power
#            key ="if_{}_sampler{}_power".format(board,s)
#            power.append(float(self.messageVars[key].get()))
#            meanPower += float(self.messageVars[key].get()) / 4
#            #print (self.messageVars[key].get(), meanPower)
#
#
#        # checks that sampler power does not deviate from the mean by more than 2%
##        print (board, power, meanPower)
#        if meanPower == 0.0:
#            return (["--", "--","--","--"])
#
#        for s in range(4):
#            if abs(1 -  power[s]/ meanPower) > 0.02:
#                ret[s] = "Error"
#
#        return ret
#
    def _initVars(self, message):

        self.samplerStates = [{},{},{},{}]

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
            
            # filter powers (OCT only)
            if "if_1_filter1_power" in self.messageVars.keys():
                #convert to scientific notation
                val = int(self.messageVars["if_{}_filter1_power".format(board)].get())
                self._setStringVar("if_{}_filter1_power".format(board), '{:.3e}'.format(val))
            if "if_1_filter2_power" in self.messageVars.keys():
                #convert to scientific notation
                val = int(self.messageVars["if_{}_filter2_power".format(board)].get())
                self._setStringVar("if_{}_filter2_power".format(board), '{:.3e}'.format(val))

            # sampler specifics
            #state = self._getSamplerState(board)
            for s in range(4):
                # sampler state summary
                #self._setStringVar("if_{}_sampler{}_state".format(board,s), state[s])

                # convert sampler powers into scientific notation
                val = int(self.messageVars["if_{}_sampler{}_power".format(board,s)].get())
                self._setStringVar("if_{}_sampler{}_power".format(board,s), '{:.3e}'.format(val))

            # process delay correlation (sampler phase)
            key = "if_{}_delayCorr".format(board)
            corrs = list(self.messageVars["if_{}_delayCorr".format(board)].get()[1:-1].split(","))
            self._setStringVar("if_{}_delayCorr_01".format(board,s), corrs[0].strip())
            self._setStringVar("if_{}_delayCorr_12".format(board,s), corrs[1].strip())
            self._setStringVar("if_{}_delayCorr_23".format(board,s), corrs[2].strip())

            # sampler delay sync
            states = self._getSamplerDelayState(board)
            if ("Error" in states):
                self._setStringVar("if_{}_sync".format(board), "Error")
            elif ("OK" in states):
                self._setStringVar("if_{}_sync".format(board), "OK")
            else:
                self._setStringVar("if_{}_sync".format(board), "--")
                # this board is inactive (or not present)
                

            # sampler power deviation from mean
            self._setStringVar("if_{}_sampler_delta_power".format(board), "{:.2f}".format((max(self._getSamplerPowerDelta(board)))))

            # sampler offset asymmetry (based on bstates)
            if self.displayOptions['samplerBstateOffset']:
                offsets = self._getSamplerOffsetAsymmetry(board)
                for s in range(4):
                    self._setStringVar("if_{}_sampler{}_asymmetry".format(board,s), "{:.2f}".format(offsets[s]*100))

                # shortened version of bstate fractions
                for s in range(4):
                    bstats = eval(self.messageVars["if_{}_sampler{}_statsFrac".format(board, s)].get())
                    self._setStringVar("if_{}_sampler{}_statsFracShort".format(board, s), ' '.join("{:.1f}".format(i) for i in map(float,bstats))) 
            

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
       #     print (pre + [message])
            yield pre + [message]
        

    def getBstats(self, board, filter ):
#
       # stats = self.messageVars["if_{}_filter{}_statsFrac".format(board, filter)].get()[1:-1].split(",")
        stats = [float(i) for i in self.messageVars["if_{}_filter{}_statsFrac".format(board, filter)].get()[1:-1].split(",")]
        #print (stats)
        yield  stats

    def getCounts(self):
        '''
        Generator method to supply the FuncAnimation with the latest dbbc if counts
        '''

        counts = []
        
        for i in range(1, 9):
            if (self.activeBoards[i-1]):
                counts.append(float(self.messageVars["if_{}_count".format(i)].get()))
        
        #print (counts)
        yield counts

    def _selectCboBoard(self, event):
        self._updateTreeBBC()

    def _updateTreeBBC(self):

        idx = self.cboBoardBBC['values'].index(self.cboBoardBBC.get())

        # populate BBC tree
        for i in self.treeBBC.get_children():
            self.treeBBC.delete(i)

        items = ['frequency',
            'bandwidth',
            'agcStatus', 
            'gainUSB', 
            'gainLSB', 
            'powerOnUSB', 
            'powerOnLSB', 
            'powerOffUSB', 
            'powerOffLSB', 
            #'stat00', 
            #'stat01', 
            #'stat10', 
            #'stat11', 
            'tsysUSB', 
            'tsysLSB', 
            'sefdUSB', 
            'sefdLSB'
            ]

        for set in range(2):
            for bbc in range (1,9):
                
                bbcNum = (idx*8)+bbc+set*64
                id1 = 'bbc_%d' %(bbcNum)
                
                #skip if no multicasxt message exists for BBC (should really not happen)
                try:
                    freq = float(self.messageVars["if_{}_bbc_{}_frequency".format(idx+1, bbcNum)].get())
                except KeyError:
        #            print ("Missing key: ", "if_{}_bbc_{}_frequency".format(idx+1, bbcNum))
                    continue

                # skip unconfigureds BBCs ( if option is set)
                if self.hideBBCVar.get() and freq == 0.0:
                    continue

                self.treeBBC.insert('', 'end', id1, text=id1)
                for item in items:
                    self.treeBBC.insert(id1, 'end', values=[item, self.messageVars["if_{}_bbc_{}_{}".format(idx+1, bbcNum,item)].get()])

    def _setupTabBBC(self):

        tabBBC =  ttk.Frame(self.notebook, height=280)
        tabBBC.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabBBC, text='BBC Details')

        #frmBBC = ttk.LabelFrame(tabBBC, text="")
        #frmBBC.grid(row=1,column=0,sticky=E+W+S+N, padx=10, pady=10)

        self.treeBBC = ttk.Treeview(tabBBC, height=20) 
        self.treeBBC['columns'] = ('item', 'value')
        self.treeBBC.heading("#0", text="bbc")
        self.treeBBC.heading("item", text="item")
        self.treeBBC.heading("value", text="value")
        self.treeBBC.grid(row=10,column=0,columnspan=2,sticky=E+W+S+N, padx=15)

        # add a scrollbar
        scrollbar = ttk.Scrollbar(tabBBC, orient=VERTICAL, command=self.treeBBC.yview)
        self.treeBBC.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=10, column=3, sticky='ns')

        cbValues = []

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1

            cbValues.append( "Board %d" % (b))

        self.cboBoardBBC = ttk.Combobox(tabBBC, values=cbValues)

        ttk.Label(tabBBC, text="Display BBCs for board").grid(row=0,column=0, sticky=W, padx=15, pady=15)
        self.cboBoardBBC.current(0)
        self._updateTreeBBC()
        self.cboBoardBBC.grid(row=0,column=1, pady=10, sticky=W)
        self.cboBoardBBC['state'] = 'readonly'
        self.cboBoardBBC.bind("<<ComboboxSelected>>", self._selectCboBoard)

        chkHideBBC = ttk.Checkbutton(tabBBC, text='Hide unconfigured BBCs', variable=self.hideBBCVar, command=self._updateTreeBBC)
        chkHideBBC.grid(row=2, column=0, padx=15, sticky=W)

    def _setupTabFilter(self):

        # column layout
        labelWidth = 7
        boardColWidth = 11

        tabFilter = ttk.Frame(self.notebook, height=280)
        tabFilter.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabFilter, text='Filter Details')

        frmPower = ttk.LabelFrame(tabFilter, text="Power")
        frmPower.grid(row=0,column=0,sticky=E+W+S+N, padx=10, pady=10)
        ttk.Label(frmPower, text="filter 1", width=labelWidth).grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmPower, text="filter 2").grid(row=3,column=0, sticky=E+W, padx=5)

        frmPlots = ttk.LabelFrame(tabFilter, text="2-bit statistics")
        frmPlots.grid(row=10,column=0,sticky=E+W+S+N, padx=10, pady=10)
        ttk.Label(frmPlots, text="filter 1", width=labelWidth).grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmPlots, text="filter 2").grid(row=3,column=0, sticky=E+W, padx=5)

        
        pltStats = []
        self.aniBstats = []
        count = 0

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1

            ttk.Label(frmPower, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)
            ttk.Label(frmPlots, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)

            fig, axs = plt.subplots(2,1)
            fig.set_size_inches(0.8,1.6)
            for f in range(1,3):
                key ="if_{}_filter{}_power".format(b, f)
                #print (self.messageVars[key].get())
                self.messageComp[key] = ttk.Button(frmPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
                self.messageComp[key].grid(row=f+1, column=i+1, sticky=E+W)

                pltStats.append (PlotBstat(axs[f-1], self.messageVars["if_{}_filter{}_statsFrac".format(b, f)]))
                self.aniBstats.append( animate.FuncAnimation(fig, pltStats[count].update, interval=2000, blit=True))
                count += 1
            fig.tight_layout()
            canvasBstats = FigureCanvasTkAgg(fig, master=frmPlots)
            canvasBstats.get_tk_widget().grid(row=2, rowspan=2, column=i+1, sticky=E+W+S+N)
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

    def _setupFrameOffset(self, parent, row, col, labelWidth, boardWidth):

        frmSamplerOffset = ttk.LabelFrame(parent, text="Sampler offset")
        frmSamplerOffset.grid(row=row,column=col,sticky=E+W+S+N, padx=10, pady=10)
        ttk.Label(frmSamplerOffset, text="offset 0", width=labelWidth).grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="offset 1").grid(row=3,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="offset 2").grid(row=4,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="offset 3").grid(row=5,column=0, sticky=E+W, padx=5)

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1
            ttk.Label(frmSamplerOffset, text=str(b), width=boardWidth).grid(row=1,column=i+1, sticky=E+W)

            for sampler in range(4): 
                key ="if_{}_sampler{}_offset".format(b,sampler)
                self.messageComp[key] = ttk.Button(frmSamplerOffset, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key], width=9)
                self.messageComp[key].grid(row=2+sampler, column=i+1, sticky=E+W)

    def _setupFrameBstateOffset(self, parent, row, col, labelWidth, boardWidth):

        frmSamplerOffset = ttk.LabelFrame(parent, text="Sampler offset")
        frmSamplerOffset.grid(row=row,column=col,sticky=E+W+S+N, padx=10, pady=10)
        ttk.Label(frmSamplerOffset, text="asymm. 0", width=labelWidth).grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="asymm. 1").grid(row=3,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="asymm. 2").grid(row=4,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerOffset, text="asymm. 3").grid(row=5,column=0, sticky=E+W, padx=5)

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1
            ttk.Label(frmSamplerOffset, text=str(b), width=boardWidth).grid(row=0,column=i+1, sticky=E+W)

            for sampler in range(4): 
                key ="if_{}_sampler{}_asymmetry".format(b,sampler)
                self.messageComp[key] = ttk.Button(frmSamplerOffset, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key], width=9)
                self.messageComp[key].grid(row=1+sampler, column=i+1, sticky=E+W)
                

    def _setupTabSampler(self):

        # column layout
        labelWidth = 7
        boardColWidth = 11

        tabSampler = ttk.Frame(self.notebook, height=280)
        tabSampler.grid(row=0,column=0,sticky=E+W+S+N)
        self.notebook.add(tabSampler, text='Sampler Details') 

        # tabSampler
        frmSamplerPower = ttk.LabelFrame(tabSampler, text="Sampler gain")
        frmSamplerPower.grid(row=20,column=0,sticky=E+W+S+N, padx=10, pady=10)
        ttk.Label(frmSamplerPower, width=labelWidth, text="delta %").grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerPower, text="power 0").grid(row=3,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerPower, text="power 1").grid(row=4,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerPower, text="power 2").grid(row=5,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerPower, text="power 3").grid(row=6,column=0, sticky=E+W, padx=5)

        if self.displayOptions['samplerBstateOffset']:
            self._setupFrameBstateOffset(tabSampler, 11, 0, labelWidth, boardColWidth)

        if self.displayOptions['samplerOffset']:
            self._setupFrameOffset(tabSampler, 11, 0, labelWidth, boardColWidth)

        frmSamplerDelay = ttk.LabelFrame(tabSampler, text="Sampler phase")
        frmSamplerDelay.grid(row=0,column=0,sticky=E+W+S+N, padx=10, pady=10)
        #ttk.Label(frmSamplerDelay, text="sync").grid(row=2,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerDelay, text="delay 0/1", width=labelWidth).grid(row=3,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerDelay, text="delay 1/2").grid(row=4,column=0, sticky=E+W, padx=5)
        ttk.Label(frmSamplerDelay, text="delay 2/3").grid(row=5,column=0, sticky=E+W, padx=5)

        if (self.displayOptions['samplerBstate']):
            frmBstat = ttk.LabelFrame(tabSampler, text="2-bit statistics")
            frmBstat.grid(row=30,column=0,sticky=E+W+S+N, padx=10, pady=10)
            ttk.Label(frmBstat, text="samp. 0", width=labelWidth).grid(row=1,column=0, sticky=E+W, padx=5)
            ttk.Label(frmBstat, text="samp. 1").grid(row=2,column=0, sticky=E+W, padx=5)
            ttk.Label(frmBstat, text="samp. 2").grid(row=3,column=0, sticky=E+W, padx=5)
            ttk.Label(frmBstat, text="samp. 3").grid(row=4,column=0, sticky=E+W, padx=5)

        pltStats = []
        self.aniSamplerBstats = []
        count = 0

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                continue
            b = i+1
            

            ttk.Label(frmSamplerPower, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)
#            if (self.displayOptions['samplerOffset']):
#               ttk.Label(frmSamplerOffset, text=str(b)).grid(row=1,column=i+1, sticky=E+W)
            ttk.Label(frmSamplerDelay, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)

            # sampler gain
            key = "if_{}_sampler_delta_power".format(b)
            self.messageComp[key] = ttk.Button(frmSamplerPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key], width=9)
            self.messageComp[key].grid(row=2, column=i+1, sticky=E+W)
            for sampler in range(4):
                key ="if_{}_sampler{}_power".format(b,sampler)
                self.messageComp[key] = ttk.Button(frmSamplerPower, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key], width=9)
                self.messageComp[key].grid(row=sampler+3, column=i+1, sticky=E+W)
            
            # sampler sync
            #key ="if_{}_sync".format(b)
            ##self.messageComp[key] = ttk.Button(frmSamplerDelay, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
            #self.messageComp[key].grid(row=2, column=i+1, sticky=E+W)

            # sampler delay correlations
            corrs = ["01","12","23"]
            row = 3
            for corr in corrs:
                key = "if_{}_delayCorr_{}".format(b, corr)
                self.messageComp[key] = ttk.Button(frmSamplerDelay, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key], width=9)
                self.messageComp[key].grid(row=row, column=i+1, sticky=E+W )
                row +=1

            # sampler offsets (based on bstates)
            #if self.displayOptions["samplerBstateOffset"]):
                

            # sampler bstates
            if (self.displayOptions["samplerBstate"]):
                fig, ax = plt.subplots(4,1)
                fig.set_size_inches(0.8, 4*0.7)
                for f in range(4):
                    print (b,f)
                    pltStats.append (PlotBstat(ax[f], self.messageVars["if_{}_sampler{}_statsFrac".format(b, f)]))
                    self.aniSamplerBstats.append( animate.FuncAnimation(fig, pltStats[count].update, interval=1000,  blit=True))
                    count += 1

                fig.tight_layout()
                canvasBstats = FigureCanvasTkAgg(fig, master=frmBstat)
                canvasBstats.get_tk_widget().grid(row=1, column=b, rowspan=4, sticky=E+W+S+N)
                

    def _setupWidgets(self):
        '''
        Define the widget layout common to all DBBC3 multicast modes.
        '''

        # define styles
        self.style = ttk.Style()
        myfont = font.Font(family="Arial", size=11)
        smallfont = font.Font(family="Arial", size=6)

        self.style.configure("Small.TButton",font=smallfont, foreground="black", relief="ridge",  justify="center", width=self.txtWidth)
        self.style.map( "Small.TButton", foreground=[("disabled", "black")], justify=[("disabled", "center")])

        self.style.configure("My.TButton",font=myfont, foreground="black", relief="ridge",  justify="center", width=self.txtWidth)
        self.style.map( "My.TButton", foreground=[("disabled", "black")], justify=[("disabled", "center")])

        self.style.configure("OK.TButton",font=myfont, foreground="black", relief="ridge", background="lime green", justify="center", width=self.txtWidth)
        self.style.map( "OK.TButton", foreground=[("disabled", "black")], background=[("disabled", "lime green")],justify=[("disabled", "center")])

        self.style.configure("WARN.TButton",font=myfont, foreground="black", relief="sunken", background="orange", justify="center", width=self.txtWidth)
        self.style.map( "WARN.TButton", foreground=[("disabled", "black")], background=[("disabled", "orange")],justify=[("disabled", "center")])

        self.style.configure("ERROR.TButton",font=myfont, foreground="black", relief="sunken", background="red", justify="center", width=self.txtWidth)
        self.style.map( "ERROR.TButton", foreground=[("disabled", "black")], background=[("disabled", "red")],justify=[("disabled", "center")])

        self.style.configure("OFF.TButton",font=myfont, foreground="grey", relief="sunken", background="darkgrey", justify="center", width=self.txtWidth)
        self.style.map( "OFF.TButton", foreground=[("disabled", "grey")], background=[("disabled", "darkgrey")],justify=[("disabled", "center")])

        # dashboard column layout
        labelWidth = 10
        boardColWidth = 7

        # menubar setup
        menubar = Menu()
        optionmenu = Menu(menubar, tearoff=0)
        menubar.add_command(label="Exit", command=self.root.quit)
        self.root.config(menu=menubar)

        #Notebook tab container
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=10, column=10, rowspan=100, sticky=E+W+S+N)
        self.notebook.columnconfigure(10, weight=2)

        if (self.mode == "DDC_U"):
            self._setupWidgets_DDC_U()

        # define the frames
        frmInfo = ttk.LabelFrame(self.root, text="DBBC3")
        frmInfo.grid(row=5,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmTime = ttk.LabelFrame(self.root, text="Last Multicast")
        frmTime.grid(row=5,column=10, sticky=E+W+N+S, padx=2,pady=2)

        frmIf = ttk.LabelFrame(self.root, text="IF Power")
        frmIf.grid(row=10,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSynth = ttk.LabelFrame(self.root, text="Downconversion")
        frmSynth.grid(row=20,column=0, sticky=E+W+N+S, padx=2,pady=2)

        frmSampler = ttk.LabelFrame(self.root, text="Sampler")
        frmSampler.grid(row=30,column=0, sticky=E+W+N+S, padx=2,pady=2)

        # frmGeneral setup
        ttk.Label(frmInfo, text="mode", width=labelWidth).grid(row=2,column=0, sticky=W, padx=2)
        ttk.Label(frmInfo, text="FW Version", width=labelWidth).grid(row=3,column=0, sticky=W, padx=2)
        self.messageComp["mode"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["mode"])
        self.messageComp["majorVersion"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["majorVersion"])
        self.messageComp["minorVersion"] = ttk.Button(frmInfo, style="My.TButton", state=DISABLED, textvariable=self.messageVars["minorVersion"])

        self.messageComp["mode"].grid(row=2,column=10, columnspan=2, sticky='ew' )
        self.messageComp["majorVersion"].grid(row=3,column=10, sticky='ew')
        self.messageComp["minorVersion"].grid(row=3,column=11, sticky='ew')


        # frmTime setup
        self.messageComp["time"] = ttk.Label(frmTime, textvariable=self.messageVars["time"])
        self.messageComp["time"].grid(row=4,column=10, columnspan=10, sticky=E+W+N+S, padx=2,pady=2)

        # frmIf setup
        ttk.Label(frmIf, text="counts", width=labelWidth).grid(row=2,column=0, sticky=W)
        ttk.Label(frmIf, text="target", width=labelWidth).grid(row=3,column=0, sticky=W)
        ttk.Label(frmIf, text="mode", width=labelWidth).grid(row=4,column=0, sticky=W)
        ttk.Label(frmIf, text="attenuation", width=labelWidth).grid(row=5,column=0, sticky=W)
        ttk.Label(frmSynth, text="enabled", width=labelWidth).grid(row=2,column=0, sticky=W)
        ttk.Label(frmSynth, text="synth", width=labelWidth).grid(row=3,column=0, sticky=W)
        ttk.Label(frmSynth, text="frequency", width=labelWidth).grid(row=4,column=0, sticky=W)

        # frmSampler setup
        ttk.Label(frmSampler, text="in-sync", width=labelWidth).grid(row=2,column=0, sticky=W)

        for i in range(len(self.activeBoards)):
            if not self.activeBoards[i]:
                #print (i, self.activeBoards[i])
                continue
            b = i+1

            ttk.Label(frmIf, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)
            ttk.Label(frmSynth, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)
            ttk.Label(frmSampler, text=str(b), width=boardColWidth).grid(row=1,column=i+1, sticky=E+W)

            #frmIf
            key = "if_{}_count".format(b)
            self.messageComp[key] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
            key = "if_{}_target".format(b)
            self.messageComp[key] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
            key = "if_{}_mode".format(b)
            self.messageComp[key] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
            key = "if_{}_attenuation".format(b)
            self.messageComp[key] = ttk.Button(frmIf, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])

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

            # sampler sync
            key ="if_{}_sync".format(b)
            self.messageComp[key] = ttk.Button(frmSampler, style="My.TButton", state=DISABLED, textvariable=self.messageVars[key])
            self.messageComp[key].grid(row=2, column=i+1, sticky=E+W)

            # frmSampler
            #for s in range(4):
            #    self.messageComp["if_{}_sampler{}_state".format(b,s)] = ttk.Button(frmSampler, style="My.TButton", state=DISABLED, textvariable=self.messageVars["if_{}_sampler{}_state".format(b,s)])
            #    self.messageComp["if_{}_sampler{}_state".format(b,s)].grid(row=2+s, column=i+1, sticky=E+W)

        # setup notebook tabs
        self._setupTabIF()

        self._setupTabSampler()

        if (self.displayOptions["tabBBC"]):
            self._setupTabBBC()

        if (self.displayOptions["tabFilter"]):
            self._setupTabFilter()


        #if self.mode == "OCT_D" and self.majorVersion >= 120:
        #    self._setupTabFilter()
        

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


