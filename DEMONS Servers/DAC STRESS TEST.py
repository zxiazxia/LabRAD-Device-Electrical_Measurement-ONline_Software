import labrad
import time
import numpy as np
import random

def clearreading():
    v= dac.read()
    while v != '':
        v= dac.read()
        print v

def ThrowingTheDice(SET):
    list = np.zeros(len(SET))
    for i in range(len(list)):
        list[i] = float(random.randint(-50,50))/10.0
    return list
        
cxn = labrad.connect()
dac = cxn.dac_adc

DAC_Under_Test = [0,1,3]
ADC_Under_Test = [6,4,2,1,3]

DAC_NOW = np.zeros(len(DAC_Under_Test))
DAC_SET = np.zeros(len(DAC_Under_Test))
ADC_Reading = np.zeros(len(ADC_Under_Test))
TestNumber = 0

dac.select_device()
print 'device selected'

clearreading()

#This is a stress test testing the DAC under long term dis buffer ramp conditions.


while True:
    TestNumber +=1
    print 'This is not a drill but Number', TestNumber
    print 'Ramping DAC to each values ', DAC_SET
    # v = dac.buffer_ramp_dis(DAC_Under_Test, ADC_Under_Test, DAC_NOW,DAC_SET,5000,10,500)
    v = dac.buffer_ramp(DAC_Under_Test, ADC_Under_Test, DAC_NOW,DAC_SET,500,10)

    print "Ramp ", TestNumber, "Finished"
    for i in range(len(ADC_Under_Test)):
        ADC_Reading[i] = v[i][-1]
    print "ADC Readings are ", ADC_Reading
    DAC_NOW = DAC_SET
    DAC_SET = ThrowingTheDice(DAC_SET)
    
    
    
    
