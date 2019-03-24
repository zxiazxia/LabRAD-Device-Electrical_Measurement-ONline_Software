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

path = sys.path[0] + r"\Labrad Connect"
LabRADConnectUI, QtBaseClass = uic.loadUiType(path + r"\LabRADConnect.ui")

class Window(QtGui.QMainWindow, LabRADConnectUI):
    cxnsignal = QtCore.pyqtSignal(str, object)
    discxnsignal = QtCore.pyqtSignal(str)
    cxnLocal = QtCore.pyqtSignal(dict)
    cxnRemote = QtCore.pyqtSignal(dict)
    cxnDisconnected = QtCore.pyqtSignal()
    newSessionFolder = QtCore.pyqtSignal(str)
    newDVFolder = QtCore.pyqtSignal()
    
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
        'dac_adc'   : False
        }
        
        self.pushButtonDictionary = {
        'cxn'       : self.pushButton_LabRAD,
        'dv'        : self.pushButton_DataVault,
        'ser_server': self.pushButton_SerialServer,
        'dac_adc'   : self.pushButton_DACADC
        }

        self.labelDictionary = {
        'cxn'       : self.label_Labrad,
        'dv'        : self.label_DataVault,
        'ser_server': self.label_SerialServer,
        'dac_adc'   : self.label_DACADC
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
        self.pushButton_DACADC.clicked.connect(lambda: self.connectServer('dac_adc'))
        self.pushButton_SerialServer.clicked.connect(lambda: self.connectServer('ser_server'))

        self.key_list = []
        

        # self.pushButton_DataVaultFolder.clicked.connect(self.chooseSession)
        # self.pushButton_SessionFolder.clicked.connect(self.chooseSession_2)
    
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
                elif servername == 'dac_adc':
                    try:
                        dv = yield self.LabradDictionary['cxn'].dac_adc
                        self.LabradDictionary[servername] = dv
                        connection_flag = True
                    except:
                        connection_flag = False

                if connection_flag:
                    self.cxnsignal.emit(servername, self.LabradDictionary[servername])
                    self.labelDictionary[servername].setText('Connected')
                    self.pushButtonDictionary[servername].setStyleSheet('#' + str(self.pushButtonDictionary[servername].objectName()) + '{background: rgb(0, 170, 0);border-radius: 4px;}')
                    self.cxnsignal.emit(servername, self.LabradDictionary[servername])
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
            discxnsignal = QtCore.pyqtSignal(str)
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

    def moveDefault(self):    
        self.move(10,170)
        
    def sleep(self,secs):
        """Asynchronous compatible sleep command. Sleeps for given time in seconds, but allows
        other operations to be done elsewhere while paused."""
        d = Deferred()
        self.reactor.callLater(secs,d.callback,'Sleeping')
        return d        