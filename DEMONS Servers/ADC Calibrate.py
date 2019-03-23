import labrad
import time
import numpy as np
import operator

def clearreading():
    v= dac.read()
    while v != '':
        v= dac.read()
        print v

        
cxn = labrad.connect()
dac = cxn.dac_adc

DAC_As_Standard = 0
ADC_Under_Test = [0,1,2,3,4,5,6,7]
SET_Points=[-9,0,9]
ADC_Reading = []
ADC_Offset = np.zeros(len(ADC_Under_Test))
ADC_Gain = np.zeros(len(ADC_Under_Test))
ADC_Asym = np.zeros(len(ADC_Under_Test))

for i in range(len(SET_Points)):
    ADC_Reading.append([])


dac.select_device()
print 'device selected'

clearreading()

#This is TEST that test ADC reading at different point

for j in range(len(SET_Points)):
    print "Setting the DAC to ", SET_Points[j], ' V'
    dac.set_voltage(DAC_As_Standard ,SET_Points[j])
    for i in range(len(ADC_Under_Test)):
        raw_input("Plug in DAC to ADC Channel %i"%(ADC_Under_Test[i]+1))
        v = dac.read_voltage(ADC_Under_Test[i])
        ADC_Reading[j].append(v)
        print 'Reading ADC Channel ', ADC_Under_Test[i]+1,' : ', ADC_Reading[j][i]
        
ADC_Offest = ADC_Reading[1]
ADC_Gain = [x/18.0 for x in map(operator.sub , ADC_Reading[2], ADC_Reading[0])]
ADC_Asym = map(operator.sub, map(operator.add , ADC_Reading[2], ADC_Reading[0]),map(operator.add , ADC_Reading[1], ADC_Reading[1]))
    
print "OffSets   are: ", ADC_Offest
print "Gains     are: ", ADC_Gain
print "Asymmetry are: ", ADC_Asym

for i in range(5):
    print ''

print ADC_Reading
    
