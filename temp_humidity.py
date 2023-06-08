from machine import Pin
import utime as time
import dht
import array

#####################################################################
#                  Temperature and humidy Sensor
#                       Lesson 20 
#
#  Script: This script will read the temperature and humdity, and
#          then use a toggle button to change the display from Celsius
#          and Fahrenheit
#
#  Date: 06/05/2023
#
#  Enjoy, copy if you like
#####################################################################
togglePin=15
dataPin=16
sensorPin= Pin(dataPin,Pin.OUT,Pin.PULL_DOWN)
sensor=dht.DHT11(sensorPin)

# Setup Array structures to hold the values from the sensor

tempArry= [0,0]
tempDisp=[' ',' ']
tempDisp[0]='C'
tempDisp[1]='F'

#setup input toggle button.

toggleButton=Pin(togglePin,Pin.IN,Pin.PULL_UP)
      
# The button read is very fast, so we have to slow down the read. So to do this we need to checck
# the time and wait a few milliseconds
buttonMsWait=0

# trying to find a way to use interupts instead of sequential reads

buttonInterruptFlag=0
displayIdx=0

# Setup the interrupt handler so that it can toggle the index for
# the displays
#
def buttonInterruptHandler(pin):
    global buttonInterruptFlag, buttonMsWait,displayIdx
    if ((time.ticks_ms()-buttonMsWait) > 300):
        buttonMsWait=time.ticks_ms()
        buttonInterruptFlag=1
        displayIdx=not displayIdx
        
#declare the handler for the button interrupt.
        
toggleButton.irq(trigger=Pin.IRQ_RISING, handler=buttonInterruptHandler)

## notSure, but I had to do a priming read of the sensor, without this
## I kept getting a timeout error. I don't see it in other peoples solution
## So not sure why my environment is special. I tried getting the next
## version of Thonny and this is did not help. So I stuck with this
## as part of the solution

try:
    sensor.measure()
except:
    time.sleep(1)


####################################################################
# Start Main loop
####################################################################
try:

    print('My Sensor Data')
## while forever ## 
    while True:
        sensor.measure()
        tempReading=sensor.temperature()
        humReading=sensor.humidity()
        tempArry[0]=tempReading
        tempArry[1]=round(tempReading*(9/5)+32)
        print("\r" ,'temp= ', tempArry[displayIdx],chr(176)+tempDisp[displayIdx],'Humidity= ',humReading,'%',end=' ')
        time.sleep(1)     
##(END While)##
 
except KeyboardInterrupt:
    print("Going Down")
