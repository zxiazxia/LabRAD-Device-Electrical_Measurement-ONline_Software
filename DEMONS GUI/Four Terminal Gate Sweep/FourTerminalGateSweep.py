from __future__ import division
import sys
import twisted
from PyQt4 import QtCore, QtGui, QtTest, uic
from twisted.internet.defer import inlineCallbacks, Deferred , returnValue
import numpy as np
import pyqtgraph as pg
import exceptions
import time
import threading
import copy
import time
from scipy.signal import detrend
#importing a bunch of stuff


path = sys.path[0] + r"\Four Terminal Gate Sweep"
print path
FourTerminalGateSweepWindowUI, QtBaseClass = uic.loadUiType(path + r"\FourTerminalGateSweepWindow.ui")
Ui_ServerList, QtBaseClass = uic.loadUiType(path + r"\requiredServers.ui")

#Not required, but strongly recommended functions used to format numbers in a particular way.
sys.path.append(sys.path[0]+'\Resources')
from DEMONSFormat import *

class Window(QtGui.QMainWindow, FourTerminalGateSweepWindowUI):

    def __init__(self, reactor, parent=None):
        super(Window, self).__init__(parent)
        
        self.reactor = reactor
        self.parent = parent
        self.setupUi(self)

        self.push_Servers.clicked.connect(self.showServersList)

        self.Parameter = {
            'DeviceName': 'Device Name',
            'FourTerminal_MinVoltage': 0.0,
            'FourTerminal_MaxVoltage': 1.0,
            'FourTerminal_Delay': 0.01,
            'FourTerminalSetting_Numberofsteps_Status': "Numberofsteps",
            'FourTerminal_Numberofstep': 1000,
        }

        self.FourTerminal_ChannelInput=[]
        self.FourTerminal_ChannelOutput=[]

        self.lineEdit_Device_Name.editingFinished.connect(lambda: UpdateLineEdit_String(self.Parameter, 'DeviceName', self.lineEdit_Device_Name))

        self.lineEdit_FourTerminal_MinVoltage.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.Parameter, 'FourTerminal_MinVoltage', self.lineEdit_FourTerminal_MinVoltage, [-10.0, 10.0]))
        self.lineEdit_FourTerminal_MinVoltage.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.Parameter, 'FourTerminal_Numberofstep', 'FourTerminal_MaxVoltage', 'FourTerminal_MinVoltage', 'FourTerminalSetting_Numberofsteps_Status', self.lineEdit_FourTerminal_Numberofstep))
        self.lineEdit_FourTerminal_MaxVoltage.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.Parameter, 'FourTerminal_MaxVoltage', self.lineEdit_FourTerminal_MaxVoltage, [-10.0, 10.0]))
        self.lineEdit_FourTerminal_MaxVoltage.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.Parameter, 'FourTerminal_Numberofstep', 'FourTerminal_MaxVoltage', 'FourTerminal_MinVoltage', 'FourTerminalSetting_Numberofsteps_Status', self.lineEdit_FourTerminal_Numberofstep))
        self.lineEdit_FourTerminal_Numberofstep.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.Parameter, 'FourTerminal_Numberofstep', 'FourTerminal_MaxVoltage', 'FourTerminal_MinVoltage', 'FourTerminalSetting_Numberofsteps_Status', self.lineEdit_FourTerminal_Numberofstep))
        self.lineEdit_FourTerminal_Delay.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.Parameter, 'FourTerminal_Delay', self.lineEdit_FourTerminal_Delay))
        self.pushButton_FourTerminal_NoSmTpTSwitch.clicked.connect(lambda: Toggle_NumberOfSteps_StepSize(self.Parameter, 'FourTerminal_Numberofstep', 'FourTerminal_MaxVoltage', 'FourTerminal_MinVoltage', 'FourTerminalSetting_Numberofsteps_Status', self.label_FourTerminalNumberofstep, 'Volt per Step', self.lineEdit_FourTerminal_Numberofstep))  


    def showServersList(self):
        serList = serversList(self.reactor, self)
        serList.exec_()