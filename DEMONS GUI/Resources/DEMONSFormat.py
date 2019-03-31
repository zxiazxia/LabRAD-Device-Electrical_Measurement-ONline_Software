import numpy as np
from itertools import product
import sys
import twisted
from twisted.internet.defer import inlineCallbacks, Deferred , returnValue
import pyqtgraph as pg
import exceptions
import time

#---------------------------------------------------------------------------------------------------------#         
""" The following section describes how to read and write values to various lineEdits on the GUI."""

#Registry
def DACADC_Registry():
    return ['DA16_16_02']

'''
Update parameter, normally just text
Input: dictionary of parameters, key for the value to be changed, the lineEdit where the input comes from
Output: Change the parameter
'''
def UpdateLineEdit_String(parameterdict, key, lineEdit):
    parameterdict[key] = str(lineEdit[key].text())

'''
Update parameter with a bound
Input: dictionary of parameters, key for the value to be changed, the lineEdit where the input comes from, bound [lower, upper], datatype
Output: Change the parameter based on the validity of input value
'''
def UpdateLineEdit_Bound(dict, key, lineEdit, bound = None, datatype = float):
    dummystr=str(lineEdit[key].text())   #read the text
    dummyval=readNum(dummystr, None , False)
    if isinstance(dummyval, float):
        if bound == None:
            dict[key] = datatype(dummyval)
        elif (dummyval >= bound[0] and dummyval <= bound[1]):
            dict[key] = datatype(dummyval)
                
    lineEdit[key].setText(formatNum(dict[key], 6))

def UpdateLineEdit_NearestNumber(dict, key, lineEdit, Selection, datatype = float):
    dummystr=str(lineEdit[key].text())   #read the text
    dummyval=readNum(dummystr, None , False)
    if isinstance(dummyval, float):
        if bound == None:
            dict[key] = datatype(dummyval)
        elif (dummyval >= bound[0] and dummyval <= bound[1]):
            dict[key] = datatype(dummyval)
                
    lineEdit[key].setText(formatNum(dict[key], 6))

'''
Update Number of Step value, it is special because it need to switch between stepsize and number of step
Input: dictionary of parameters, key for the value to be changed, key for end, key for start, statuskey for status, the lineEdit where the input comes from, bound [lower, upper], datatype
Output: Change the parameter based on the validity of input value
'''
def UpdateLineEdit_NumberOfStep(dict, key, endkey, startkey, statuskey, lineEdit, bound = None, datatype = float):
    dummystr=str(lineEdit[key].text())   #read the text
    dummyval=readNum(dummystr, None , False)
    if isinstance(dummyval, datatype):
        if dict[statuskey] == "Numberofsteps":   #based on status, dummyval is deterimined and update the Numberof steps parameters
            dict[key] = int(round(dummyval)) #round here is necessary, without round it cannot do 1001 steps back and force
        elif dict[statuskey] == "StepSize":
            dict[key] = int(StepSizeToNumberOfSteps(dict[endkey], dict[startkey], float(dummyval)))
    if dict[statuskey] == "Numberofsteps":
        lineEdit[key].setText(formatNum(dict[key], 6))
    elif dict[statuskey] == "StepSize":
        lineEdit[key].setText(formatNum(NumberOfStepsToStepSize(dict[endkey], dict[startkey], float(dict[key])),6))

'''
Toggle between Number of Step and Step Size
Input: dictionary of parameters, key for the value to be changed, key for max, key for min, statuskey for status, label, the correct label unit like 'tesla per step', the lineEdit where the input comes from
Output: Change the parameter based on the validity of input value
'''
def Toggle_NumberOfSteps_StepSize(dict, key, endkey, startkey, statuskey, label, labelunit, lineEdit):
    if dict[statuskey] == "Numberofsteps":
        label.setText(labelunit)
        dict[statuskey] = "StepSize"
        lineEdit[key].setText(formatNum(NumberOfStepsToStepSize(dict[endkey], dict[startkey], float(dict[key])),6))
        UpdateLineEdit_NumberOfStep(dict, key, endkey, startkey, statuskey, lineEdit)
    else:
        label.setText('Number of Steps')
        dict[statuskey] = "Numberofsteps"
        lineEdit[key].setText(formatNum(dict[key],6))
        UpdateLineEdit_NumberOfStep(dict, key, endkey, startkey, statuskey, lineEdit)

'''
Simple StepSize to Number of Step Converters
'''
def StepSizeToNumberOfSteps(End, Start, SS):  #Conver stepsize to number of steps
    Numberofsteps=int(abs(End - Start)/float(SS)+1)
    return Numberofsteps

def NumberOfStepsToStepSize(Start, End, NoS):
    StepSize=float(abs(Start - End)/float(NoS - 1.0))
    return StepSize


'''
Takes devicelist, server name(str), device name(str), target which is the name of the device in list_devices() and the indicator pushbutton
Then save the selected device object to devicelist.
'''
@inlineCallbacks
def SelectDevice(devicelist, server, device, target, indicator, SequentialFunction = None):
    try:
        dummyserver = []
        if target != 'Offline' and server != False and target != '':#target can be blank when reconstruct the combobox
            try:
                devicelist[str(device)] = server
                yield devicelist[str(device)].select_device(str(target))
            except Exception as inst:
                print 'Connection to ' + device +  ' failed: ', inst, ' on line: ', sys.exc_traceback.tb_lineno
                devicelist[device] = False

        else:
            devicelist[device] = False
        RefreshIndicator(indicator, devicelist[device])
        if not SequentialFunction is None:
            SequentialFunction()
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

def RefreshIndicator(indicator, device):
    if device != False:
        setIndicator(indicator, 'rgb(0, 170, 0)')
    else:
        setIndicator(indicator, 'rgb(161, 0, 0)')

'''
change stylesheet of a pushbutton to certain color
'''
def setIndicator(indicator, color):
    indicator.setStyleSheet('#' + indicator.objectName() + '{background:' + color + ';border-radius: 4px;}')


'''
From server, query the list of device, post that on combobox and select the device to be offline.
It is useful for refreshing the list.
'''
@inlineCallbacks
def RedefineComboBox(combobox, server, devicelist, device, reconnect = True):
    try:
        if server != False:
            itemlist = yield QueryDeviceList(server)
        else:
            itemlist = []
        itemlist = ['Offline'] + itemlist
        if len(itemlist) != 1:
            defaultdevice = itemlist[1]
            defaultindex = 1
        else:
            defaultdevice = 'Offline'
            defaultindex = 0
        ReconstructComboBox(combobox, itemlist)
        if reconnect:
            combobox.setCurrentIndex(defaultindex)#This part change the index which should be connect to select device.
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

def ReconstructComboBox(combobox, list):
    combobox.clear()
    for name in list:
        combobox.addItem(name)

def RefreshButtonStatus(ButtonsCondition):
    for button in ButtonsCondition:
        button.setEnabled(ButtonsCondition[button])

'''
takes in server object and return a list of selectable device.
'''
@inlineCallbacks
def QueryDeviceList(server):
    devicelist = yield server.list_devices()
    namelist = []
    for combo in devicelist:
        namelist.append(combo[1])
    returnValue(namelist) 

'''
return True or False based on whether the pushbutton is green or red
'''
def JudgeIndicator(indicator): #based on stylesheet of indicator, return True or False
    color = 'rgb(0, 170, 0)'
    green = '#' + indicator.objectName() + '{background:' + color + ';border-radius: 4px;}'
    stylesheet = indicator.styleSheet()
    if stylesheet == green:
        return True
    else:
        return False

'''
Takes in parameter dictionary, key(str) of parameter, lineEdit that is related, device object for sending command, functionlist(list that guide to the correct function)
'''
@inlineCallbacks
def UpdateSetlineEdit(dict, key, lineEdit, device, function, bound = None, datatype = float):
    dummystr=str(lineEdit[key].text())   #read the text
    dummyval=readNum(dummystr, None , False)
    if isinstance(dummyval, float):
        if bound == None:
            dummyval = datatype(dummyval)
        elif (dummyval >= bound[0] and dummyval <= bound[1]):
            dummyval = datatype(dummyval)
    if device != False:
        try: 
            if function[0] == 'SR860':
                if function[1] == 'sensitivity':
                    yield device.sensitivity(dummyval)
                elif function[1] == 'timeconstant':
                    yield device.time_constant(dummyval)
                elif function[1] == 'frequency':
                    yield device.frequency(dummyval)
            flag = True
        except:
            flag = False
        if flag:
            dict[key] = dummyval
    else:
        dict[key] = dummyval
    lineEdit[key].setText(formatNum(dict[key], 6))

'''
Functions for each module to upload their datavault directory
'''
@inlineCallbacks
def updateDataVaultDirectory(window, directory):
    try:
        yield window.serversList['dv'].cd('')
        yield window.serversList['dv'].cd(directory)
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Clear Plots, can take a list/dict or single plot
'''
def ClearPlots(Plots):
    if isinstance(Plots, list):
        for plot in Plots:
            plot.clear()
    elif isinstance(Plots, dict):
        for name, plot in Plots.iteritems():
            plot.clear()
    else:
        Plots.clear()

'''
Input: PlotItem, Layout of Plot and Plot properties
'''
def Setup1DPlot(Plot, Layout, Title, yaxis, yunit, xaxis, xunit):
    Plot.setGeometry(QtCore.QRect(0, 0, 10, 10))
    Plot.setTitle( Title)
    Plot.setLabel('left', yaxis, units = yunit)
    Plot.setLabel('bottom', xaxis, units = xunit)
    Plot.showAxis('right', show = True)
    Plot.showAxis('top', show = True)
    Plot.setXRange(0,1) #Default Range
    Plot.setYRange(0,2) #Default Range
    Plot.enableAutoRange(enable = True)
    Layout.addWidget(Plot)

'''
Input: Data for Xaxis, Yaxis and plot object
'''
def Plot1DData(xaxis, yaxis, plot, color = 0.5):
    plot.plot(x = xaxis, y = yaxis, pen = color)

def Division(voltage, current, multiplier = 1):
    if current != 0.0:
        resistance = float(voltage / current) * multiplier
    else:
        resistance = float(voltage / 0.0000000001) * multiplier
    return resistance

'''
Attach Attach_Data to the front of data
'''
def AttachData_Front(data, attached_data):
    Data_Combined = np.insert(data, 0, attached_data, axis = 1)
    return Data_Combined

'''
Attach Attach_Data to the back of data
'''
def AttachData_Back(data, attached_data):
    column = data.shape[1]
    Data_Combined = np.insert(data, column, attached_data, axis = 1)
    return Data_Combined

def Attach_ResistanceConductance(data, VoltageIndex, CurrentIndex, multiplier = 1):
    Voltage, Current = data[:, VoltageIndex], data[:, CurrentIndex]
    Resistance = np.transpose(map(Division, Voltage, Current))
    Conductance = np.transpose(map(Division, Current, Voltage))
    Data_Attached1 = AttachData_Back(data, Resistance)
    Data_Attached = AttachData_Back(Data_Attached1, Conductance)
    
    return Data_Attached


'''
Multiply array with the input list
'''
def Multiply(Data, Multiplierlist):
    multiplymatrix = np.diag(Multiplierlist)
    MultipliedData = np.dot(Data, multiplymatrix)
    return MultipliedData

"""Asynchronous compatible sleep command. Sleeps for given time in seconds, but allows
other operations to be done elsewhere while paused."""
def SleepAsync(reactor, secs):
        d = Deferred()
        reactor.callLater(secs, d.callback, 'Sleeping')
        return d














'''
nSOT Scanner Session
'''
def formatNum(val, decimal_values = 2):
    if val != val:
        return 'nan'
        
    string = '%e'%val
    ind = string.index('e')
    num  = float(string[0:ind])
    exp = int(string[ind+1:])
    if exp < -6:
        diff = exp + 9
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'n'
    elif exp < -3:
        diff = exp + 6
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'u'
    elif exp < 0:
        diff = exp + 3
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'m'
    elif exp < 3:
        if val - int(val) == 0:
            val = int(val)
        else: 
            val = round(val,decimal_values)
        string = str(val)
    elif exp < 6:
        diff = exp - 3
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'k'
    elif exp < 9:
        diff = exp - 6
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'M'
    elif exp < 12:
        diff = exp - 9
        num = num * 10**diff
        if num - int(num) == 0:
            num = int(num)
        else: 
            num = round(num,decimal_values)
        string = str(num)+'G'
    return string
    
#By default, accepts no parent and will warn you for inputting a number without units. 
#Adding a parent is needed to have error thrown in a reasonable place and avoid recursion errors. 
#For entries that are expected to be of order unity the warningFlag can be set to False. 
def readNum(string, parent, warningFlag = True):
    try:
        val = float(string)
        
        if warningFlag and val != 0:
            warning = UnitWarning(parent, val)
            parent.setFocus()
            if warning.exec_():
                pass
            else:
                return 'Rejected Input'
    except:
        try:
            exp = string[-1]
            if exp == 'm':
                exp = 1e-3
            if exp == 'u':
                exp = 1e-6
            if exp == 'n':
                exp = 1e-9
            if exp == 'p':
                exp = 1e-12
            if exp == 'k':
                exp = 1e3
            if exp == 'M':
                exp = 1e6
            if exp == 'G':
                exp = 1e9
            try:
                val = float(string[0:-1])*exp
            except: 
                return 'Incorrect Format'
        except:
            return 'Empty Input'
    return val
        
#---------------------------------------------------------------------------------------------------------#         
""" The following section creates a generic warning if a numebr is input without a unit."""
        
from PyQt4 import QtGui, QtCore, uic
import sys

path = sys.path[0] + r"\Resources"
Ui_UnitWarning, QtBaseClass = uic.loadUiType(path + r"\UnitWarningWindow.ui")
        
class UnitWarning(QtGui.QDialog, Ui_UnitWarning):
    def __init__(self, parent, val):
        super(UnitWarning, self).__init__(parent)
        self.window = parent
        self.setupUi(self)
        
        self.label.setText(self.label.text() + formatNum(val) + '.')
        
        self.push_yes.clicked.connect(self.acceptEntry)
        self.push_no.clicked.connect(self.rejectEntry)
        
    def acceptEntry(self):
        self.accept()
        
    def rejectEntry(self):
        self.reject()
        
    def closeEvent(self, e):
        self.reject()
        
#---------------------------------------------------------------------------------------------------------#         
""" The following section has basic data processing methods."""
            
def processLineData(lineData, process):
    pixels = np.size(lineData)
    if process == 'Raw':
        return lineData 
    elif process == 'Subtract Average':
        x = np.linspace(0,pixels-1,pixels)
        fit = np.polyfit(x, lineData, 0)
        residuals  = lineData - fit[0]
        return residuals
    elif process == 'Subtract Linear Fit':
        x = np.linspace(0,pixels-1,pixels)
        fit = np.polyfit(x, lineData, 1)
        residuals  = lineData - fit[0]*x - fit[1]
        return residuals
    elif process == 'Subtract Parabolic Fit':
        x = np.linspace(0,pixels-1,pixels)
        fit = np.polyfit(x, lineData, 2)
        residuals  = lineData - fit[0]*x**2 - fit[1]*x - fit[2]
        return residuals
        
def processImageData(image, process):
    shape = np.shape(image)
    
    width = int(shape[0])
    length = int(shape[1])
    
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, length)
    X, Y = np.meshgrid(x, y, copy=False)
    
    X = X.flatten()
    Y = Y.flatten()
    
    if process == 'Raw':
        return image
        
    elif process == 'Subtract Image Average':
        avg = np.average(image)
        return image - avg
        
    elif process == 'Subtract Line Average':
        for i in range(0,length):
            image[:,i] = processLineData(image[:,i],'Subtract Average')
        return image

    elif process == 'Subtract Image Plane':
        A = np.array([X*0+1, X, Y]).T
        B = image.flatten('F')
        

        coeff, r, rank, s = np.linalg.lstsq(A, B)
        
        for i in xrange(length):
            for j in xrange(width):
                image[j][i] = image[j][i] - np.dot(coeff, [1, x[j], y[i]])
        return image
   
    elif process == 'Subtract Line Linear':
        for i in range(0,length):
            image[:,i] = processLineData(image[:,i],'Subtract Linear Fit')
        return image

    elif process == 'Subtract Image Quadratic':
        A = np.array([X*0+1, X, Y, X**2, Y**2, X*Y]).T
        B = image.flatten('F')

        coeff, r, rank, s = np.linalg.lstsq(A, B)

        for i in xrange(length):
            for j in xrange(width):
                image[j][i] = image[j][i] - np.dot(coeff, [1, x[j], y[i], x[j]**2, y[i]**2, x[j]*y[i]])    
        
        return image

    elif process == 'Subtract Line Quadratic':
        for i in range(0,length):
            image[:,i] = processLineData(image[:,i],'Subtract Parabolic Fit')
        return image
        
#---------------------------------------------------------------------------------------------------------#         
""" The following section creates a better image plotted, based off of pyqt's ImageView, to allow plotting of partial images."""
    
import pyqtgraph as pg

class ScanImageView(pg.ImageView):
    '''
    Extension of pyqtgraph's ImageView. This allows you to plot only part of a dataset. This works by specifying a "random filling" number which, 
    if found during plotting, is ignored from both the plotting and the histogram. 
    '''
    def __init__(self, parent=None, name="ImageView", view=None, imageItem=None, randFill = -0.1, *args):
        pg.ImageView.__init__(self, parent, name, view, imageItem, *args)
        #Rand fill is the number that gets thrown out of the dataset
        self.randFill = randFill

    def setImage(self, img, autoRange=True, autoLevels=True, levels=None, axes=None, xvals=None, pos=None, scale=None, transform=None, autoHistogramRange=True):
        r0 = np.where(np.all(img == self.randFill, axis = 0))[0]
        c0 = np.where(np.all(img == self.randFill, axis = 1))[0]
        tmp = np.delete(np.delete(img, r0, axis = 1), c0, axis = 0)
        #If nothing is left, don't plot anything
        if np.size(tmp) != 0:
            pg.ImageView.setImage(self, tmp, autoRange, autoLevels, levels, axes, xvals, pos, scale, transform, False)
        else:
            #Clear plot if nothing is being plotted
            pg.ImageView.clear(self)
            self.ui.histogram.plot.clear()
            
        #Autoscales histogram x axis, making sure we can always see the peaks of the histogram
        self.ui.histogram.vb.enableAutoRange(axis = pg.ViewBox.XAxis, enable = True)
        
        if autoHistogramRange:
            self.ui.histogram.vb.autoRange()
        
    def setRandFill(self, val):
        self.randFill = val
        
    def autoRange(self):
        #Redefine this function because in the pyqtgraph version, for some unknown reason, it also calls getProcessedImage, which causes bugs when nothing
        #is being plotted. 
        self.view.enableAutoRange()
        
    def keyPressEvent(self,ev):
        pass
        
    def keyReleaseEvent(self,ev):
        pass
    #Eventually also add the following from Avi's code so that if we're plotting point by point (instead of line by line) the histogram doesn't get populated
    '''
    def updateHist(self, autoLevel=False, autoRange=False):
        histTmp = self.tmp - self.randFill
        w = np.absolute(np.divide(histTmp, histTmp, out = np.zeros_like(histTmp), where = histTmp != 0))
        step = (int(np.ceil(w.shape[0] / 200)),
                    int(np.ceil(w.shape[1] / 200)))
        if np.isscalar(step):
            step = (step, step)
        stepW = w[::step[0], ::step[1]]
        stepW = stepW[np.isfinite(stepW)]
        h = self.mainImage.getHistogram(weights = stepW)
        if h[0] is None:
            return
        self.mainPlot.ui.histogram.plot.setData(*h)
        if autoLevel:
            mn = h[0][0]
            mx = h[0][-1]
            self.mainPlot.ui.histogram.region.setRegion([mn, mx])
    '''
        