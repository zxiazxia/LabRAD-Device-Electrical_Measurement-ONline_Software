import numpy as np
from itertools import product
import sys
import twisted
from PyQt4 import QtCore, QtGui, QtTest, uic
from twisted.internet.defer import inlineCallbacks, Deferred , returnValue
import pyqtgraph as pg
import exceptions
import time
import math
from DEMONSFormat import formatNum

'''
Set DAC Voltage
'''
@inlineCallbacks
def Set_DAC(DACADC_Device, Port, Voltage):
    try:
        yield DACADC_Device.set_voltage(Port, Voltage)
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Read ADC and set label
'''
@inlineCallbacks
def Read_ADC_SetLabel(DACADC_Device, Port, label):
    try:
        voltage = yield Read_ADC(DACADC_Device, Port)
        label.setText(formatNum(voltage, 6))
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Read ADC and return value
'''
@inlineCallbacks
def Read_ADC(DACADC_Device, Port):
    try:
        voltage = yield DACADC_Device.read_voltage(Port)
        returnValue(voltage)
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Ramp the DACADC without taking data, usually used to ramp to initial voltage.
'''
@inlineCallbacks
def Ramp_DACADC(DACADC_Device, Port, StartingVoltage, EndVoltage, Numberofsteps, Delay, c = None):
    try:
        Delay = int(Delay * 1000)
        yield DACADC_Device.ramp1(Port, float(StartingVoltage), float(EndVoltage), Numberofsteps, Delay)
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Buffer_Ramp of DACADC, take the DACADC device object, list of channel output and input along with the min and max, all should be list and number of elements should match.
buffer ramp function can be look up on DACADC server.
'''
@inlineCallbacks
def Buffer_Ramp_DACADC(DACADC_Device, ChannelOutput, ChannelInput, Min, Max, Numberofsteps, Delay):
    try:
        Delay = int(Delay * 1000)
        data = yield DACADC_Device.buffer_ramp(ChannelOutput,ChannelInput,Min,Max,Numberofsteps,Delay)
        returnValue(np.transpose(data))
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
Debugging version of buffer_ramp. Use it as if it is DAC bufferramp but it does not need to be yielded
'''
def Buffer_Ramp_Debug(Device, Output, Input, Min, Max, NoS, Delay):
    DebugData = []
    xpoints = np.linspace(Min, Max, NoS)
    for i in range(0, len(Input)):
        DebugData.append([])
        for j in xpoints:
            DebugData[i].append(i * j)
    return DebugData

'''
Generate Datavault Files, using datavault object, dataname(str), list of dependent variables and independent variables
return the imagenumber and directory number for updating GUI
'''
@inlineCallbacks
def CreateDataVaultFile(datavault, DataName, DependentVariablesList, IndependentVaraiblesList):
    file = yield datavault.new(DataName, DependentVariablesList, IndependentVaraiblesList)
    ImageNumber = file[1][0:5]
    session  = ''
    for folder in file[0][1:]:
        session = session + '\\' + folder
    ImageDir = r'\.datavault' + session
    returnValue([ImageNumber, ImageDir])

'''
After creating datavault file, attach parameters to the file
'''
@inlineCallbacks
def AddParameterToDataVault(datavault, parameterdict):
    try:
        for key, value in parameterdict.iteritems():
            yield datavault.add_parameter(key, parameterdict[key])
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno

'''
grab screenshot of the window and save the screenshot to sessionfolder
'''
def saveDataToSessionFolder(winId, SessionFolder, ScreenshotName):
    try:
        p = QtGui.QPixmap.grabWindow(winId)
        a = p.save(SessionFolder + '\\' + ScreenshotName + '.jpg','jpg')
        if not a:
            print "Error saving Scan data picture"
    except Exception as inst:
        print 'Error:', inst, ' on line: ', sys.exc_traceback.tb_lineno
