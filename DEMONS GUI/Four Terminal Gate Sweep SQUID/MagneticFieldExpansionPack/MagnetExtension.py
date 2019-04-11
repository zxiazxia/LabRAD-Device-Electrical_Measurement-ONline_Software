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

        self.pushButton_StartFourTerminalSweep.clicked.connect(self.StartMeasurement)
        self.pushButton_AbortFourTerminalSweep.clicked.connect(lambda: self.parent.DEMONS.SetScanningFlag(False))

        self.Plotlist = {}
        self.Plotlist['ResistancePlot'] = {
            'PlotObject': None,
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Resistance_2DPlot,
            'Title': 'Resistance',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        self.Plotlist['ResistancePlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Resistance_YZ,
            'Title': None,
            'XAxisName': 'Resistance',
            'XUnit': u"\u03A9",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
            'LineCut': pg.InfiniteLine(pos = 0, angle = 90, movable = True),
            'LineEdit': self.lineEdit_Resistance_YZLineCut,
            'Value': 0.0,
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
            'LineCut': pg.InfiniteLine(pos = 0, angle = 0, movable = True),
            'LineEdit': self.lineEdit_Resistance_XZLineCut,
            'Value': 0.0,
        }

        self.Plotlist['VoltagePlot'] = {
            'PlotObject': None,
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Voltage_2DPlot,
            'Title': 'Voltage',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        self.Plotlist['VoltagePlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Voltage_YZ,
            'Title': None,
            'XAxisName': 'Voltage',
            'XUnit':"V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
            'LineCut': pg.InfiniteLine(pos = 0, angle = 90, movable = True),
            'LineEdit': self.lineEdit_Voltage_YZLineCut,
            'Value': 0.0,
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
            'LineCut': pg.InfiniteLine(pos = 0, angle = 0, movable = True),
            'LineEdit': self.lineEdit_Voltage_XZLineCut,
            'Value': 0.0,
        }

        self.Plotlist['CurrentPlot'] = {
            'PlotObject': None, #Define in Setup2DPlot
            'PlotData': np.zeros((2, 2)), 
            'Layout': self.Layout_Current_2DPlot,
            'Title': 'Current',
            'XAxisName': 'Gate Voltage',
            'XUnit': "V",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T",
        }
        # self.Plotlist['CurrentPlot']['PlotObject'] = pg.ImageView(view = self.Plotlist['CurrentPlot']['PlotObject'])
        self.Plotlist['CurrentPlot']['YZPlot'] = {
            'PlotObject': pg.PlotWidget(parent = None),
            'PlotData': [[], []],
            'Layout': self.Layout_Current_YZ,
            'Title': None,
            'XAxisName': 'Current',
            'XUnit':"A",
            'YAxisName': 'Magnetic Field',
            'YUnit': "T", 
            'LineCut': pg.InfiniteLine(pos = 0, angle = 90, movable = True),
            'LineEdit': self.lineEdit_Current_YZLineCut,
            'Value': 0.0,
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
            'LineCut': pg.InfiniteLine(pos = 0, angle = 0, movable = True),
            'LineEdit': self.lineEdit_Current_XZLineCut,
            'Value': 0.0,
        }

        self.SetupPlots()

    def DetermineEnableConditions(self):
        self.ButtonsCondition={
            self.pushButton_StartFourTerminalSweep: (self.parent.DeviceList['Magnet_Device']['DeviceObject'] != False) and self.parent.DEMONS.Scanning_Flag == False or True,
            self.pushButton_AbortFourTerminalSweep: self.parent.DEMONS.Scanning_Flag == True,
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
            Connect2DPlots(PlotName, self.Plotlist)

    @inlineCallbacks
    def StartMeasurement(self, c):
        try:
            self.parent.DEMONS.SetScanningFlag(True)
            self.parent.Refreshinterface()

            Multiplier = [self.parent.Parameter['Voltage_LI_Sensitivity'] * self.parent.Parameter['Voltage_LI_Gain'] / 10.0, self.parent.Parameter['Current_LI_Sensitivity'] * self.parent.Parameter['Current_LI_Gain'] / 10.0] #Voltage, Current

            ImageNumber, ImageDir = yield CreateDataVaultFile(self.parent.serversList['dv'], 'FourTerminalGateAndMagneticFieldSweep' + str(self.parent.Parameter['DeviceName']), ('Magnetic Field Index', 'Magnetic Field', 'Gate Index', 'Gate Voltage'), ('Voltage', 'Current', 'Resistance', 'Conductance'))
            self.parent.lineEdit_ImageNumber.setText(ImageNumber)
            self.parent.lineEdit_ImageDir.setText(ImageDir)

            yield AddParameterToDataVault(self.parent.serversList['dv'], self.parent.Parameter)
            ClearPlots(self.Plotlist)
            ClearPlots(self.parent.Plotlist)

            GateChannel, VoltageChannel, CurrentChannel = self.parent.Parameter['FourTerminal_GateChannel'], self.parent.Parameter['FourTerminal_VoltageReadingChannel'], self.parent.Parameter['FourTerminal_CurrentReadingChannel']
            StartVoltage, EndVoltage = self.parent.Parameter['FourTerminal_StartVoltage'], self.parent.Parameter['FourTerminal_EndVoltage']
            NumberOfSteps, Delay = self.parent.Parameter['FourTerminal_Numberofstep'], self.parent.Parameter['FourTerminal_Delay']
            StartField, EndField = self.parent.Parameter['MagnetControl_StartField'], self.parent.Parameter['MagnetControl_EndField']
            FieldSteps, FieldDelay = self.parent.Parameter['MagnetControl_Numberofstep'], self.parent.Parameter['MagnetControl_Delay']
            FieldSpeed = self.parent.Parameter['MagnetControl_RampSpeed']

            Data2D = np.empty((0, 8))

            for Plot in self.Plotlist:
                self.Plotlist[Plot]['PlotData'] = np.zeros((FieldSteps, NumberOfSteps))

            MagneticFieldSet = np.linspace(StartField, EndField, FieldSteps)
            for FieldIndex in range(FieldSteps):
                if self.parent.DEMONS.Scanning_Flag == False:
                    print 'Abort the Sweep'
                    yield self.FinishSweep()
                    break

                #Set Magnetic Field
                # yield RampMagneticField(self.parent.DeviceList['Magnet_Device']['DeviceObject'], str(self.parent.DeviceList['Magnet_Device']['ComboBoxServer'].currentText()), MagneticFieldSet[FieldIndex], FieldSpeed, self.reactor)
                yield SleepAsync(self.reactor, FieldDelay)

                #Ramp DACADC to initial
                yield Ramp_DACADC(self.parent.DeviceList['DataAquisition_Device']['DeviceObject'], GateChannel, 0.0, StartVoltage, self.parent.Parameter['Setting_RampStepSize'], self.parent.Parameter['Setting_RampDelay'])
                yield SleepAsync(self.reactor, self.parent.Parameter['Setting_WaitTime'])

                #Take Data
                Data1D = yield Buffer_Ramp_DACADC(self.parent.DeviceList['DataAquisition_Device']['DeviceObject'], [GateChannel], [VoltageChannel, CurrentChannel],[StartVoltage], [EndVoltage], NumberOfSteps, Delay)
                
                Data1D = Multiply(Data1D, Multiplier) #Scale them with corresponding multiplier [voltage, current]
                Data1D = AttachData_Front(Data1D, np.linspace(StartVoltage, EndVoltage, NumberOfSteps)) #Attach Gate Voltage
                Data1D = AttachData_Front(Data1D, range(NumberOfSteps)) #Attach Gate Index
                Data1D = AttachData_Front(Data1D, np.linspace(MagneticFieldSet[FieldIndex], MagneticFieldSet[FieldIndex], NumberOfSteps)) #Attach Magnetic Field
                Data1D = AttachData_Front(Data1D, np.linspace(FieldIndex, FieldIndex, NumberOfSteps)) #Attach Field Index
                Data1D = Attach_ResistanceConductance(Data1D, 4, 5)
                self.parent.serversList['dv'].add(Data1D)

                XData = np.linspace(StartVoltage, EndVoltage, NumberOfSteps)
                VoltageData, CurrentData, ResistanceData = Data1D[:, 4], Data1D[:, 5], Data1D[:, 6]
                ClearPlots(self.parent.Plotlist)
                Plot1DData(XData, VoltageData, self.parent.Plotlist['VoltagePlot']['PlotObject'])
                Plot1DData(XData, CurrentData, self.parent.Plotlist['CurrentPlot']['PlotObject'])
                Plot1DData(XData, ResistanceData, self.parent.Plotlist['ResistancePlot']['PlotObject'])

                #Sync Data2D
                Data2D = np.append(Data2D, Data1D, axis = 0)
                self.Plotlist['VoltagePlot']['PlotData'][FieldIndex] = VoltageData
                self.Plotlist['CurrentPlot']['PlotData'][FieldIndex] = CurrentData
                self.Plotlist['ResistancePlot']['PlotData'][FieldIndex] = ResistanceData

                MinGateVoltage, MinField = np.amin([StartVoltage, EndVoltage]), np.amin([StartField, EndField])
                ScaleGateVoltage, ScaleField = abs(StartVoltage - EndVoltage) / (NumberOfSteps - 1), abs(StartField - EndField) / (FieldSteps - 1)
                for PlotName in self.Plotlist:
                    Plot2DData(self.Plotlist[PlotName]['PlotObject'], self.Plotlist[PlotName]['PlotData'].T, MinGateVoltage, MinField, ScaleGateVoltage, ScaleField, autoRange = self.checkBox_AutoRange.isChecked(), autoLevels = self.checkBox_AutoLevel.isChecked())
                    RefreshLineCutPlot(self.Plotlist[PlotName], 'YZPlot', self.Plotlist[PlotName]['PlotData'])
                    RefreshLineCutPlot(self.Plotlist[PlotName], 'XZPlot', self.Plotlist[PlotName]['PlotData'])

                if FieldIndex == FieldSteps - 1:
                    yield self.FinishSweep()

        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    @inlineCallbacks
    def FinishSweep(self):
        try:
            if self.checkBox_FourTerminalMagneticFieldSetting_BacktoZero.isChecked():
                yield SleepAsync(self.reactor, 1)
                # yield RampMagneticField(self.parent.DeviceList['Magnet_Device']['DeviceObject'], str(self.parent.DeviceList['Magnet_Device']['ComboBoxServer'].currentText()), 0.0, self.parent.Parameter['MagnetControl_RampSpeed'], self.reactor)
            self.parent.serversList['dv'].add_comment(str(self.parent.textEdit_Comment.toPlainText()))
            self.parent.DEMONS.SetScanningFlag(False)
            self.parent.Refreshinterface()
            saveDataToSessionFolder(self.winId(), self.parent.sessionFolder, str(self.parent.lineEdit_ImageNumber.text()) + ' - ' + 'Magnetic Field ' + self.parent.Parameter['DeviceName'])
            saveDataToSessionFolder(self.parent.winId(), self.parent.sessionFolder, str(self.parent.lineEdit_ImageNumber.text()) + ' - ' + 'Four Terminal ' + self.parent.Parameter['DeviceName'])

        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

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