#!/usr/bin/env python

import argparse
import json
import re
from dbbc3.DBBC3Multicast import DBBC3Multicast

from Tkinter import *

args = None

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

        self.mc = DBBC3Multicast(args.group, args.port, args.timeout)
        self._setupWidgets()
        self.update()
        self.root.mainloop()

    def show(self):
        
        self._setupWidgets()

    def update(self):

            print ("polling")
            self.mc.poll()

            print (self.mc.message["mode"])
            print (self.mc.message["majorVersion"])
            print (self.mc.message["minorVersion"])
            print (self.mc.message["minorVersionString"])
            print (self.mc.activeIFs)
            for board in range(1,9):
                print (board, self.mc.activeIFs)
                if str(board) in self.mc.activeIFs:
                    self.lblCount[board-1].config(text=self.mc.message["if_{0}".format(board)]["count"])
                    self.lblTarget[board-1].config(text=self.mc.message["if_{0}".format(board)]["target"])
                    self.lblMode[board-1].config(text=self.mc.message["if_{0}".format(board)]["mode"])
                    self.lblAtt[board-1].config(text=self.mc.message["if_{0}".format(board)]["attenuation"])

                    if self.mc.message["if_{0}".format(board)]["mode"] != "agc":
                        self.lblMode[board-1].config(bg="red")
                    else:
                        self.lblMode[board-1].config(bg="green")

                    if abs(self.mc.message["if_{0}".format(board)]["attenuation"] - 31) < 10:
                        self.lblAtt[board-1].config(bg="green")
                    elif abs(self.mc.message["if_{0}".format(board)]["attenuation"] - 31) < 15:
                        self.lblAtt[board-1].config(bg="orange")
                    elif abs(self.mc.message["if_{0}".format(board)]["attenuation"] - 31) < 20:
                        self.lblAtt[board-1].config(bg="red")
                    
                    print (self.mc.message["if_{0}".format(board)]["count"])
                    print (self.mc.message["if_{0}".format(board)]["target"])
                    print (self.mc.message["if_{0}".format(board)]["attenuation"])
                    print (self.mc.message["if_{0}".format(board)]["mode"])
                    print ("tsys: ", self.mc.message["if_{0}".format(board)]["tsys"])
                    print ("delayCorr: ", self.mc.message["if_{0}".format(board)]["delayCorr"])
                    print ("synth: ", self.mc.message["if_{0}".format(board)]["synth"])
                    print ("tpOn: ", self.mc.message["if_{0}".format(board)]["tpOn"])
                    print ("tpOff: ", self.mc.message["if_{0}".format(board)]["tpOff"])
                    print ("time: ", self.mc.message["if_{0}".format(board)]["time"])
                    print ("ppsDelay: ", self.mc.message["if_{0}".format(board)]["ppsDelay"])
                    print (self.mc.message["if_{0}".format(board)].keys())

                    for sNum in range(4):
                            print (self.mc.message["if_{0}".format(board)]["sampler{0}".format(sNum)])

                    for bbc in range(8):
                        # first eight BBCs
                        print ("bbc_{0}".format(bbc+1+(int(board)-1)*8), self.mc.message["if_{0}".format(board)]["bbc_{0}".format(bbc+1+(int(board)-1)*8)])
                        # second eight BBCs
                        print ("bbc_{0}".format(bbc+65+(int(board)-1)*8), self.mc.message["if_{0}".format(board)]["bbc_{0}".format(bbc+65+(int(board)-1)*8)])
                else:
                    self.lblName[board-1].grid_forget()
                    self.lblCount[board-1].grid_forget()
                    self.lblTarget[board-1].grid_forget()
                    self.lblMode[board-1].grid_forget()
                    self.lblAtt[board-1].grid_forget()
            self.root.after(5000, self.update)

    def _setupWidgets(self):

        # menubar setup
        menubar = Menu(self.parent)

        optionmenu = Menu(menubar, tearoff=0)
#        optionmenu.add_command(label="Label options", command=self.showLabelOptions)
#        optionmenu.add_command(label="Database options", command=self.showDatabaseOptions)
#        optionmenu.add_command(label="Notification options", command=self.showNotificationOptions)

#        toolsmenu = Menu(menubar, tearoff=0)
#        toolsmenu.add_command(label="Print VSN label", command=self.showPrintVSNDialog)

        menubar.add_command(label="Exit", command=self.root.quit)
#        menubar.add_cascade(label="Tools", menu=toolsmenu)
#        menubar.add_cascade(label="Options", menu=optionmenu)


        self.root.config(menu=menubar)

        frmBoards = LabelFrame(self.root, text="Boards")
        frmBoards.grid(row=0,column=0, sticky=E+W+N+S, padx=2,pady=2)
        Label(frmBoards, text="name").grid(row=0,column=0, sticky=W)

        boardFrames = []
        self.lblCount = []
        self.lblTarget = []
        self.lblMode = []
        self.lblAtt = []
        self.lblName = []
        for i in range(8):
            self.lblName.append(Label(frmBoards, text=str(i)))
            self.lblCount.append(Button(frmBoards, relief=SUNKEN,state=DISABLED, disabledforeground="black", text=str(i)))
            self.lblTarget.append(Button(frmBoards, relief=SUNKEN,state=DISABLED, disabledforeground="black", text=str(i)))
            self.lblMode.append(Button(frmBoards, relief=SUNKEN,state=DISABLED, disabledforeground="black", text=str(i)))
            self.lblAtt.append(Button(frmBoards, relief=SUNKEN,state=DISABLED, disabledforeground="black", text=str(i)))

            self.lblName[i].grid(row=i,column=1, sticky=W)
            self.lblCount[i].grid(row=i,column=2, sticky=W)
            self.lblTarget[i].grid(row=i,column=3, sticky=W)
            self.lblMode[i].grid(row=i,column=4, sticky=W)
            self.lblAtt[i].grid(row=i,column=5, sticky=W)
            # counts
            #boardFrames.append(tmpFrame)

    def updateBoardInfo(self, message):

        pass
        

def parseCommandLine():

    parser = argparse.ArgumentParser("Check dbbc3 multicast")

    parser.add_argument("-p", "--port", default=25000, type=int, help="The multicast port (default: %(default)s)")
    parser.add_argument("-g", "--group", default="224.0.0.255", type=str, help="The multicast group (default: %(default)s)")
    parser.add_argument("-m", "--mode", required=False, help="The current DBBC3 mode, e.g. OCT_D or DDC_V")
    parser.add_argument("-t", "--timeout", required=False, help="The maximum number of seconds to wait for a multicast message.")
    parser.add_argument("--use-version", dest='ver', default= "", help="The version of the DBBC3 software.  Will assume the latest release version if not specified")

    return(parser.parse_args())

args = parseCommandLine()

mainDlg = MainWindow(None)


