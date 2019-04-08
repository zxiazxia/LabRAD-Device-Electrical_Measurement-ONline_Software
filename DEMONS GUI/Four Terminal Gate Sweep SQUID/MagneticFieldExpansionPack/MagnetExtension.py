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
from scipy.signal import detrend
#importing a bunch of stuff

from DEMONSFormat import *

path = sys.path[0] + r"\Four Terminal Gate Sweep SQUID\MagneticFieldExpansionPack"
Ui_MagnetControlWindow, QtBaseClass = uic.loadUiType(path + r"\MagnetExtensionWindow.ui")
Ui_ServerList, QtBaseClass = uic.loadUiType(path + r"\requiredServers.ui")

class MagnetControl(QtGui.QMainWindow, Ui_MagnetControlWindow):
    def __init__(self, reactor, parent = None):
        super(MagnetControl, self).__init__(parent)

        self.reactor = reactor
        self.parent = parent
        self.setupUi(self)

        self.pushButton_Servers.clicked.connect(self.showServersList)

        self.comboBox_MagnetControl_SelectServer.currentIndexChanged.connect(lambda: SelectServer(self.parent.DeviceList, 'Magnet_Device', self.parent.serversList, str(self.parent.DeviceList['Magnet_Device']['ComboBoxServer'].currentText())))
        self.comboBox_MagnetControl_SelectDevice.currentIndexChanged.connect(lambda: SelectDevice(self.parent.DeviceList, 'Magnet_Device', str(self.parent.DeviceList['Magnet_Device']['ComboBoxDevice'].currentText()), self.parent.Refreshinterface))
        self.lineEdit_StartField.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'MagnetControl_StartField', self.parent.lineEdit))
        self.lineEdit_StartField.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.parent.Parameter, 'MagnetControl_Numberofstep', 'MagnetControl_EndField', 'MagnetControl_StartField', 'MagnetControl_Numberofstep_Status', self.parent.lineEdit))
        self.lineEdit_EndVoltage.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'MagnetControl_EndField', self.parent.lineEdit))
        self.lineEdit_EndVoltage.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.parent.Parameter, 'MagnetControl_Numberofstep', 'MagnetControl_EndField', 'MagnetControl_StartField', 'MagnetControl_Numberofstep_Status', self.parent.lineEdit))
        self.lineEdit_Numberofstep.editingFinished.connect(lambda: UpdateLineEdit_NumberOfStep(self.parent.Parameter, 'MagnetControl_Numberofstep', 'MagnetControl_EndField', 'MagnetControl_StartField', 'MagnetControl_Numberofstep_Status', self.parent.lineEdit))
        self.pushButton_MagnetControl_NoSmTpTSwitch.clicked.connect(lambda: Toggle_NumberOfSteps_StepSize(self.parent.Parameter, 'MagnetControl_Numberofstep', 'MagnetControl_EndField', 'MagnetControl_StartField', 'MagnetControl_Numberofstep_Status', self.label_MangnetControl_NumberofStep, 'Tesla per Step', self.parent.lineEdit))  
        self.lineEdit_RampSpeed.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'MagnetControl_RampSpeed', self.parent.lineEdit))
        self.lineEdit_Delay.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.parent.Parameter, 'MagnetControl_Delay', self.parent.lineEdit))

        self.Plotlist = {}


        self.Plotlist['ResistancePlot'] = {
            'PlotObject': pg.PlotItem(),
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Resistance_2DPlot,
            'Title': 'Resistance',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        self.Plotlist['ResistancePlot']['ImageViewObject'] = pg.ImageView(parent = None, view = self.Plotlist['ResistancePlot']['PlotObject'])
        self.Plotlist['ResistancePlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Resistance_YZ,
            'Title': None,
            'XAxisName': 'Resistance',
            'XUnit': u"\u03A9",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
        }
        self.Plotlist['ResistancePlot']['XZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Resistance_XZ,
            'Title': None,
            'XAxisName': 'Gate Voltage',
            'XUnit':"V",
            'YAxisName': 'Resistance',
            'YUnit': u"\u03A9", 
        }

        self.Plotlist['VoltagePlot'] = {
            'PlotObject': pg.PlotItem(),
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Voltage_2DPlot,
            'Title': 'Voltage',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        self.Plotlist['VoltagePlot']['ImageViewObject'] = pg.ImageView(parent = None, view = self.Plotlist['VoltagePlot']['PlotObject'])
        self.Plotlist['VoltagePlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Voltage_YZ,
            'Title': None,
            'XAxisName': 'Voltage',
            'XUnit':"V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
        }
        self.Plotlist['VoltagePlot']['XZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Voltage_XZ,
            'Title': None,
            'XAxisName': 'Gate Voltage',
            'XUnit':"V",
            'YAxisName': 'Voltage',
            'YUnit': "V", 
        }

        self.Plotlist['CurrentPlot'] = {
            'PlotObject': pg.PlotItem(),
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Current_2DPlot,
            'Title': 'Current',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        self.Plotlist['CurrentPlot']['ImageViewObject'] = pg.ImageView(parent = None, view = self.Plotlist['CurrentPlot']['PlotObject'])
        self.Plotlist['CurrentPlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Current_YZ,
            'Title': None,
            'XAxisName': 'Current',
            'XUnit':"A",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
        }
        self.Plotlist['CurrentPlot']['XZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Current_XZ,
            'Title': None,
            'XAxisName': 'Gate Voltage',
            'XUnit':"V",
            'YAxisName': 'Current',
            'YUnit': "A", 
        }

        self.SetupPlots()

    def DetermineEnableConditions(self):
        self.ButtonsCondition={
            self.pushButton_StartFourTerminalSweep: (not self.parent.DeviceList['Magnet_Device'] == False) and self.parent.DEMONS.Scanning_Flag == False,
            self.pushButton_AbortFourTerminalSweep: (not self.parent.DeviceList['Magnet_Device'] == False) and self.parent.DEMONS.Scanning_Flag == True,
            self.comboBox_MagnetControl_SelectServer: self.parent.DEMONS.Scanning_Flag == False,
            self.comboBox_MagnetControl_SelectDevice: self.parent.DEMONS.Scanning_Flag == False,
            self.lineEdit_StartField: self.parent.DEMONS.Scanning_Flag == False,
            self.lineEdit_EndVoltage: self.parent.DEMONS.Scanning_Flag == False,
            self.lineEdit_Numberofstep: self.parent.DEMONS.Scanning_Flag == False,
            self.lineEdit_RampSpeed: self.parent.DEMONS.Scanning_Flag == False,
            self.lineEdit_Delay: self.parent.DEMONS.Scanning_Flag == False,
        }

    def Refreshinterface(self):
        self.DetermineEnableConditions()
        RefreshButtonStatus(self.ButtonsCondition)

    def SetupPlots(self):
        for PlotName in self.Plotlist:
            Setup2DPlot(self.Plotlist[PlotName]['PlotObject'], self.Plotlist[PlotName]['ImageViewObject'], self.Plotlist[PlotName]['Layout'], self.Plotlist[PlotName]['YAxisName'], self.Plotlist[PlotName]['YUnit'], self.Plotlist[PlotName]['XAxisName'], self.Plotlist[PlotName]['XUnit'])
            Setup1DPlot(self.Plotlist[PlotName]['YZPlot']['PlotObject'], self.Plotlist[PlotName]['YZPlot']['Layout'], self.Plotlist[PlotName]['YZPlot']['Title'], self.Plotlist[PlotName]['YZPlot']['YAxisName'], self.Plotlist[PlotName]['YZPlot']['YUnit'], self.Plotlist[PlotName]['YZPlot']['XAxisName'], self.Plotlist[PlotName]['YZPlot']['XUnit'])#Plot, Layout , Title , yaxis , yunit, xaxis ,xunit
            Setup1DPlot(self.Plotlist[PlotName]['XZPlot']['PlotObject'], self.Plotlist[PlotName]['XZPlot']['Layout'], self.Plotlist[PlotName]['XZPlot']['Title'], self.Plotlist[PlotName]['XZPlot']['YAxisName'], self.Plotlist[PlotName]['XZPlot']['YUnit'], self.Plotlist[PlotName]['XZPlot']['XAxisName'], self.Plotlist[PlotName]['XZPlot']['XUnit'])#Plot, Layout , Title , yaxis , yunit, xaxis ,xunit

    def moveDefault(self):
        self.move(200,0)

    def showServersList(self):
        serList = serversList(self.reactor, self)
        serList.exec_()

class serversList(QtGui.QDialog, Ui_ServerList):
    def __init__(self, reactor, parent = None):
        super(serversList, self).__init__(parent)
        self.setupUi(self)
        pos = parent.pos()
        self.move(pos + QtCore.QPoint(5,5))