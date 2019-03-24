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
        self.MeasurementWindows = {
            'LabRAD': LabRADConnect.Window(self.reactor, None),
            'FourTerminalGateSweepWindow': FourTerminalGateSweep.Window(self.reactor, None)
        }
        
        
        self.pushButton_LabRADConnect.clicked.connect(lambda: self.openWindow('LabRAD'))
        self.pushButton_FourTerminalGateSweep.clicked.connect(lambda: self.openWindow('FourTerminalGateSweepWindow'))
        
        self.MeasurementWindows['LabRAD'].cxnsignal.connect(self.connect)
        self.MeasurementWindows['LabRAD'].discxnsignal.connect(self.disconnect)
        
        
        #Open by default the LabRAD Connect Module and Device Select
        self.openWindow('LabRAD')        
        
    def setupAdditionalUi(self):
        """Some UI elements would not set properly from Qt Designer. These initializations are done here."""
        pass
        
#----------------------------------------------------------------------------------------------#
            
    """ The following section connects actions related to default opening windows."""
    def connect(self, key, object):
        try:
            for name, window in self.MeasurementWindows.iteritems():
                if name != 'LabRAD': #Skip through labradconnect window
                    if str(key) in window.serversList:
                        window.connectServer(str(key), object)
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    def disconnect(self, key):
        try:
            for name, window in self.MeasurementWindows.iteritems():
                if key in window.serversList:
                    window.disconnectServer(key)
        except Exception as inst:
            print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

    def openWindow(self, key):
        self.MeasurementWindows[key].showNormal()
        self.MeasurementWindows[key].moveDefault()
        self.MeasurementWindows[key].raise_()
    
    def moveDefault(self):
        self.move(10,10)
        
    def closeEvent(self, e):
        try:
            self.MeasurementWindows['LabRAD'].close()
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
