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
        self.pushButton_DisconnectAll.clicked.connect(self.disconnectLabRAD)

        self.pushButton_LabRAD.clicked.connect(lambda: self.connect('cxn', self.pushButton_LabRAD, self.label_Labrad))

        self.key_list = []
        

        # self.pushButton_DataVaultFolder.clicked.connect(self.chooseSession)
        # self.pushButton_SessionFolder.clicked.connect(self.chooseSession_2)
    
    def setupAdditionalUi(self):
        pass

    @inlineCallbacks
    def connect(self, servername, pushbutton, label):
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
                pass

            if connection_flag:
                label.setText('Connected')
                pushbutton.setStyleSheet('#' + str(pushbutton.objectName()) + '{background: rgb(0, 170, 0);border-radius: 4px;}')
                self.cxnsignal.emit(servername, self.LabradDictionary[servername])
            else:
                label.setText('Connection Failed.')
                pushbutton.setStyleSheet('#' + str(pushbutton.objectName()) + '{background: rgb(161, 0, 0);border-radius: 4px;}')
        else:
            pass


    def connectAllServers(self):
        pass

    def disconnectLabRAD(self):
        pass

    def moveDefault(self):    
        self.move(10,170)
        
        
        