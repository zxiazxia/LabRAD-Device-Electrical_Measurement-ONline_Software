import sys
from PyQt4 import Qt, QtGui, QtCore, uic
import time 
import ctypes
myappid = 'YoungLab.DeviceElectricalMeasurementONlineSoftware'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

path = sys.path[0]
sys.path.append(path + r'\Resources')
sys.path.append(path + r'\Labrad Connect')
sys.path.append(path + r'\DataVaultBrowser')
sys.path.append(path + r'\Four Terminal Gate Sweep')

UI_path = path + r"\MainWindow.ui"
MainWindowUI, QtBaseClass = uic.loadUiType(UI_path)

#import all windows for gui
import LabRADConnect
import FourTerminalGateSweep

import exceptions

class MainWindow(QtGui.QMainWindow, MainWindowUI):
    """ The following section initializes, or defines the initialization of the GUI and 
    connecting to servers."""
    def __init__(self, reactor, parent=None):
        """ DEMONS GUI """
        
        super(MainWindow, self).__init__(parent)
        self.reactor = reactor
        self.setupUi(self)
        self.setupAdditionalUi()
        
        #Move to default position
        self.moveDefault()
        
        #Intialize all widgets. 
        self.LabRAD = LabRADConnect.Window(self.reactor, None)
        
        #Connects all drop down menu button
        self.pushButton_LabRADConnect.clicked.connect(self.openLabRADConnectWindow)
        
        # self.pushButton_FourTerminalGateSweep.clicked.connect(self.openFourTerminalGateSweep)
        
        # #Connect signals between modules
        # #When LabRAD Connect module emits all the local and remote labRAD connections, it goes to the device
        # #select module. This module selects appropriate devices for things. That is then emitted and is distributed
        # #among all the other modules
        # self.LabRAD.cxnLocal.connect(self.DeviceSelect.connectLabRAD)
        # self.LabRAD.cxnRemote.connect(self.DeviceSelect.connectRemoteLabRAD)
        # self.DeviceSelect.newDeviceInfo.connect(self.distributeDeviceInfo)
        
        # self.LabRAD.cxnDisconnected.connect(self.disconnectLabRADConnections)
        # self.LabRAD.newSessionFolder.connect(self.distributeSessionFolder)
        
        
        
        #Open by default the LabRAD Connect Module and Device Select
        self.openLabRADConnectWindow()
        
        
    def setupAdditionalUi(self):
        """Some UI elements would not set properly from Qt Designer. These initializations are done here."""
        pass
        
#----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to default opening windows."""
    
    def moveDefault(self):
        self.move(10,10)
    
        
    def openLabRADConnectWindow(self):
        self.LabRAD.showNormal()
        self.LabRAD.moveDefault()
        self.LabRAD.raise_()
        
#----------------------------------------------------------------------------------------------#
    """ The following section connects actions related to passing LabRAD connections."""
    
    def distributeDeviceInfo(self,dict):
        #Call connectLabRAD functions for relevant modules
        self.PlottersControl.connectLabRAD(dict)
        self.nSOTChar.connectLabRAD(dict)
        self.ScanControl.connectLabRAD(dict)
        self.TFChar.connectLabRAD(dict)
        self.Approach.connectLabRAD(dict)
        self.JPEControl.connectLabRAD(dict)
        self.Scripting.connectLabRAD(dict)
        self.GoToSetpoint.connectLabRAD(dict)
        self.FieldControl.connectLabRAD(dict)
        self.TempControl.connectLabRAD(dict)
        self.SampleCharacterizer.connectLabRAD(dict)
        self.AttocubeCoarseControl.connectLabRAD(dict)

    def disconnectLabRADConnections(self):
        self.DeviceSelect.disconnectLabRAD()
        self.PlottersControl.disconnectLabRAD()
        self.nSOTChar.disconnectLabRAD()
        self.ScanControl.disconnectLabRAD()
        self.TFChar.disconnectLabRAD()
        self.Approach.disconnectLabRAD()
        self.JPEControl.disconnectLabRAD()
        self.FieldControl.disconnectLabRAD()
        self.Scripting.disconnectLabRAD()
        self.TempControl.disconnectLabRAD()
        self.SampleCharacterizer.disconnectLabRAD()
        self.AttocubeCoarseControl.disconnectLabRAD()

    def distributeSessionFolder(self, folder):
        self.TFChar.setSessionFolder(folder)
        self.ScanControl.setSessionFolder(folder)
        self.nSOTChar.setSessionFolder(folder)
        self.SampleCharacterizer.setSessionFolder(folder)

    def updateDataVaultFolder(self):
        self.ScanControl.updateDataVaultDirectory()
        self.TFChar.updateDataVaultDirectory()
        self.nSOTChar.updateDataVaultDirectory()
        self.SampleCharacterizer.updateDataVaultDirectory()

#----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to setting the default layouts."""
        
    def setLayout1(self):
        self.moveDefault()
        self.hideAllWindows()
        self.openScanControlWindow()
        self.openApproachWindow()
        
            
    def hideAllWindows(self):
        self.ScanControl.hide()
        self.LabRAD.hide()
        self.nSOTChar.hide()
        self.PlottersControl.hide()
        self.TFChar.hide()
        self.Approach.hide()
        self.ApproachMonitor.hide()
        self.JPEControl.hide()
        self.PosCalibration.hide()
        self.GoToSetpoint.hide()
        self.QRreader.hide()
        self.TempControl.hide()
        self.SampleCharacterizer.hide()
        self.AttocubeCoarseControl.hide()
            
    def closeEvent(self, e):
        try:
            self.LabRAD.close()
        except Exception as inst:
            print inst
    
#----------------------------------------------------------------------------------------------#     
""" The following runs the GUI"""

if __name__=="__main__":
    import qt4reactor
    app = QtGui.QApplication(sys.argv)
    qt4reactor.install()
    from twisted.internet import reactor
    window = MainWindow(reactor)
    window.show()
    reactor.runReturn()
    sys.exit(app.exec_())
