from PyQt4 import QtGui, QtCore, uic
from twisted.internet.defer import inlineCallbacks, Deferred
import twisted
import numpy as np
import pyqtgraph as pg
import exceptions
import time
import sys
import platform
import datetime
import os
import dirExplorer

path = sys.path[0] + r"\Labrad Connect"
LabRADConnectUI, QtBaseClass = uic.loadUiType(path + r"\LabRADConnect.ui")

class Window(QtGui.QMainWindow, LabRADConnectUI):
    cxnsignal = QtCore.pyqtSignal(str, object)
    discxnsignal = QtCore.pyqtSignal(str)
    newSessionFolder = QtCore.pyqtSignal(str)
    newDVFolder = QtCore.pyqtSignal(list)
    
    def __init__(self, reactor, parent=None):
        super(Window, self).__init__(parent)
        self.reactor = reactor
        self.setupUi(self)
        self.setupAdditionalUi()
        self.moveDefault()
        
        #Initialize variables for all possible server connections in a dictionary
        #Makes multiple connections for browsing data vault in every desired context
        self.LabradDictionary = {
        'cxn'       : False,
        'dv'        : False,
        'ser_server': False,
        'DACADC'   : False,
        'SR830'   : False,
        'SR860'   : False,
        'SIM900'   : False,
        'GPIBDeviceManager'   : False,
        'GPIBServer'   : False,
        }
        
        self.pushButtonDictionary = {
        'cxn'       : self.pushButton_LabRAD,
        'dv'        : self.pushButton_DataVault,
        'ser_server': self.pushButton_SerialServer,
        'DACADC'   : self.pushButton_DACADC,
        'SR830'   : self.pushButton_SR830,
        'SR860'   : self.pushButton_SR860,
        'SIM900'   : self.pushButton_SIM900,
        'GPIBDeviceManager'   : self.pushButton_GPIBDeviceManager,
        'GPIBServer'   : self.pushButton_GPIBServer,
        }

        self.labelDictionary = {
        'cxn'       : self.label_Labrad,
        'dv'        : self.label_DataVault,
        'ser_server': self.label_SerialServer,
        'DACADC'   : self.label_DACADC,
        'SR830'   : self.label_SR830,
        'SR860'   : self.label_SR860,
        'SIM900'   : self.label_SIM900,
        'GPIBDeviceManager'   : self.label_GPIBDeviceManager,
        'GPIBServer'   : self.label_GPIBServer,
        }
        
        #Data vault session info
        self.lineEdit_DataVaultFolder.setReadOnly(True)
        self.DVFolder = ''
        self.lineEdit_DataVaultFolder.setText(self.DVFolder)
        
        #Saving images of all data taken info
        self.lineEdit_SessionFolder.setReadOnly(True)
        home = os.path.expanduser("~")
        self.SessionFolder = home + '\\Data Sets\\DEMONSData\\' + str(datetime.date.today())
        self.lineEdit_SessionFolder.setText(self.SessionFolder)
        
        folderExists = os.path.exists(self.SessionFolder)
        if not folderExists:
            os.makedirs(self.SessionFolder)
        
        self.pushButton_ConnectAll.clicked.connect(self.connectAllServers)
        self.pushButton_DisconnectAll.clicked.connect(self.disconnectAllServers)

        self.pushButton_LabRAD.clicked.connect(lambda: self.connectServer('cxn'))
        self.pushButton_DataVault.clicked.connect(lambda: self.connectServer('dv'))
        self.pushButton_DACADC.clicked.connect(lambda: self.connectServer('DACADC'))
        self.pushButton_SerialServer.clicked.connect(lambda: self.connectServer('ser_server'))
        self.pushButton_SR830.clicked.connect(lambda: self.connectServer('SR830'))
        self.pushButton_SR860.clicked.connect(lambda: self.connectServer('SR860'))
        self.pushButton_SIM900.clicked.connect(lambda: self.connectServer('SIM900'))
        self.pushButton_GPIBDeviceManager.clicked.connect(lambda: self.connectServer('GPIBDeviceManager'))
        self.pushButton_GPIBServer.clicked.connect(lambda: self.connectServer('GPIBServer'))

        self.key_list = []
        
        self.pushButton_DataVaultFolder.clicked.connect(self.chooseDVFolder)
        self.pushButton_SessionFolder.clicked.connect(self.chooseSessionFolder)
    
    def setupAdditionalUi(self):
        pass

    @inlineCallbacks
    def connectServer(self, servername, disconnect = True): #Click to toggle connection to a server
        try:
            if self.LabradDictionary[servername] is False:
                if servername == 'cxn':
                    from labrad.wrappers import connectAsync
                    try:
                        cxn = yield connectAsync(host = '127.0.0.1', password = 'pass')
                        self.LabradDictionary[servername] = cxn
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'dv':
                    try:
                        dv = yield self.LabradDictionary['cxn'].data_vault
                        self.LabradDictionary[servername] = dv
                        self.DVFolder = r'\.dataVault'
                        self.lineEdit_DataVaultFolder.setText(self.DVFolder)
                        self.newDVFolder.emit([])#Emit DataVault Default
                        self.newSessionFolder.emit(self.SessionFolder)
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'ser_server':
                    try:
                        computerName = platform.node() # get computer name
                        serialServerName = computerName.lower().replace(' ','_').replace('-','_') + '_serial_server'
                        ser_server = yield self.LabradDictionary['cxn'].servers[serialServerName]
                        self.LabradDictionary[servername] = ser_server
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'DACADC':
                    try:
                        dac = yield self.LabradDictionary['cxn'].dac_adc
                        self.LabradDictionary[servername] = dac
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'SR830':
                    try:
                        sr830 = yield self.LabradDictionary['cxn'].sr830
                        self.LabradDictionary[servername] = sr830
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'SR860':
                    try:
                        sr860 = yield self.LabradDictionary['cxn'].sr860
                        self.LabradDictionary[servername] = sr860
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'SIM900':
                    try:
                        sim900 = yield self.LabradDictionary['cxn'].sim900
                        self.LabradDictionary[servername] = sim900
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'GPIBDeviceManager':
                    try:
                        gpib_device_manager = yield self.LabradDictionary['cxn'].gpib_device_manager
                        self.LabradDictionary[servername] = gpib_device_manager
                        connection_flag = True
                    except:
                        connection_flag = False
                elif servername == 'GPIBServer':
                    try:
                        computerName = platform.node() # get computer name
                        gpibServerName = computerName.lower().replace(' ','_').replace('-','_') + '_gpib_bus'
                        gpib_server = yield self.LabradDictionary['cxn'].servers[gpibServerName]
                        self.LabradDictionary[servername] = gpib_server
                        connection_flag = True
                    except Exception as inst:
                        connection_flag = False
                        print inst


                if connection_flag:
                    self.cxnsignal.emit(servername, self.LabradDictionary[servername])
                    self.labelDictionary[servername].setText('Connected')
                    self.pushButtonDictionary[servername].setStyleSheet('#' + str(self.pushButtonDictionary[servername].objectName()) + '{background: rgb(0, 170, 0);border-radius: 4px;}')
                else:
                    self.labelDictionary[servername].setText('Connection Failed.')
                    self.pushButtonDictionary[servername].setStyleSheet('#' + str(self.pushButtonDictionary[servername].objectName()) + '{background: rgb(161, 0, 0);border-radius: 4px;}')
            else:
                if disconnect:
                    self.disconnectServer(servername)
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno
            
    def disconnectServer(self, servername): 
        try:
            self.LabradDictionary[servername] = False
            self.labelDictionary[servername].setText('Disconnected.')
            self.pushButtonDictionary[servername].setStyleSheet('#' + str(self.pushButtonDictionary[servername].objectName()) + '{background: rgb(161, 0, 0);border-radius: 4px;}')
            self.discxnsignal.emit(servername)
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno
    
    @inlineCallbacks
    def connectAllServers(self, e):
        yield self.connectServer('cxn', False)
        yield self.sleep(1)
        for name in self.LabradDictionary:
            if name == 'cxn':
                pass
            else:
                yield self.connectServer(name, False)
            
    def disconnectAllServers(self, e):
        for name in self.LabradDictionary:
            self.disconnectServer(name)

    @inlineCallbacks
    def chooseDVFolder(self, c = None):
        try:
            if self.LabradDictionary['dv'] is False:
                msgBox = QtGui.QMessageBox(self)
                msgBox.setIcon(QtGui.QMessageBox.Information)
                msgBox.setWindowTitle('Data Vault Connection Missing')
                msgBox.setText("\r\n Cannot choose data vault folder until connected to data vault.")
                msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
                msgBox.setStyleSheet("background-color:black; color:rgb(168,168,168)")
                msgBox.exec_()
            else: 
                dv = self.LabradDictionary['dv']
                dvExplorer = dirExplorer.dataVaultExplorer(dv, self.reactor, self)
                yield dvExplorer.popDirs()
                dvExplorer.show()
                dvExplorer.raise_()
                dvExplorer.accepted.connect(lambda: self.OpenDataVaultFolder(self.reactor, dv, dvExplorer.directory)) 

        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno                    
   
    @inlineCallbacks
    def OpenDataVaultFolder(self, c, datavault, directory):
        try:
            yield datavault.cd(directory)
            directory = directory[1:]
            DVFolder  = ''
            DVList = []
            for i in directory:
                DVList.append(i)
                DVFolder = DVFolder + '\\' + i
            self.DVFolder = r'\.datavault' + DVFolder
            self.lineEdit_DataVaultFolder.setText(self.DVFolder)
            self.newDVFolder.emit(DVList)
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno                    
              
    def chooseSessionFolder(self):
        home = os.path.expanduser("~")
        folder = str(QtGui.QFileDialog.getExistingDirectory(self, directory = home + '\\Data Sets\\DEMONSData'))
        if folder:
            self.SessionFolder = folder
            self.lineEdit_SessionFolder.setText(self.SessionFolder)
            self.newSessionFolder.emit(self.SessionFolder)
        
    def moveDefault(self):    
        self.move(650, 10)



    def sleep(self,secs):
        """Asynchronous compatible sleep command. Sleeps for given time in seconds, but allows
        other operations to be done elsewhere while paused."""
        d = Deferred()
        self.reactor.callLater(secs,d.callback,'Sleeping')
        return d        