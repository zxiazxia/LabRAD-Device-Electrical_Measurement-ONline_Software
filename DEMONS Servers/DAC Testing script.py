import labrad
import time

def clearreading():
    v= dac.read()
    while v != '':
        v= dac.read()
        print v

cxn = labrad.connect()
dac = cxn.dac_adc

dac.select_device()
print 'device selected'

clearreading()

print 'Reading All ADC'
for i in range(8):
    v = dac.read_voltage(i)
    print 'Channel Number', i, v

print 'Testing Overrange'
print 'Set Voltage'
print dac.set_voltage(0,-9.999)
time.sleep(0.1)
clearreading()

# print 'Buffer Ramp'
# v = dac.buffer_ramp([0], [0], [-9.999],[9.999],10,10)
# print v
# clearreading()
    
# print 'Buffe Ramp dis'
# v = dac.buffer_ramp_dis([0], [0], [-9.9999],[9.9999],50,1,5)
# print v
# clearreading()

print 'testing buffer ramp'
for i in range(4):
    print 'buffer ramping DAC channel',i
    v = dac.buffer_ramp([i], range(8), [0],[1],10,100000)
    print v
    
print 'testing buffer dis ramp'
for i in range(4):
    print 'buffer dis ramping DAC channel',i
    v = dac.buffer_ramp_dis([i], range(8), [1],[0],500,1,10)
    print v
    
print 'testing offset of ADC, only valid if all inputs are grounded'
for i in range(8):
    v = dac.read_voltage(i)
    print 'Channel Number', i, v
    
    
