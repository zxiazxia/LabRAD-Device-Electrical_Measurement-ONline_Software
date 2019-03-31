from __future__ import division
import sys
import twisted
from twisted.internet.defer import inlineCallbacks, Deferred , returnValue
from PyQt4 import Qt, QtGui, QtCore, uic
import numpy as np
import exceptions
import time
import threading
import copy
from scipy.signal import detrend
#importing a bunch of stuff


path = sys.path[0] + r"\DAC Controler"
print path
ControlerWindowUI, QtBaseClass = uic.loadUiType(path + r"\DACControlerWindow.ui")
Ui_ServerList, QtBaseClass = uic.loadUiType(path + r"\requiredServers.ui")

#Not required, but strongly recommended functions used to format numbers in a particular way.
sys.path.append(sys.path[0]+'\Resources')
from DEMONSFormat import *
from DEMONSMeasure import *

class Window(QtGui.QMainWindow, ControlerWindowUI):

    def __init__(self, reactor, parent=None):
        super(Window, self).__init__(parent)
        
        self.reactor = reactor
        self.parent = parent
        self.setupUi(self)

        self.pushButton_Servers.clicked.connect(self.showServersList)

        self.serversList = {
            'DACADC': False
        }

        self.ServerDeviceList = {
            'DACADC': ['DataAquisition_Device']
        }

        self.deviceList = {
            'DataAquisition_Device': False
        }

        self.targetnumber = {
            'Output1': 0.0,
            'Output2': 0.0,
            'Output3': 0.0,
            'Output4': 0.0
        }

        self.lineEdit = {
            'Output1': self.lineEdit_TargetNumber_1,
            'Output2': self.lineEdit_TargetNumber_2,
            'Output3': self.lineEdit_TargetNumber_3,
            'Output4': self.lineEdit_TargetNumber_4
        }

        for key in self.lineEdit:
            if not isinstance(self.targetnumber[key], str):
                UpdateLineEdit_Bound(self.targetnumber, key, self.lineEdit)

        self.DetermineEnableConditions()

        self.comboBox_Tracker_SelectDevice.currentIndexChanged.connect(lambda: SelectDevice(self.deviceList, self.serversList['DACADC'], 'DataAquisition_Device', str(self.comboBox_Tracker_SelectDevice.currentText()), self.pushButton_Device_Indicator, self.Refreshinterface))
        self.lineEdit_TargetNumber_1.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.targetnumber, 'Output1', self.lineEdit, [-10.0, 10.0]))
        self.lineEdit_TargetNumber_2.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.targetnumber, 'Output2', self.lineEdit, [-10.0, 10.0]))
        self.lineEdit_TargetNumber_3.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.targetnumber, 'Output3', self.lineEdit, [-10.0, 10.0]))
        self.lineEdit_TargetNumber_4.editingFinished.connect(lambda: UpdateLineEdit_Bound(self.targetnumber, 'Output4', self.lineEdit, [-10.0, 10.0]))

        self.pushButton_SET_1.clicked.connect(lambda: Set_DAC(self.deviceList['DataAquisition_Device'], 0, self.targetnumber['Output1']))
        self.pushButton_SET_2.clicked.connect(lambda: Set_DAC(self.deviceList['DataAquisition_Device'], 1, self.targetnumber['Output2']))
        self.pushButton_SET_3.clicked.connect(lambda: Set_DAC(self.deviceList['DataAquisition_Device'], 2, self.targetnumber['Output3']))
        self.pushButton_SET_4.clicked.connect(lambda: Set_DAC(self.deviceList['DataAquisition_Device'], 3, self.targetnumber['Output4']))

        self.pushButton_Read_1.clicked.connect(lambda: Read_ADC_SetLabel(self.deviceList['DataAquisition_Device'], 0, self.label_ADC_1))
        self.pushButton_Read_2.clicked.connect(lambda: Read_ADC_SetLabel(self.deviceList['DataAquisition_Device'], 1, self.label_ADC_2))
        self.pushButton_Read_3.clicked.connect(lambda: Read_ADC_SetLabel(self.deviceList['DataAquisition_Device'], 2, self.label_ADC_3))
        self.pushButton_Read_4.clicked.connect(lambda: Read_ADC_SetLabel(self.deviceList['DataAquisition_Device'], 3, self.label_ADC_4))

    def DetermineEnableConditions(self):
        self.ButtonsCondition={
            self.pushButton_SET_1: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_SET_2: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_SET_3: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_SET_4: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_Read_1: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_Read_2: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_Read_3: not self.deviceList['DataAquisition_Device'] == False,
            self.pushButton_Read_4: not self.deviceList['DataAquisition_Device'] == False,
        }

    def connectServer(self, key, server):
        try:
            self.serversList[str(key)] = server
            self.refreshServerIndicator()
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    def disconnectServer(self, key):
        try:
            self.serversList[str(key)] = False
            for key, listdevice in self.ServerDeviceList.iteritems():
                for devicename in listdevice:
                    self.deviceList[str(devicename)] = False
            self.refreshServerIndicator()
            self.Refreshinterface()
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    def refreshServerIndicator(self):
        try:
            optional = []
            flag = True
            for key in self.serversList:
                if self.serversList[str(key)] == False and not str(key) in optional:
                    flag = False
            if flag:
                setIndicator(self.pushButton_Servers, 'rgb(0, 170, 0)')

                #When all servers are connected, automatically select default device.
                RedefineComboBox(self.comboBox_Tracker_SelectDevice, self.serversList['DACADC'], self.deviceList, 'DataAquisition_Device')
                self.Refreshinterface()
            else:
                setIndicator(self.pushButton_Servers, 'rgb(161, 0, 0)')
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    def Refreshinterface(self): #exclude server
        self.DetermineEnableConditions()
        RefreshButtonStatus(self.ButtonsCondition)
        RefreshIndicator(self.pushButton_Device_Indicator, self.deviceList['DataAquisition_Device'])
            
    def moveDefault(self):
        self.move(10,170)
        
    def showServersList(self):
        serList = serversList(self.reactor, self)
        serList.exec_()
        
class serversList(QtGui.QDialog, Ui_ServerList):
    def __init__(self, reactor, parent = None):
        super(serversList, self).__init__(parent)
        self.setupUi(self)
        pos = parent.pos()
        self.move(pos + QtCore.QPoint(5,5))