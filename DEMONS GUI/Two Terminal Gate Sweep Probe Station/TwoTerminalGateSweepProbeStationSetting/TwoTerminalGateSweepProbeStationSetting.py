import sys
import twisted
from PyQt4 import QtCore, QtGui, QtTest, uic
from twisted.internet.defer import inlineCallbacks, Deferred
import numpy as np
import pyqtgraph as pg
import exceptions
import time
import threading
import copy

from DEMONSFormat import *

path = sys.path[0] + r"\Two Terminal Gate Sweep Probe Station\TwoTerminalGateSweepProbeStationSetting"
Ui_Setting, QtBaseClass = uic.loadUiType(path + r"\TwoTerminalGateSweepProbeStationSettingWindow.ui")

class Setting(QtGui.QMainWindow, Ui_Setting):
    def __init__(self, reactor, parent = None):
        super(Setting, self).__init__(parent)

        self.reactor = reactor
        self.setupUi(self)
        
        self.parent = parent

        self.lineEdit_Setting_RampDelay.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'Setting_RampDelay', self.parent.lineEdit))
        self.lineEdit_Setting_RampStepSize.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'Setting_RampStepSize', self.parent.lineEdit))
        self.lineEdit_Setting_WaitTime.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'Setting_WaitTime', self.parent.lineEdit))

    def moveDefault(self):
        self.move(200,0)
